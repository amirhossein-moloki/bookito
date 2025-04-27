# filters.py
import django_filters
from .models import Book, Translator

class BookFilter(django_filters.FilterSet):
    # فیلتر برای ژانر
    genre = django_filters.CharFilter(field_name='genres__name', lookup_expr='icontains', label='Genre')

    # فیلتر برای زبان
    language = django_filters.CharFilter(field_name='language__name', lookup_expr='icontains', label='Language')

    # فیلتر برای مترجم (بر اساس نام کامل، نام کوچک یا نام خانوادگی)
    translator_name = django_filters.CharFilter(method='filter_translator_by_full_name', label='Translator Full Name')
    translator_first_name = django_filters.CharFilter(field_name='translators__first_name', lookup_expr='icontains', label='Translator First Name')
    translator_last_name = django_filters.CharFilter(field_name='translators__last_name', lookup_expr='icontains', label='Translator Last Name')

    # فیلتر برای نویسنده (بر اساس نام کامل، نام کوچک یا نام خانوادگی)
    author_name = django_filters.CharFilter(method='filter_author_by_full_name', label='Author Full Name')
    first_name = django_filters.CharFilter(field_name='authors__first_name', lookup_expr='icontains', label='Author First Name')
    last_name = django_filters.CharFilter(field_name='authors__last_name', lookup_expr='icontains', label='Author Last Name')

    # فیلتر برای ناشر
    publisher = django_filters.CharFilter(field_name='publisher__name', lookup_expr='icontains', label='Publisher')

    # فیلتر برای قیمت
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Min Price')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Max Price')

    # فیلتر برای تاریخ انتشار
    publication_date_min = django_filters.DateFilter(field_name='publication_date', lookup_expr='gte', label='Min Publication Date')
    publication_date_max = django_filters.DateFilter(field_name='publication_date', lookup_expr='lte', label='Max Publication Date')

    # فیلترهای اضافی
    discount_min = django_filters.NumberFilter(field_name='discount', lookup_expr='gte', label='Min Discount')
    discount_max = django_filters.NumberFilter(field_name='discount', lookup_expr='lte', label='Max Discount')
    rating_min = django_filters.NumberFilter(field_name='rating', lookup_expr='gte', label='Min Rating')
    rating_max = django_filters.NumberFilter(field_name='rating', lookup_expr='lte', label='Max Rating')
    in_stock = django_filters.BooleanFilter(field_name='stock', lookup_expr='gt', method='filter_in_stock', label='In Stock')

    class Meta:
        model = Book
        fields = [
            'genre', 'language', 'translator_name', 'translator_first_name', 'translator_last_name',
            'author_name', 'first_name', 'last_name', 'publisher',
            'price_min', 'price_max', 'publication_date_min', 'publication_date_max',
            'discount_min', 'discount_max', 'rating_min', 'rating_max', 'in_stock'
        ]

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__gt=0)
        return queryset

    def filter_translator_by_full_name(self, queryset, name, value):
        """
        این متد نام و نام خانوادگی مترجم را از یک پارامتر ورودی می‌گیرد،
        آن را تقسیم می‌کند و سپس جستجو بر اساس هر دو فیلد انجام می‌دهد.
        """
        if value:
            # تقسیم نام و نام خانوادگی
            names = value.split()
            if len(names) == 2:
                first_name, last_name = names
                return queryset.filter(first_name__icontains=first_name, last_name__icontains=last_name)
            else:
                return queryset  # اگر تعداد بخش‌ها صحیح نبود، هیچ فیلتر خاصی اعمال نکنیم
        return queryset

    def filter_author_by_full_name(self, queryset, name, value):
        """
        این متد نام و نام خانوادگی نویسنده را از یک پارامتر ورودی می‌گیرد،
        آن را تقسیم می‌کند و سپس جستجو بر اساس هر دو فیلد انجام می‌دهد.
        """
        if value:
            # تقسیم نام و نام خانوادگی
            names = value.split()
            if len(names) == 2:
                first_name, last_name = names
                return queryset.filter(authors__first_name__icontains=first_name, authors__last_name__icontains=last_name)
            else:
                return queryset  # اگر تعداد بخش‌ها صحیح نبود، هیچ فیلتر خاصی اعمال نکنیم
        return queryset
