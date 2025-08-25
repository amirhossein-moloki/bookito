from django.contrib import admin
from .models import Discount, DiscountUsage

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('code', 'type', 'value', 'start_date', 'end_date', 'is_active', 'times_used', 'max_uses')
    search_fields = ('code',)
    list_filter = ('is_active', 'type', 'start_date', 'end_date')
    ordering = ('-start_date',)
    filter_horizontal = ('applicable_books', 'applicable_formats', 'applicable_genres', 'applicable_authors')
    fieldsets = (
        (None, {
            'fields': ('code', 'type', 'value', 'is_active')
        }),
        ('Date Range', {
            'fields': ('start_date', 'end_date')
        }),
        ('Usage Limits', {
            'fields': ('max_uses', 'max_uses_per_customer', 'times_used')
        }),
        ('Conditions', {
            'fields': ('min_purchase_amount',)
        }),
        ('Applicability (leave blank for global)', {
            'classes': ('collapse',),
            'fields': ('applicable_books', 'applicable_formats', 'applicable_genres', 'applicable_authors'),
        }),
    )
    readonly_fields = ('times_used',)

class DiscountUsageAdmin(admin.ModelAdmin):
    list_display = ('discount', 'user', 'use_count')
    search_fields = ('discount__code', 'user__username')
    autocomplete_fields = ['discount', 'user']

# Register models in the admin
admin.site.register(Discount, DiscountAdmin)
admin.site.register(DiscountUsage, DiscountUsageAdmin)
