from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile


# User 모델 생성 후 Profile 자동 생성 시그널
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    # 사용자가 새로 생성되었을 때 Profile 객체 생성
    if created:
        Profile.objects.create(user=instance)

