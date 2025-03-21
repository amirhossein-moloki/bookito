# Generated by Django 5.1.5 on 2025-01-26 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Language', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Translator',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('birth_date', models.DateField(blank=True, null=True)),
                ('nationality', models.CharField(blank=True, max_length=100, null=True)),
                ('biography', models.TextField(blank=True, null=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='translator_pictures/')),
                ('rating', models.DecimalField(blank=True, decimal_places=2, max_digits=3, null=True)),
                ('languages', models.ManyToManyField(blank=True, to='Language.language')),
            ],
        ),
    ]
