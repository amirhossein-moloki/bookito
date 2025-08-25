from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import BookFormat, StockNotification

@receiver(post_save, sender=BookFormat)
def send_stock_notifications(sender, instance, created, **kwargs):
    """
    Signal receiver to send notifications when a BookFormat comes back in stock.
    """
    if not created and instance.stock > 0:
        # To avoid sending notifications every time an in-stock item is saved,
        # we check for pending notifications. This implies the item was out of stock.

        pending_notifications = StockNotification.objects.filter(
            book_format=instance,
            notified=False
        )

        if pending_notifications.exists():
            subject = f"کتاب مورد علاقه شما موجود شد: {instance.book.title}"
            from_email = settings.EMAIL_HOST_USER

            for notification in pending_notifications:
                message = (
                    f"سلام {notification.user.username},\n\n"
                    f"کتاب '{instance.book.title}' (فرمت: {instance.format_name}) که منتظرش بودید، دوباره موجود شده است.\n"
                    f"هم اکنون می‌توانید آن را از فروشگاه ما تهیه کنید.\n\n"
                    f"با تشکر,\n"
                    f"تیم فروشگاه کتاب"
                )

                try:
                    # In a real app, this should be an async task (e.g., Celery)
                    send_mail(
                        subject,
                        message,
                        from_email,
                        [notification.user.email],
                        fail_silently=False,
                    )
                    notification.notified = True
                    notification.notified_at = timezone.now()
                    notification.save(update_fields=['notified', 'notified_at'])
                except Exception as e:
                    # Proper logging should be implemented here
                    print(f"Failed to send stock notification email to {notification.user.email}: {e}")
