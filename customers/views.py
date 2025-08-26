from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, serializers
from books.models import Book, BookFormat
from .serializers import CartItemSerializer, WishlistSerializer
from .utils import calculate_shipping_cost
from .models import Cart, CartItem, Invoice, Discount, InvoiceItem, Address, Customer, Wishlist
import requests

MERCHANT_ID = getattr(settings, 'ZARINPAL_MERCHANT_ID', None)
ZARINPAL_API_URL = 'ZARINPAL_API_URL'

if MERCHANT_ID is None:
    raise ValueError("Merchant ID for Zarinpal is not defined in settings")

class CustomerMixin:
    @property
    def customer(self):
        return self.request.user.customer

class AddToCartView(CustomerMixin, APIView):
    def post(self, request, *args, **kwargs):
        book_format_id = request.data.get('book_format_id')
        if not book_format_id:
            return Response({"message": "book_format_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity = int(request.data.get('quantity', 1))
            if quantity <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response({"message": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        book_format = get_object_or_404(BookFormat, id=book_format_id)

        # Check stock for in-stock items
        if book_format.status == BookFormat.Status.IN_STOCK:
            if book_format.stock < quantity:
                return Response({"message": f"Not enough stock for {book_format.book.title} ({book_format.format_name})."}, status=status.HTTP_400_BAD_REQUEST)
        # Prevent adding out-of-stock items
        elif book_format.status == BookFormat.Status.OUT_OF_STOCK:
            return Response({"message": f"{book_format.book.title} ({book_format.format_name}) is out of stock."}, status=status.HTTP_400_BAD_REQUEST)
        # Pre-order items can be added regardless of stock
        elif book_format.status == BookFormat.Status.PRE_ORDER:
            pass  # No stock check needed for pre-orders

        cart, _ = Cart.objects.get_or_create(customer=self.customer, defaults={'is_active': True})
        cart_item, created = CartItem.objects.get_or_create(cart=cart, book_format=book_format, defaults={'quantity': 0})

        # Further stock check for in-stock items already in cart
        if book_format.status == BookFormat.Status.IN_STOCK:
            if book_format.stock < cart_item.quantity + quantity:
                return Response({"message": f"Total requested quantity exceeds stock for {book_format.book.title} ({book_format.format_name})."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity += quantity
        cart_item.save()

        return Response({"message": f"Added {book_format.book.title} ({book_format.format_name}) to your cart."}, status=status.HTTP_200_OK)

class RemoveFromCartView(CustomerMixin, APIView):
    def post(self, request, *args, **kwargs):
        book_format_id = request.data.get('book_format_id')
        if not book_format_id:
            return Response({"message": "book_format_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quantity_to_remove = int(request.data.get('quantity', 1))
            if quantity_to_remove <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response({"message": "Invalid quantity."}, status=status.HTTP_400_BAD_REQUEST)

        cart = get_object_or_404(Cart, customer=self.customer, is_active=True)
        cart_item = get_object_or_404(CartItem, cart=cart, book_format_id=book_format_id)

        if cart_item.quantity < quantity_to_remove:
            return Response({"message": "Cannot remove more items than are in the cart."}, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity -= quantity_to_remove
        if cart_item.quantity <= 0:
            cart_item.delete()
            message = f"Removed {cart_item.book_format.book.title} ({cart_item.book_format.format_name}) from your cart."
        else:
            cart_item.save()
            message = f"Reduced quantity for {cart_item.book_format.book.title} ({cart_item.book_format.format_name})."

        return Response({"message": message}, status=status.HTTP_200_OK)

class ClearCartView(CustomerMixin, APIView):
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, customer=self.customer, is_active=True)
        cart.clear()
        return Response({"message": "Cart cleared successfully."}, status=status.HTTP_200_OK)

class CartDetailView(CustomerMixin, APIView):
    def get(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(customer=self.customer)
        # Recalculate discount amount in case cart items changed
        discount_amount = cart.get_discount_amount(user_for_check=request.user)

        # Note: The serializer for CartItem might need to be updated
        # if it doesn't already show all necessary details.
        cart_items_serializer = CartItemSerializer(cart.items.all(), many=True)

        return Response({
            "cart_details": cart_items_serializer.data,
            "total_price_without_discount": cart.total_price_without_discount,
            "discount_amount": discount_amount,
            "total_price_with_discount": cart.total_price,
            "total_items": cart.get_total_items()
        }, status=status.HTTP_200_OK)

class ApplyDiscountView(CustomerMixin, APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('discount_code')
        if not code:
            # If code is empty, remove the discount
            cart, _ = Cart.objects.get_or_create(customer=self.customer)
            cart.discount = None
            cart.save()
            return Response({"message": "Discount removed."}, status=status.HTTP_200_OK)

        try:
            discount = Discount.objects.get(code__iexact=code)
        except Discount.DoesNotExist:
            return Response({"error": "Invalid discount code."}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(customer=self.customer)
        cart.discount = discount # Temporarily assign to check validity

        calculated_amount = cart.get_discount_amount(user_for_check=request.user)

        if calculated_amount > 0:
            cart.save() # Persist the discount assignment
            return Response({
                "message": "Discount applied successfully.",
                "discount_amount": str(calculated_amount),
                "new_total_price": str(cart.total_price)
            }, status=status.HTTP_200_OK)
        else:
            cart.discount = None # Remove invalid discount
            cart.save()
            return Response({"error": "This discount code is not valid for your cart, has expired, or usage limit reached."}, status=status.HTTP_400_BAD_REQUEST)

# ... other views ...
class CalculateShippingView(APIView):
    def get(self, request, *args, **kwargs): pass
class StartPaymentView(View):
    def get(self, request, *args, **kwargs): pass
class VerifyPaymentView(CustomerMixin, View):
    """
    Verifies the payment with the payment gateway and finalizes the order.
    This view contains mocked logic for payment verification.
    """
    def get(self, request, *args, **kwargs):
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')

        # In a real scenario, you would verify the authority and status
        # with the payment gateway. Here, we'll simulate a success.
        is_payment_successful = status_param == 'OK'

        if is_payment_successful:
            # Payment is successful
            customer = self.customer
            try:
                cart = Cart.objects.get(customer=customer)
            except Cart.DoesNotExist:
                # This case should ideally not happen if a user is at payment verification
                messages.error(request, "سبد خرید شما یافت نشد.")
                return redirect('cart_detail') # Redirect to a real cart detail URL

            # Create Invoice from Cart
            invoice = Invoice.objects.create(
                customer=customer.user,
                total_price=cart.total_price,
                shipping_cost=0,  # Or calculate it
                paid=True
            )

            for item in cart.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    book_format=item.book_format,
                    quantity=item.quantity,
                    price=item.book_format.price,
                    is_preorder=(item.book_format.status == BookFormat.Status.PRE_ORDER)
                )
                #
                # Decrease stock for non-pre-order items
                if item.book_format.status == BookFormat.Status.IN_STOCK:
                    item.book_format.stock -= item.quantity
                    item.book_format.save(update_fields=['stock'])


            # Record discount usage if a discount was applied to the cart
            if cart.discount:
                cart.discount.record_usage(customer.user)

            # Here you would typically finalize the invoice, create shipping orders, etc.
            # For now, we just clear the cart.
            cart.clear()

            messages.success(request, "پرداخت شما با موفقیت انجام شد و سفارش شما ثبت گردید.")
            return redirect('order_complete') # Redirect to a real order completion URL
        else:
            messages.error(request, "پرداخت ناموفق بود یا توسط شما لغو شد.")
            return redirect('cart_detail') # Redirect to a real cart detail URL
class OrderCompleteView(View):
    def get(self, request, *args, **kwargs): pass
from .serializers import InvoiceSerializer

class InvoiceListView(generics.ListAPIView):
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Invoice.objects.filter(customer=self.request.user)
class UpdateInvoiceItemStatusView(APIView):
    def post(self, request, item_id, *args, **kwargs): pass


class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all the wishlist items
        for the currently authenticated user.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        return Wishlist.objects.filter(customer=customer)

    def perform_create(self, serializer):
        """
        Create a new wishlist item.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        book_format_id = self.request.data.get('book_format_id')
        book_format = get_object_or_404(BookFormat, id=book_format_id)

        # Check if the item already exists in the wishlist
        if Wishlist.objects.filter(customer=customer, book_format=book_format).exists():
            raise serializers.ValidationError({'detail': 'This item is already in your wishlist.'})

        serializer.save(customer=customer, book_format=book_format)


class WishlistDestroyView(generics.DestroyAPIView):
    """
    View to remove an item from the wishlist.
    """
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Ensure that users can only delete their own wishlist items.
        """
        customer = get_object_or_404(Customer, user=self.request.user)
        return Wishlist.objects.filter(customer=customer)
