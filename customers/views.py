from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from books.models import Book, BookFormat
from .serializers import CartItemSerializer
from .utils import calculate_shipping_cost
from .models import Cart, CartItem, Invoice, Discount, InvoiceItem, Address, Customer
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

        if book_format.stock < quantity:
            return Response({"message": f"Not enough stock for {book_format.book.title} ({book_format.format_name})."}, status=status.HTTP_400_BAD_REQUEST)

        cart, _ = Cart.objects.get_or_create(customer=self.customer, defaults={'is_active': True})
        cart_item, created = CartItem.objects.get_or_create(cart=cart, book_format=book_format, defaults={'quantity': 0})

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
        cart.items.all().delete()
        return Response({"message": "Cart cleared successfully."}, status=status.HTTP_200_OK)

class CartDetailView(CustomerMixin, APIView):
    def get(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(customer=self.customer, defaults={'is_active': True})
        serializer = CartItemSerializer(cart.items.all(), many=True)
        return Response({
            "cart_details": serializer.data,
            "total_price": cart.get_total_price(),
            "total_items": cart.get_total_items()
        }, status=status.HTTP_200_OK)

class ApplyDiscountView(CustomerMixin, View):
    def post(self, request, discount_code, *args, **kwargs):
        # Implementation depends on how Discount model and cart logic work
        pass

class CalculateShippingView(APIView):
    def get(self, request, *args, **kwargs):
        # Implementation depends on Address model and shipping logic
        pass

class StartPaymentView(View):
    def get(self, request, *args, **kwargs):
        # Implementation depends on Zarinpal integration
        pass

class VerifyPaymentView(View):
    def get(self, request, *args, **kwargs):
        # Implementation depends on Zarinpal integration
        pass

class OrderCompleteView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'order_complete.html')

class InvoiceListView(View):
    def get(self, request, *args, **kwargs):
        # Implementation depends on user permissions
        pass

class UpdateInvoiceItemStatusView(APIView):
    def post(self, request, item_id, *args, **kwargs):
        # Implementation depends on InvoiceItem status logic
        pass
