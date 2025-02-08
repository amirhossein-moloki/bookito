from django.db import models
from accounts.models import User
from books.models import Book  # وارد کردن مدل Book از اپلیکیشن library
from discounts.models import Discount
from authors.models import Author
from publishers.models import Publisher
from translators.models import Translator
from genres.models import Genre
from Language.models import Language


class Invoice(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # هزینه پست
    created_at = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.id} for {self.customer.username}"

    def mark_as_paid(self):
        self.paid = True
        self.save()

    def get_items(self):
        return [item.get_item_details() for item in self.items.all()]

    def get_total_with_shipping(self):
        # محاسبه هزینه نهایی با احتساب هزینه پست
        return self.total_price + self.shipping_cost



class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="items")  # ارتباط با فاکتور
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ارتباط با کتاب
    quantity = models.PositiveIntegerField(default=1)  # تعداد کتاب در فاکتور
    price = models.DecimalField(max_digits=10, decimal_places=2)  # قیمت کتاب در زمان خرید

    def __str__(self):
        return f"{self.quantity} x {self.book.title}"

    def get_item_details(self):
        return {
            "book": self.book.title,
            "quantity": self.quantity,
            "price": self.price
        }


class Address(models.Model):
    PROVINCE_CHOICES = [
        ("1", "محل دائمی سکونت | مالک هستم | بیش از دو سال در این مکان هستم"),
        ("2", "محل دائمی سکونت | مالک هستم | بیش از یکسال و کمتر از دو سال در این مکان هستم"),
        ("3", "محل دائمی سکونت | مالک هستم | بزودی تغییر مکان می دهم"),
        ("4", "محل دائمی سکونت | مستاجر هستم | بیش از یکسال در این مکان هستم"),
        ("5", "محل دائمی سکونت | مستاجر هستم | کمتر از یکسال در این مکان هستم"),
        ("6", "محل موقت سکونت | در ایران ساکن نیستم و ساکن کشور دیگری هستم"),
        ("7", "محل موقت سکونت | مالک هستم | ساکن شهر دیگری هستم"),
        ("8", "محل موقتی سکونت | نه مالک و نه مستاجر هستم | بزودی تغییر مکان می دهم"),
        ("9", "محل دائمی کار و تجارت | مالک یا مستاجر هستم | بتازگی در این مکان هستم )کمتر از دوماه("),
        ("10", "محل دائمی کار و تجارت | مالک هستم | بیش از یکسال در این مکان هستم"),
        ("11", "محل دائمی کار و تجارت | مالک هستم | کمتر از یکسال در این مکان هستم )بیش از دو ماه("),
        ("12", "محل دائمی کار و تجارت | مستاجر هستم | بیش از یکسال در این مکان هستم"),
        ("13", "محل دائمی کار و تجارت | مستاجر هستم | کمتر از یکسال در این مکان هستم )بیش از دو ماه(")
    ]

    residence_type = models.CharField(
        max_length=2,
        choices=PROVINCE_CHOICES,
        null=True,
        blank=True,
        default=None
    )
    province = models.CharField(max_length=100, null=True, blank=True)
    province_code = models.CharField(max_length=10, null=True, blank=True)  # اضافه شده
    city = models.CharField(max_length=100, null=True, blank=True)
    city_code = models.CharField(max_length=10, null=True, blank=True)  # اضافه شده
    street_address = models.CharField(max_length=255, null=True, blank=True)
    house_number = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    unit_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.province}"



class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')  # ارتباط با مدل User
    first_name = models.CharField(max_length=100, null=True, blank=True)  # نام مشتری
    last_name = models.CharField(max_length=100, null=True, blank=True)  # نام خانوادگی مشتری
    gender = models.IntegerField(choices=[(1, 'Male'), (2, 'Female'), (3, 'Other')], null=True, blank=True)  # جنسیت
    national_id = models.CharField(max_length=10, null=True, blank=True)  # کد ملی 10 رقمی
    full_name = models.CharField(max_length=255, null=True, blank=True)  # نام کامل مشتری
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # شماره تماس
    email = models.EmailField(null=True, blank=True)  # ایمیل
    registration_date = models.DateTimeField(auto_now_add=True)  # تاریخ ثبت‌نام
    is_active = models.BooleanField(default=True)  # وضعیت فعال یا غیرفعال بودن مشتری
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='customers')  # ارتباط با آدرس

    # علاقه‌مندی‌ها
    favorite_genres = models.ManyToManyField(Genre, blank=True,
                                             related_name='favorited_by')  # علاقه‌مندی‌ها به ژانرها
    favorite_authors = models.ManyToManyField(Author, blank=True,
                                              related_name='favorited_by')  # علاقه‌مندی‌ها به نویسندگان
    favorite_publishers = models.ManyToManyField(Publisher, blank=True,
                                                 related_name='favorited_by')  # علاقه‌مندی‌ها به ناشران
    favorite_translators = models.ManyToManyField(Translator, blank=True,
                                                  related_name='favorited_by')  # علاقه‌مندی‌ها به مترجمان

    def __str__(self):
        return f"{self.user.username}'s profile"

    def get_total_books_bought(self):
        # محاسبه تعداد کتاب‌های خریداری شده توسط مشتری
        return sum([order.books.count() for order in self.orders.all()])



class CustomerInterest(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE)  # ارتباط یک به یک با مشتری

    # علاقه به ژانرها (درصد علاقه به هر ژانر)
    genre_interest = models.JSONField(default=dict)  # مثلا {"ترس": 20, "تاریخ": 80}

    # علاقه به نویسنده‌ها (درصد علاقه به هر نویسنده)
    author_interest = models.JSONField(default=dict)  # مثلا {"جک لندن": 50, "هرمان ملویل": 50}

    # علاقه به مترجمان (درصد علاقه به هر مترجم)
    translator_interest = models.JSONField(default=dict)  # مثلا {"محمدرضا شفیعی": 100}

    # علاقه به انتشارات‌ها (درصد علاقه به هر انتشارات)
    publisher_interest = models.JSONField(default=dict)  # مثلا {"نشر چشمه": 60, "نشر نی": 40}

    def __str__(self):
        return f"Interest data for {self.customer.username}"

    def update_interest(self):
        # محاسبه درصد علاقه برای هر دسته
        total_genre_books = sum(self.genre_interest.values())
        total_author_books = sum(self.author_interest.values())
        total_translator_books = sum(self.translator_interest.values())
        total_publisher_books = sum(self.publisher_interest.values())

        # به‌روزرسانی درصد علاقه‌ها
        if total_genre_books > 0:
            self.genre_interest = {k: (v / total_genre_books) * 100 for k, v in self.genre_interest.items()}
        if total_author_books > 0:
            self.author_interest = {k: (v / total_author_books) * 100 for k, v in self.author_interest.items()}
        if total_translator_books > 0:
            self.translator_interest = {k: (v / total_translator_books) * 100 for k, v in
                                        self.translator_interest.items()}
        if total_publisher_books > 0:
            self.publisher_interest = {k: (v / total_publisher_books) * 100 for k, v in self.publisher_interest.items()}

        self.save()


def update_customer_interest(customer, book, quantity=1):
    customer_interest, _ = CustomerInterest.objects.get_or_create(customer=customer)

    # به‌روزرسانی علاقه به ژانرها
    for genre in book.genres.all():
        customer_interest.genre_interest[genre.name] = customer_interest.genre_interest.get(genre.name, 0) + quantity

    # به‌روزرسانی علاقه به نویسنده، ناشر و مترجم
    if book.author:
        customer_interest.author_interest[book.author.full_name] = customer_interest.author_interest.get(book.author.full_name, 0) + quantity
    if book.publisher:
        customer_interest.publisher_interest[book.publisher.name] = customer_interest.publisher_interest.get(book.publisher.name, 0) + quantity
    if book.translator:
        customer_interest.translator_interest[book.translator.full_name] = customer_interest.translator_interest.get(book.translator.full_name, 0) + quantity

    customer_interest.update_interest()
    customer_interest.save()



# در مدل Cart
class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    discount_code = models.ForeignKey(Discount, null=True, blank=True, on_delete=models.SET_NULL)  # ارتباط با کد تخفیف
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # مقدار تخفیف اعمال‌شده

    def __str__(self):
        return f"Cart of {self.customer.full_name}"

    def get_total_price(self):
        # محاسبه قیمت کل بدون تخفیف
        total_price = sum([item.get_total_price() for item in self.items.all()])

        # اعمال تخفیف اگر موجود باشد
        if self.discount_amount > 0:
            total_price -= self.discount_amount

        return total_price

    def get_total_items(self):
        # محاسبه تعداد کل آیتم‌ها در سبد خرید
        return sum([item.quantity for item in self.items.all()])

    def apply_discount(self, discount_code):
        """
        چک کردن اعتبار کد تخفیف و اعمال آن به سبد خرید.
        تخفیف باید در صورتی که معتبر باشد، اعمال شود.
        """
        if discount_code.is_valid():
            self.discount_code = discount_code
            # محاسبه مبلغ تخفیف بر اساس درصد تخفیف
            total_price = self.get_total_price_without_discount()
            self.discount_amount = total_price * (discount_code.percentage / 100)
            self.save()
        else:
            raise ValueError("Invalid or expired discount code.")

    def get_total_weight(self):
        # محاسبه وزن کل سبد خرید
        total_weight = sum([item.book.weight * item.quantity for item in self.items.all()])
        return total_weight

    def get_total_price_without_discount(self):
        """
        محاسبه قیمت کل بدون اعمال تخفیف.
        """
        return sum([item.get_total_price() for item in self.items.all()])

    def clear_cart(self):
        """
        خالی کردن سبد خرید.
        """
        self.items.all().delete()
        self.discount_code = None
        self.discount_amount = 0
        self.save()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)  # ارجاع به مدل Book در اپلیکیشن library
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    def get_total_price(self):
        return self.book.price * self.quantity  # قیمت کل برای این آیتم (کتاب × تعداد)
