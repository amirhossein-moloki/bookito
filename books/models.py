from django.db import models
from authors.models import Author
from publishers.models import Publisher
from translators.models import Translator
from genres.models import Genre
from Language.models import Language

class Book(models.Model):
    title = models.CharField(max_length=255)  # عنوان کتاب
    authors = models.ManyToManyField(Author, blank=True)  # ارتباط چند به چند با نویسنده
    translators = models.ManyToManyField(Translator, blank=True)  # ارتباط چند به چند با مترجم
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)  # ارتباط با ناشر
    publication_date = models.DateField(null=True, blank=True)  # تاریخ انتشار
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True)  # شماره استاندارد بین‌المللی کتاب
    price = models.DecimalField(max_digits=15, decimal_places=0)
    summary = models.TextField(null=True, blank=True)  # خلاصه کتاب
    genres = models.ManyToManyField(Genre, blank=True)  # ارتباط چند به چند با ژانر کتاب
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)  # ارتباط با زبان کتاب
    page_count = models.IntegerField(null=True, blank=True)  # تعداد صفحات کتاب
    cover_type = models.CharField(max_length=255, null=True, blank=True)
    cover_image = models.ImageField(upload_to='books/covers/', null=True, blank=True)  # تصویر جلد کتاب
    stock = models.IntegerField(default=0)  # تعداد موجودی کتاب
    sold_count = models.IntegerField(default=0)  # تعداد فروخته‌شده
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # امتیاز کتاب (اختیاری)
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # درصد تخفیف (اختیاری)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # وزن کتاب به کیلوگرم

    def __str__(self):
        return self.title

    @classmethod
    def get_books_by_genre(cls, genre_name):
        return cls.objects.filter(genres__name=genre_name)

    @classmethod
    def get_books_by_author(cls, author_name):
        return cls.objects.filter(authors__name=author_name)

    @classmethod
    def get_books_by_translator(cls, translator_name):
        return cls.objects.filter(translators__name=translator_name)

    @classmethod
    def get_books_by_publisher(cls, publisher_name):
        return cls.objects.filter(publisher__name=publisher_name)

    @classmethod
    def get_books_by_price_range(cls, min_price, max_price):
        return cls.objects.filter(price__gte=min_price, price__lte=max_price)

    @classmethod
    def get_books_by_publication_date_range(cls, start_date, end_date):
        return cls.objects.filter(publication_date__gte=start_date, publication_date__lte=end_date)

    @classmethod
    def get_books_by_rating(cls, min_rating, max_rating):
        return cls.objects.filter(rating__gte=min_rating, rating__lte=max_rating)

    @classmethod
    def get_books_by_discount(cls, min_discount, max_discount):
        return cls.objects.filter(discount__gte=min_discount, discount__lte=max_discount)

    @classmethod
    def get_books_in_stock(cls):
        return cls.objects.filter(stock__gt=0)



class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  # نام دسته‌بندی
    books = models.ManyToManyField('Book', related_name='categories', blank=True)  # ارتباط چند به چند با کتاب‌ها

    def __str__(self):
        return self.name
