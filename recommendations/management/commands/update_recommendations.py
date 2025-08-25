from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from recommendations.models import BookRecommendation
from recommendations.logic import get_hybrid_recommendations
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Updates book recommendations for all users.'

    def handle(self, *args, **options):
        User = get_user_model()
        users = User.objects.all()
        self.stdout.write(f'Starting recommendation update for {users.count()} users...')

        for user in users:
            try:
                recommendations = get_hybrid_recommendations(user)
                if recommendations:
                    recommendation_obj, created = BookRecommendation.objects.get_or_create(user=user)
                    recommendation_obj.recommendations.set(recommendations)
                    recommendation_obj.save()
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Successfully created and updated recommendations for {user.username}'))
                    else:
                        self.stdout.write(self.style.SUCCESS(f'Successfully updated recommendations for {user.username}'))
                else:
                    self.stdout.write(self.style.WARNING(f'No recommendations generated for {user.username}'))
            except Exception as e:
                logger.error(f"Could not update recommendations for {user.username}: {e}")
                self.stderr.write(self.style.ERROR(f'Failed to update recommendations for {user.username}: {e}'))

        self.stdout.write(self.style.SUCCESS('Finished updating recommendations for all users.'))
