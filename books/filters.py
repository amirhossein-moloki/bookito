import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    # فیلتر برای ژانر
    genre = django_filters.CharFilter(field_name='genre__name', lookup_expr='icontains', label='Genre')

    # فیلتر برای زبان
    language = django_filters.CharFilter(field_name='language__name', lookup_expr='icontains', label='Language')

    # فیلتر برای مترجم
    translator = django_filters.CharFilter(field_name='translator__name', lookup_expr='icontains', label='Translator')

    # فیلتر برای نویسنده
    author = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains', label='Author')

    # فیلتر برای انتشارات
    publisher = django_filters.CharFilter(field_name='publisher__name', lookup_expr='icontains', label='Publisher')

    # فیلتر برای قیمت
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min Price')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max Price')

    # فیلتر برای تاریخ انتشار
    publication_date_min = django_filters.DateFilter(field_name='publication_date', lookup_expr='gte', label='Min Publication Date')
    publication_date_max = django_filters.DateFilter(field_name='publication_date', lookup_expr='lte', label='Max Publication Date')

    class Meta:
        model = Book
        fields = ['genre', 'language', 'translator', 'author', 'publisher', 'price_min', 'price_max', 'publication_date_min', 'publication_date_max']
