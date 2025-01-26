from django.contrib import admin
from .models import Book
from authors.models import Author
from translators.models import Translator
from publishers.models import Publisher
from genres.models import Genre
from Language.models import Language

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'translator', 'publisher', 'publication_date', 'isbn', 'price', 'stock', 'sold_count', 'rating', 'discount')
    list_filter = ('author', 'translator', 'publisher', 'genre', 'language', 'publication_date')
    search_fields = ('title', 'isbn', 'author__name', 'translator__name', 'publisher__name', 'genre__name', 'language__name')
    list_editable = ('price', 'stock', 'rating', 'discount')
    ordering = ('-publication_date',)

admin.site.register(Book, BookAdmin)
