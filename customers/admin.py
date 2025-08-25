from django.contrib import admin
from .models import Invoice, InvoiceItem, Address, Customer, CustomerInterest, Cart, CartItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    autocomplete_fields = ['book_format']

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'created_at', 'paid')
    list_filter = ('paid', 'created_at')
    search_fields = ('customer__user__username', 'id')
    inlines = [InvoiceItemInline]

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number', 'email', 'is_active', 'registration_date')
    list_filter = ('is_active', 'registration_date')
    search_fields = ('user__username', 'full_name', 'email')

class CustomerInterestAdmin(admin.ModelAdmin):
    list_display = ('customer',)
    search_fields = ('customer__user__username',)

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    autocomplete_fields = ['book_format']

class CartAdmin(admin.ModelAdmin):
    list_display = ('customer', 'created_at', 'updated_at', 'is_active', 'total_price')
    list_filter = ('is_active', 'created_at')
    search_fields = ('customer__user__username',)
    inlines = [CartItemInline]
    readonly_fields = ('total_price',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'book_format', 'quantity')
    search_fields = ('cart__customer__user__username', 'book_format__book__title')
    autocomplete_fields = ['cart', 'book_format']

# Register models in the admin
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(CustomerInterest, CustomerInterestAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
