from django.contrib import admin
from .models import Author
from Language.models import Language
from genres.models import Genre

class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'birth_date', 'is_alive', 'nationality', 'number_of_books')
    list_filter = ('is_alive', 'nationality', 'languages', 'genres')
    search_fields = ('first_name', 'last_name', 'biography', 'birth_place', 'nationality')
    list_editable = ('is_alive', 'nationality', 'number_of_books')
    filter_horizontal = ('languages', 'genres')
    ordering = ('-birth_date',)

admin.site.register(Author, AuthorAdmin)
