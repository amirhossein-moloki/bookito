from django.db import models

class Language(models.Model):
    name = models.CharField(max_length=100, unique=True)  # نام زبان

    def __str__(self):
        return self.name
