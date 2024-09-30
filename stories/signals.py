from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserStory, UserBadge, Badge
from django.contrib.auth.models import User

@receiver(post_save, sender=UserStory)
def check_for_badge(sender, instance, **kwargs):
    user = instance.user
    story_count = UserStory.objects.filter(user=user).count()

    if story_count == 50:
        badge, created = Badge.objects.get_or_create(name="50 Hikaye Okuma", defaults={
            'description': "50 hikaye okudunuz!"
        })

        # Rozet daha önce verilmemişse kullanıcıya ekle
        if not UserBadge.objects.filter(user=user, badge=badge).exists():
            UserBadge.objects.create(user=user, badge=badge)
