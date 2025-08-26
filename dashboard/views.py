import json
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from customers.models import Invoice, InvoiceItem, Customer
from books.models import Book

@staff_member_required
def dashboard_view(request):
    # 1. Sales Overview
    sales_data = Invoice.objects.filter(paid=True).extra(
        select={'day': "DATE(created_at)"}
    ).values('day').annotate(total_sales=Sum('total_price')).order_by('day')

    sales_labels = [str(s['day']) for s in sales_data]
    sales_values = [float(s['total_sales']) for s in sales_data]

    # 2. Best-Selling Books
    best_selling_books_data = InvoiceItem.objects.values('book_format__book__title').annotate(
        total_sold=Sum('quantity')
    ).order_by('-total_sold')[:10]

    best_selling_books_labels = [item['book_format__book__title'] for item in best_selling_books_data]
    best_selling_books_values = [item['total_sold'] for item in best_selling_books_data]

    # 3. New Customers
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_customers_data = Customer.objects.filter(registration_date__gte=thirty_days_ago).extra(
        select={'day': "DATE(registration_date)"}
    ).values('day').annotate(count=Count('id')).order_by('day')

    new_customers_labels = [str(c['day']) for c in new_customers_data]
    new_customers_values = [c['count'] for c in new_customers_data]

    context = {
        'sales_labels': json.dumps(sales_labels),
        'sales_values': json.dumps(sales_values),
        'best_selling_books_labels': json.dumps(best_selling_books_labels),
        'best_selling_books_values': json.dumps(best_selling_books_values),
        'new_customers_labels': json.dumps(new_customers_labels),
        'new_customers_values': json.dumps(new_customers_values),
    }

    return render(request, 'dashboard/dashboard.html', context)
