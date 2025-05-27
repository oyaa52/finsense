from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile


# 새로운 사용자가 생성될 때 자동으로 Profile 객체 생성
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        Profile.objects.create(user=instance)

