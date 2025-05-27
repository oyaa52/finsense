from django.contrib import admin
from .models import Post, Comment, Follow

# Django 관리자 페이지에 community 앱 모델 등록
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follow)
