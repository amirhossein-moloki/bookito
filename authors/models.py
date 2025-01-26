from django.db import models
from Language.models import Language
from genres.models import Genre
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField()
    birth_date = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='authors/', null=True, blank=True)
    is_alive = models.BooleanField(default=True)
    birth_place = models.CharField(max_length=255, null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    number_of_books = models.IntegerField(default=0)
    social_media_links = models.JSONField(null=True, blank=True)
    awards = models.TextField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    # تغییر فیلد languages به ارتباط Many-to-Many با مدل Language
    languages = models.ManyToManyField(Language, related_name='authors', blank=True)
    website = models.URLField(null=True, blank=True)
    genres = models.ManyToManyField(Genre, related_name='authors')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
