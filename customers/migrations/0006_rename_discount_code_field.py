from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_remove_cartitem_book_remove_invoiceitem_book_and_more'),
        ('discounts', '0002_remove_discount_percentage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='discount_amount',
        ),
        migrations.RenameField(
            model_name='cart',
            old_name='discount_code',
            new_name='discount',
        ),
    ]
