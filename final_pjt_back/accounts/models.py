from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    email = models.EmailField(unique=True)

    # products/models.py에 있는 DepositProduct,SavingProduct (중간 테이블 역할)
    # username, password 등은 AbstractUser에서 상속받음
    # 필요한 경우 여기에 추가 필드를 정의할 수 있음


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)], null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    occupation = models.CharField(max_length=50, null=True, blank=True)
    marital_status = models.CharField(max_length=20, null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    amount_available = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    investment_purpose = models.CharField(max_length=100, null=True, blank=True)
    investment_term = models.IntegerField(null=True, blank=True)  # 개월 단위
    investment_tendency = models.CharField(
        max_length=20, null=True, blank=True
    )  # 안정형, 안정추구형, 위험중립형, 적극투자형, 공격투자형
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    social_profile_image_url = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


class FavoriteChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_channels')
    channel_id = models.CharField(max_length=255)
    channel_title = models.CharField(max_length=255)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'channel_id') # 사용자와 채널 ID 조합은 유일해야 함
        ordering = ['-added_at'] # 최근 추가된 순으로 정렬

    def __str__(self):
        return f"{self.user.username} - {self.channel_title}"


class FavoriteVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_videos')
    video_id = models.CharField(max_length=255)
    video_title = models.CharField(max_length=255)
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True)
    channel_title = models.CharField(max_length=255, blank=True)
    publish_time = models.DateTimeField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video_id') # 사용자와 비디오 ID 조합은 유일해야 함
        ordering = ['-added_at'] # 최근 추가된 순으로 정렬

    def __str__(self):
        return f"{self.user.username} - {self.video_title}"
