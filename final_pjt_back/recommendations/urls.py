from django.urls import path
from . import views # views 임포트

app_name = 'recommendations'

urlpatterns = [
    # 메인 페이지 기본 뉴스 영상 로드용 (페이지네이션 X, max_results=2 고정)
    # 현재 MainPageDefaultView는 PopularFinancialVideosAPIView를 사용하므로,
    # 이 YoutubeVideoSearchAPIView에 대한 URL 패턴은 직접적으로 사용되지 않을 수 있습니다.
    # 다만, utils.py의 search_youtube_financial_videos 함수가 fallback으로 사용되므로
    # 해당 함수를 직접 테스트하거나 다른 용도로 사용될 가능성을 고려하여 남겨둘 수 있습니다.
    # 명확히 사용되지 않는다면 삭제해도 무방합니다.
    path('youtube-search/', views.YoutubeVideoSearchAPIView.as_view(), name='youtube_search_main'),
    
    # EconomicNewsView용 (페이지네이션 O, 검색 기능 포함)
    path('youtube/economic-news/', views.search_youtube_videos_paginated, name='youtube_economic_news_paginated'),
    
    # 사용되지 않는 이전 URL 패턴은 삭제합니다.
    # path('youtube/search/', views.search_youtube_videos, name='search_youtube_videos'), 

    # 메인 페이지 인기 금융 영상 (상위 2개)
    path('youtube/popular-financial-videos/', views.PopularFinancialVideosAPIView.as_view(), name='youtube_popular_financial'),
] 