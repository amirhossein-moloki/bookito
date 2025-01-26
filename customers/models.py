from django.db import models
from accounts.models import User
from books.models import Book  # وارد کردن مدل Book از اپلیکیشن library

class Invoice(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="invoices")  # ارتباط با مشتری
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # قیمت کل خرید
    created_at = models.DateTimeField(auto_now_add=True)  # تاریخ ایجاد فاکتور
    paid = models.BooleanField(default=False)  # وضعیت پرداخت

    def __str__(self):
        return f"Invoice {self.id} for {self.customer.username}"

    def mark_as_paid(self):
        self.paid = True
        self.save()

    def get_items(self):
        # بازگشت همه آیتم‌های فاکتور (کتاب‌ها و تعداد آن‌ها)
        return [item.get_item_details() for item in self.items.all()]

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
    province = models.CharField(max_length=100, null=True, blank=True)  # استان
    city = models.CharField(max_length=100, null=True, blank=True)  # شهر
    street_address = models.CharField(max_length=255, null=True, blank=True)  # آدرس خیابان
    house_number = models.CharField(max_length=50, null=True, blank=True)  # پلاک
    postal_code = models.CharField(max_length=10, null=True, blank=True)  # کد پستی

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.province}"


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer')  # ارتباط با مدل User
    full_name = models.CharField(max_length=255, null=True, blank=True)  # نام کامل مشتری
    phone_number = models.CharField(max_length=15, null=True, blank=True)  # شماره تماس
    email = models.EmailField(null=True, blank=True)  # ایمیل
    registration_date = models.DateTimeField(auto_now_add=True)  # تاریخ ثبت‌نام
    is_active = models.BooleanField(default=True)  # وضعیت فعال یا غیرفعال بودن مشتری
    address = models.ForeignKey(Address, null=True, blank=True, on_delete=models.SET_NULL,
                                related_name='customers')  # ارتباط با آدرس

    # علاقه‌مندی‌ها
    favorite_genres = models.ManyToManyField('Genre', blank=True,
                                             related_name='favorited_by')  # علاقه‌مندی‌ها به ژانرها
    favorite_authors = models.ManyToManyField('Author', blank=True,
                                              related_name='favorited_by')  # علاقه‌مندی‌ها به نویسندگان
    favorite_publishers = models.ManyToManyField('Publisher', blank=True,
                                                 related_name='favorited_by')  # علاقه‌مندی‌ها به ناشران
    favorite_translators = models.ManyToManyField('Translator', blank=True,
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
    # فرض می‌کنیم که CustomerInterest برای این مشتری موجود است
    customer_interest, created = CustomerInterest.objects.get_or_create(customer=customer)

    # اطلاعات مرتبط با ژانر، نویسنده، مترجم و انتشارات
    genre = book.genre.name  # ژانر کتاب
    author = book.author.first_name  # نویسنده کتاب
    publisher = book.publisher.name  # انتشارات کتاب
    translator = book.translator.first_name if book.translator else None  # مترجم کتاب

    # به‌روزرسانی علاقه‌مندی‌ها برای ژانر، نویسنده، مترجم و انتشارات
    customer_interest.genre_interest[genre] = customer_interest.genre_interest.get(genre, 0) + quantity
    customer_interest.author_interest[author] = customer_interest.author_interest.get(author, 0) + quantity
    customer_interest.publisher_interest[publisher] = customer_interest.publisher_interest.get(publisher, 0) + quantity
    if translator:
        customer_interest.translator_interest[translator] = customer_interest.translator_interest.get(translator,
                                                                                                      0) + quantity

    # به‌روزرسانی درصدها بعد از هر خرید
    customer_interest.update_interest()

    # ذخیره تغییرات
    customer_interest.save()


class Cart(models.Model):
    customer = models.OneToOneField('Customer', on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    discount_code = models.ForeignKey('DiscountCode', null=True, blank=True,
                                      on_delete=models.SET_NULL)  # ارتباط با کد تخفیف
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # مقدار تخفیف اعمال‌شده

    def __str__(self):
        return f"Cart of {self.customer.full_name}"

    def get_total_price(self):
        # محاسبه قیمت کل
        total_price = sum([item.get_total_price() for item in self.items.all()])

        # اعمال تخفیف اگر موجود باشد
        total_price -= self.discount_amount
        return total_price

    def get_total_items(self):
        return sum([item.quantity for item in self.items.all()])

    def apply_discount(self, discount_code):
        # چک کردن اعتبار کد تخفیف
        if discount_code.is_valid():
            self.discount_code = discount_code
            self.discount_amount = self.get_total_price() * (discount_code.discount_percentage / 100)  # محاسبه تخفیف
            self.save()
        else:
            raise ValueError("Invalid or expired discount code.")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('library.Book', on_delete=models.CASCADE)  # ارجاع به مدل Book در اپلیکیشن library
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.book.title} x {self.quantity}"

    def get_total_price(self):
        return self.book.price * self.quantity  # قیمت کل برای این آیتم (کتاب × تعداد)


# اضافه کردن محصولات به سبد خرید و کاهش موجودی
def add_to_cart(cart, book, quantity=1):
    if book.stock >= quantity:
        # اضافه کردن آیتم به سبد خرید
        cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
        cart_item.quantity += quantity
        cart_item.save()

        # کاهش موجودی و افزایش تعداد فروش
        book.decrease_stock(quantity)
    else:
        raise ValueError("Not enough stock available")


# پس از پرداخت و تکمیل خرید
def complete_purchase(cart):
    # ایجاد فاکتور جدید
    total_price = cart.get_total_price()
    invoice = Invoice.objects.create(customer=cart.customer, total_price=total_price)
    invoice.mark_as_paid()  # وضعیت پرداخت را تغییر می‌دهیم

    # حذف محصولات از سبد خرید و انتقال به وضعیت پردازش
    cart.is_active = False
    cart.save()

    # افزودن محصولات به وضعیت پردازش (مثلاً انتقال به جدول سفارشات)
    # این قسمت بستگی به ساختار پروژه شما دارد
