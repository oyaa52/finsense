from django.db import models
from django.conf import settings

# Create your models here.


# 게시글 모델
class Post(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts') # 작성자
    content = models.TextField() # 내용
    image = models.ImageField(upload_to='posts/', null=True, blank=True) # 이미지 (선택 사항)
    created_at = models.DateTimeField(auto_now_add=True) # 생성일시
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True) # 좋아요 누른 사용자들

    class Meta:
        ordering = ['-created_at'] # 최신순 정렬

    def __str__(self):
        return f"{self.user.username}의 게시글 (ID: {self.pk})"


# 댓글 모델 (대댓글 지원)
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments') # 원본 게시글
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_comments') # 작성자, related_name 충돌 방지
    content = models.TextField() # 내용
    created_at = models.DateTimeField(auto_now_add=True) # 생성일시
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE) # 부모 댓글 (대댓글용)

    class Meta:
        ordering = ['created_at'] # 작성순 정렬

    def __str__(self):
        if self.parent:
            return f"{self.user.username}의 대댓글 (to: {self.parent.user.username}, Post ID: {self.post.pk})"
        return f"{self.user.username}의 댓글 (Post ID: {self.post.pk})"


# 팔로우 관계 모델
class Follow(models.Model):
    follower = models.ForeignKey( # 팔로우 하는 사용자
        settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE
    )
    following = models.ForeignKey( # 팔로우 받는 사용자
        settings.AUTH_USER_MODEL, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True) # 팔로우 시작일시

    class Meta:
        unique_together = ("follower", "following") # (팔로워, 팔로잉) 조합은 유일해야 함 (중복 팔로우 방지)
        ordering = ['-created_at'] # 최근 팔로우 순 정렬

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
