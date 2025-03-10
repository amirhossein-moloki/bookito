# Generated by Django 5.1.5 on 2025-01-26 13:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Language', '0001_initial'),
        ('authors', '0001_initial'),
        ('genres', '0001_initial'),
        ('publishers', '0001_initial'),
        ('translators', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('publication_date', models.DateField(blank=True, null=True)),
                ('isbn', models.CharField(blank=True, max_length=13, null=True, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('summary', models.TextField(blank=True, null=True)),
                ('page_count', models.IntegerField(blank=True, null=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='books/covers/')),
                ('stock', models.IntegerField(default=0)),
                ('sold_count', models.IntegerField(default=0)),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authors.author')),
                ('genre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='genres.genre')),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='Language.language')),
                ('publisher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='publishers.publisher')),
                ('translator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='translators.translator')),
            ],
        ),
    ]
