from django.urls import path
from . import views # views 임포트

app_name = 'recommendations'

urlpatterns = [
    # 메인 페이지 기본 뉴스 영상 로드용 (페이지네이션 X, max_results=2 고정)
    path('youtube-search/', views.YoutubeVideoSearchAPIView.as_view(), name='youtube_search_main'),
    
    # EconomicNewsView용 (페이지네이션 O, 검색 기능 포함 가능)
    path('youtube/economic-news/', views.search_youtube_videos_paginated, name='youtube_economic_news_paginated'),
    
    # 기존 path('youtube/search/', views.search_youtube_videos, name='search_youtube_videos'),는
    # 새 paginated API로 대체되었으므로 주석 처리 또는 삭제합니다.
    # 여기서는 주석 처리합니다.
    # path('youtube/search/', views.search_youtube_videos, name='search_youtube_videos'), 
] 