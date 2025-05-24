from django.urls import path
from . import views # views 임포트

app_name = 'recommendations'

urlpatterns = [
    path('youtube-search/', views.YoutubeVideoSearchAPIView.as_view(), name='youtube_search'), # 주석 해제 및 연결
] 