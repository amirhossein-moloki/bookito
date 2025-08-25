from django.db import models
from django.conf import settings
from authors.models import Author
from publishers.models import Publisher
from translators.models import Translator
from genres.models import Genre
from Language.models import Language

class Book(models.Model):
    # Core, conceptual fields remain
    title = models.CharField(max_length=255)  # عنوان کتاب
    authors = models.ManyToManyField(Author, blank=True)  # ارتباط چند به چند با نویسنده
    translators = models.ManyToManyField(Translator, blank=True)  # ارتباط چند به چند با مترجم
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)  # ارتباط با ناشر
    publication_date = models.DateField(null=True, blank=True)  # تاریخ انتشار
    summary = models.TextField(null=True, blank=True)  # خلاصه کتاب
    genres = models.ManyToManyField(Genre, blank=True)  # ارتباط چند به چند با ژانر کتاب
    language = models.ForeignKey(Language, on_delete=models.SET_NULL, null=True, blank=True)  # ارتباط با زبان کتاب

    # This field is not format-specific
    sold_count = models.IntegerField(default=0)  # تعداد فروخته‌شد

    def __str__(self):
        return self.title

    # --- Obsolete classmethods removed ---
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
    def get_books_by_publication_date_range(cls, start_date, end_date):
        return cls.objects.filter(publication_date__gte=start_date, publication_date__lte=end_date)


class BookFormat(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='formats', verbose_name="کتاب")
    format_name = models.CharField(max_length=100, verbose_name="نوع فرمت")  # e.g., Hardcover, Paperback, Ebook

    price = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="قیمت")
    isbn = models.CharField(max_length=13, unique=True, null=True, blank=True, verbose_name="شابک")
    page_count = models.IntegerField(null=True, blank=True, verbose_name="تعداد صفحات")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="وزن (کیلوگرم)")
    cover_image = models.ImageField(upload_to='books/covers/', null=True, blank=True, verbose_name="تصویر جلد")
    stock = models.IntegerField(default=0, verbose_name="موجودی")
    discount = models.DecimalField(max_digits=5, decimal_places=0, null=True, blank=True, verbose_name="درصد تخفیف")

    class Meta:
        verbose_name = "فرمت کتاب"
        verbose_name_plural = "فرمت‌های کتاب"
        unique_together = ('book', 'format_name')

    def __str__(self):
        return f"{self.book.title} ({self.format_name})"


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)  # نام دسته‌بندی
    books = models.ManyToManyField('Book', related_name='categories', blank=True)  # ارتباط چند به چند با کتاب‌ها

    def __str__(self):
        return self.name


class StockNotification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stock_notifications')
    book_format = models.ForeignKey(BookFormat, on_delete=models.CASCADE, related_name='stock_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
    notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Stock Notification"
        verbose_name_plural = "Stock Notifications"
        unique_together = ('user', 'book_format', 'notified')

    def __str__(self):
        return f"Notification for {self.user.username} on {self.book_format.book.title}"
