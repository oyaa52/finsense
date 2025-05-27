from django.contrib import admin
from .models import User, Profile, FavoriteChannel, FavoriteVideo

# Django 관리자 페이지에 accounts 앱 모델 등록
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(FavoriteChannel)
admin.site.register(FavoriteVideo)
