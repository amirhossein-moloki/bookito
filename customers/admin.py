from django.contrib import admin
from .models import Invoice, InvoiceItem, Address, Customer, CustomerInterest, Cart, CartItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'created_at', 'paid')
    list_filter = ('paid', 'created_at')
    search_fields = ('customer__username', 'id')
    inlines = [InvoiceItemInline]

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'email', 'is_active', 'registration_date')
    list_filter = ('is_active', 'registration_date')
    search_fields = ('user__username', 'full_name', 'email')

class CustomerInterestAdmin(admin.ModelAdmin):
    list_display = ('customer', 'genre_interest', 'author_interest', 'translator_interest', 'publisher_interest')
    search_fields = ('customer__username',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'created_at', 'updated_at', 'is_active', 'get_total_price')
    list_filter = ('is_active', 'created_at')
    inlines = [CartItemInline]

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'book', 'quantity')
    search_fields = ('cart__customer__username', 'book__title')

# ثبت مدل‌ها در صفحه ادمین
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerInterest, CustomerInterestAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
