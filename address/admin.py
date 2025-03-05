from django.contrib import admin
from .models import Address
class AddressAdmin(admin.ModelAdmin):
    list_display = ('province', 'city', 'street_address', 'house_number', 'postal_code')
    search_fields = ('province', 'city', 'street_address', 'house_number', 'postal_code')

admin.site.register(Address, AddressAdmin)