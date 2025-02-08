from django.contrib import admin
from .models import Book
from authors.models import Author
from translators.models import Translator
from publishers.models import Publisher
from genres.models import Genre
from Language.models import Language

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_authors', 'get_translators', 'publisher', 'publication_date', 'isbn', 'price', 'stock', 'sold_count', 'rating', 'discount')
    list_filter = ('authors', 'translators', 'publisher', 'genres', 'language', 'publication_date')  # اصلاح شده
    search_fields = ('title', 'isbn', 'authors__name', 'translators__name', 'publisher__name', 'genres__name', 'language__name')
    list_editable = ('price', 'stock', 'rating', 'discount')
    ordering = ('-publication_date',)

    # متدهایی برای گرفتن نام نویسنده‌ها و مترجم‌ها
    def get_authors(self, obj):
        return ", ".join([f"{author.first_name} {author.last_name}" for author in obj.authors.all()])

    get_authors.short_description = 'Authors'

    def get_translators(self, obj):
        return ", ".join([str(translator) for translator in obj.translators.all()])

    get_translators.short_description = 'Translators'


admin.site.register(Book, BookAdmin)

