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
from books.models import Book
from .serializers import CartItemSerializer
from .utils import calculate_shipping_cost  # فرض بر این است که این تابع در utils تعریف شده است
from .models import Cart, CartItem, Invoice,Cart, CartItem, Discount, Invoice, InvoiceItem, Address,Customer
import requests
# تنظیمات زرین پال
MERCHANT_ID = getattr(settings, 'ZARINPAL_MERCHANT_ID', None)
ZARINPAL_API_URL = 'ZARINPAL_API_URL'

# بررسی وجود تنظیمات زرین پال
if MERCHANT_ID is None:
    raise ValueError("Merchant ID for Zarinpal is not defined in settings")

# -------------------------------
# Mixins
# -------------------------------
class CustomerMixin:
    """
    برای دسترسی راحت به مشتری (customer) از روی request.user
    """
    @property
    def customer(self):
        return self.request.user.customer


# -------------------------------
# Cart API Views
# -------------------------------
class AddBookToCartView(CustomerMixin, APIView):
    """
    افزودن کتاب به سبد خرید
    """
    def post(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            return Response({"message": "مقدار تعداد نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, id=book_id)

        # بررسی موجودی کتاب
        if book.stock < quantity:
            return Response({
                "message": f"تعداد درخواستی از کتاب '{book.title}' بیشتر از موجودی است."
            }, status=status.HTTP_400_BAD_REQUEST)

        # دریافت یا ایجاد سبد خرید فعال مشتری
        cart, _ = Cart.objects.get_or_create(customer=self.customer, is_active=True)

        # دریافت یا ایجاد آیتم مربوط به کتاب در سبد خرید
        cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({
            "message": f"کتاب '{book.title}' از ناشر '{book.publisher.name}' به سبد خرید شما اضافه شد."
        }, status=status.HTTP_200_OK)


class RemoveBookFromCartView(CustomerMixin, APIView):
    """
    حذف (یا کاهش تعداد) کتاب از سبد خرید
    """
    def post(self, request, *args, **kwargs):
        book_id = request.data.get('book_id')
        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            return Response({"message": "مقدار تعداد نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        book = get_object_or_404(Book, id=book_id)
        cart = get_object_or_404(Cart, customer=self.customer, is_active=True)
        cart_item = CartItem.objects.filter(cart=cart, book=book).first()

        if not cart_item:
            return Response({
                "message": f"کتاب '{book.title}' در سبد خرید شما موجود نیست."
            }, status=status.HTTP_400_BAD_REQUEST)

        if cart_item.quantity < quantity:
            return Response({
                "message": f"تعداد درخواستی از کتاب '{book.title}' بیشتر از موجودی شما در سبد خرید است."
            }, status=status.HTTP_400_BAD_REQUEST)

        cart_item.quantity -= quantity
        if cart_item.quantity == 0:
            cart_item.delete()
        else:
            cart_item.save()

        return Response({
            "message": f"{quantity} کتاب '{book.title}' از سبد خرید شما حذف شد."
        }, status=status.HTTP_200_OK)


class ClearCartView(CustomerMixin, APIView):
    """
    خالی کردن سبد خرید
    """
    def post(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, customer=self.customer, is_active=True)
        cart.items.all().delete()
        return Response({"message": "سبد خرید شما با موفقیت خالی شد."}, status=status.HTTP_200_OK)


class CartDetailView(CustomerMixin, APIView):
    """
    مشاهده سبد خرید
    """
    def get(self, request, *args, **kwargs):
        cart = get_object_or_404(Cart, customer=self.customer, is_active=True)
        cart_items = cart.items.all()
        serializer = CartItemSerializer(cart_items, many=True)
        return Response({
            "cart_details": serializer.data,
            "total_price": str(cart.get_total_price()),
            "total_items": cart.get_total_items()
        }, status=status.HTTP_200_OK)


# -------------------------------
# Discount and Shipping Views (Non-API)
# -------------------------------
class ApplyDiscountView(CustomerMixin, View):
    """
    اعمال کد تخفیف بر روی سبد خرید
    """
    def post(self, request, discount_code, *args, **kwargs):
        cart = self.customer.cart
        discount = get_object_or_404(Discount, code=discount_code)
        try:
            cart.apply_discount(discount)
            messages.success(request, "Discount applied successfully.")
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('cart_detail')


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Address, Customer, Invoice
from .utils import calculate_shipping_cost

class CalculateShippingView(APIView):
    """
    محاسبه هزینه پست و ذخیره در فاکتور
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        customer = get_object_or_404(Customer, user=user)

        # دریافت سبد خرید کاربر
        cart = customer.cart

        if not cart.items.exists():
            return Response({"error": "Your cart is empty."}, status=400)

        total_weight = cart.get_total_weight()
        total_price = cart.get_total_price()

        # دریافت آدرس
        address_id = request.query_params.get("address_id")
        if not address_id:
            return Response({"error": "Address ID is required."}, status=400)

        address = get_object_or_404(Address, id=address_id, customer=customer)
        to_city_code = address.city_code

        # محاسبه هزینه ارسال
        api_key = "your_api_key_here"
        shipping_cost = calculate_shipping_cost(
            from_city_code=1001,
            to_city_code=to_city_code,
            cart_total=total_price,
            cart_weight=total_weight,
            api_key=api_key
        )

        # بررسی وجود فاکتور پرداخت‌نشده برای این کاربر
        invoice, created = Invoice.objects.get_or_create(
            customer=customer,
            paid=False,  # فاکتورهای پرداخت نشده را بررسی می‌کنیم
            defaults={"total_price": total_price, "shipping_cost": shipping_cost}
        )

        # اگر فاکتور قبلاً وجود داشت، فقط هزینه ارسال را به‌روزرسانی کنیم
        if not created:
            invoice.shipping_cost = shipping_cost
            invoice.total_price = total_price
            invoice.save()

        return Response({
            "shipping_cost": shipping_cost,
            "total_with_shipping": invoice.get_total_with_shipping()
        }, status=status.HTTP_200_OK)


# -------------------------------
# Payment and Invoice Views
# -------------------------------
class StartPaymentView(View):
    """
    شروع فرایند پرداخت
    """

    def get(self, request, *args, **kwargs):
        cart = self.customer.cart
        if not cart.items.exists():
            messages.error(request, "سبد خرید شما خالی است. لطفاً کالاهایی را به سبد خرید خود اضافه کنید.")
            return redirect('cart_detail')

        total_price = cart.get_total_price()
        total_weight = cart.get_total_weight()
        # دریافت هزینه ارسال با استفاده از تابع کمکی
        shipping_cost = calculate_shipping_cost(total_weight, getattr(self.customer, 'address', None))

        # ایجاد فاکتور
        invoice = Invoice.objects.create(
            customer=request.user,
            total_price=total_price,
            shipping_cost=shipping_cost,
            created_at=timezone.now(),
        )

        # ایجاد درخواست پرداخت
        data = {
            'MerchantID': MERCHANT_ID,
            'Amount': total_price + shipping_cost,  # جمع کل قیمت و هزینه ارسال
            'CallbackURL': request.build_absolute_uri('/payment/verify/')
        }

        # ارسال درخواست پرداخت به زرین‌پال
        response = requests.post(f"{ZARINPAL_API_URL}PaymentRequest.json", data=data)
        response_data = response.json()

        if response_data.get("Status") == 100:
            payment_url = f"https://www.zarinpal.com/pg/StartPay/{response_data.get('Authority')}"
            invoice.payment_url = payment_url
            invoice.save()
            return redirect(payment_url)
        else:
            messages.error(request, "مشکلی در ایجاد پرداخت وجود دارد. لطفاً دوباره تلاش کنید.")
            return redirect('cart_detail')


class VerifyPaymentView(View):
    """
    تایید پرداخت پس از بازگشت از درگاه زرین پال
    """

    def get(self, request, *args, **kwargs):
        authority = request.GET.get('Authority')
        status_param = request.GET.get('Status')

        if not authority or status_param != 'OK':
            messages.error(request, "پرداخت لغو شد یا اطلاعات نامعتبر است.")
            return redirect('cart_detail')

        # تایید پرداخت از زرین پال
        data = {
            'MerchantID': MERCHANT_ID,
            'Authority': authority,
            'Amount': int(request.GET.get('Amount', 0)),  # مبلغ پرداختی
        }

        response = requests.post(f"{ZARINPAL_API_URL}PaymentVerification.json", data=data)
        response_data = response.json()

        if response_data.get("Status") == 100:
            invoice = get_object_or_404(Invoice, payment_url__contains=authority)
            invoice.mark_as_paid()  # فرض می‌کنیم این متد وضعیت فاکتور را به پرداخت‌شده تغییر می‌دهد
            messages.success(request, "پرداخت شما با موفقیت انجام شد.")
            return redirect('order_complete')
        else:
            messages.error(request, "پرداخت ناموفق بود. لطفاً دوباره تلاش کنید.")
            return redirect('cart_detail')


class OrderCompleteView(View):
    """
    نمایش صفحه تکمیل خرید
    """

    def get(self, request, *args, **kwargs):
        return render(request, 'order_complete.html')


class InvoiceListView(View):
    """
    نمایش لیست فاکتورهای پرداخت‌شده (فقط برای کاربرانی با دسترسی ویژه)
    """
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect('login')
        invoices = Invoice.objects.filter(paid=True)
        return render(request, 'invoices_list.html', {'invoices': invoices})


# -------------------------------
# Invoice Item Update API View
# -------------------------------
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class UpdateInvoiceItemStatusView(APIView):
    """
    به‌روزرسانی وضعیت آیتم‌های فاکتور (مثلاً از طریق AJAX)
    """
    def post(self, request, item_id, *args, **kwargs):
        item = get_object_or_404(InvoiceItem, id=item_id)
        new_status = request.data.get('status')
        if new_status not in ['not_shipped', 'shipped', 'processing']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        item.status = new_status
        item.save()
        return Response({"message": f"Status updated to {new_status}"}, status=status.HTTP_200_OK)
