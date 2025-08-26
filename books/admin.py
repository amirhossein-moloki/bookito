from django.contrib import admin
from .models import Book, BookFormat
from authors.models import Author
from translators.models import Translator
from publishers.models import Publisher
from genres.models import Genre
from Language.models import Language

class BookFormatInline(admin.TabularInline):
    model = BookFormat
    extra = 1  # Number of extra forms to display

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_authors', 'get_translators', 'publisher', 'publication_date', 'sold_count')
    list_filter = ('authors', 'translators', 'publisher', 'genres', 'language', 'publication_date')
    search_fields = ('title', 'authors__name', 'translators__name', 'publisher__name')
    ordering = ('-publication_date',)
    inlines = [BookFormatInline]

    def get_authors(self, obj):
        return ", ".join([f"{author.first_name} {author.last_name}" for author in obj.authors.all()])
    get_authors.short_description = 'Authors'

    def get_translators(self, obj):
        return ", ".join([str(translator) for translator in obj.translators.all()])
    get_translators.short_description = 'Translators'

admin.site.register(Book, BookAdmin)

@admin.register(BookFormat)
class BookFormatAdmin(admin.ModelAdmin):
    list_display = ('book', 'format_name', 'price', 'stock', 'status', 'preorder_end_date', 'isbn')
    search_fields = ('book__title', 'format_name', 'isbn')
    list_filter = ('format_name', 'status')
    autocomplete_fields = ['book']
    fieldsets = (
        (None, {
            'fields': ('book', 'format_name', 'isbn')
        }),
        ('Pricing and Stock', {
            'fields': ('price', 'discount', 'stock', 'status', 'preorder_end_date')
        }),
        ('Physical Attributes', {
            'fields': ('page_count', 'weight', 'cover_image')
        }),
    )
