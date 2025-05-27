from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    email = models.EmailField(unique=True) # 이메일 중복 불가
    # username, password 등은 AbstractUser에서 상속
    # 추가 필요 필드는 여기에 정의


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # User 모델과 1:1 관계
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)], null=True, blank=True, help_text="나이")
    gender = models.CharField(max_length=10, null=True, blank=True, help_text="성별")
    occupation = models.CharField(max_length=50, null=True, blank=True, help_text="직업")
    marital_status = models.CharField(max_length=20, null=True, blank=True, help_text="결혼 여부")
    monthly_income = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text="월 소득 (단위: 원)")
    amount_available = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, help_text="사용 가능 금액 (단위: 원)")
    investment_purpose = models.CharField(max_length=100, null=True, blank=True, help_text="투자 목적")
    investment_term = models.IntegerField(null=True, blank=True, help_text="투자 기간 (단위: 개월)")
    investment_tendency = models.CharField(
        max_length=20, null=True, blank=True, help_text="투자 성향 (예: 안정형, 안정추구형, 위험중립형, 적극투자형, 공격투자형)"
    )  
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True, help_text="프로필 이미지")

    def __str__(self):
        return f"{self.user.username}'s profile"


class FavoriteChannel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_channels')
    channel_id = models.CharField(max_length=255) # 유튜브 채널 ID
    channel_title = models.CharField(max_length=255) # 유튜브 채널명
    added_at = models.DateTimeField(auto_now_add=True) # 즐겨찾기 추가 일시

    class Meta:
        unique_together = ('user', 'channel_id') # (사용자, 채널 ID) 조합은 유일해야 함
        ordering = ['-added_at'] # 최근 추가된 순으로 정렬

    def __str__(self):
        return f"{self.user.username} - {self.channel_title}"


class FavoriteVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_videos')
    video_id = models.CharField(max_length=255) # 유튜브 비디오 ID
    video_title = models.CharField(max_length=255) # 유튜브 비디오 제목
    thumbnail_url = models.URLField(max_length=500, blank=True, null=True) # 비디오 썸네일 URL
    channel_title = models.CharField(max_length=255, blank=True) # 비디오의 채널명
    publish_time = models.DateTimeField(null=True, blank=True) # 비디오 게시 일시
    added_at = models.DateTimeField(auto_now_add=True) # 즐겨찾기 추가 일시

    class Meta:
        unique_together = ('user', 'video_id') # (사용자, 비디오 ID) 조합은 유일해야 함
        ordering = ['-added_at'] # 최근 추가된 순으로 정렬

    def __str__(self):
        return f"{self.user.username} - {self.video_title}"
