from django.contrib import admin
from .models import AssetPrice

# Django 관리자 페이지에 assetinfo 앱 모델 등록
admin.site.register(AssetPrice)
