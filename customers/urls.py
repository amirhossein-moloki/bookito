from django.urls import path
from .views import (
    AddToCartView, RemoveFromCartView, ClearCartView, CartDetailView,
    ApplyDiscountView, CalculateShippingView, StartPaymentView, VerifyPaymentView,
    OrderCompleteView, InvoiceListView
)

app_name = 'customers'

urlpatterns = [
    # Cart API URLs
    path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
    path('cart/remove/', RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('cart/clear/', ClearCartView.as_view(), name='clear_cart'),
    path('cart/detail/', CartDetailView.as_view(), name='cart_detail'),

    # Discount and Shipping
    path('cart/discount/<str:discount_code>/', ApplyDiscountView.as_view(), name='apply_discount'),
    path('cart/shipping/', CalculateShippingView.as_view(), name='calculate_shipping'),

    # Payment
    path('payment/start/', StartPaymentView.as_view(), name='start_payment'),
    path('payment/verify/', VerifyPaymentView.as_view(), name='verify_payment'),

    # Order
    path('order/complete/', OrderCompleteView.as_view(), name='order_complete'),

    # Invoice
    path('invoice/list/', InvoiceListView.as_view(), name='invoice_list'),
]
