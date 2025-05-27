from django.urls import path
from . import views # 현재 앱(recommendations)의 views 모듈 임포트

app_name = 'recommendations'  # URL 네임스페이스 설정 (예: {% url 'recommendations:youtube_search_main' %})

urlpatterns = [
    # (사용주의) GET /api/recommendations/youtube-search/ - YouTube 금융 동영상 검색 (페이지네이션 미지원)
    # views.py의 YoutubeVideoSearchAPIView 클래스에 연결. 현재 명확한 사용처는 없으나, utils.search_youtube_financial_videos 테스트 등 잠재적 사용 가능.
    path('youtube-search/', views.YoutubeVideoSearchAPIView.as_view(), name='youtube_search_main'),
    
    # GET /api/recommendations/youtube/economic-news/ - YouTube 경제/금융 뉴스 동영상 검색 (페이지네이션 지원)
    # views.py의 search_youtube_videos_paginated 함수 뷰에 연결. EconomicNewsView에서 사용.
    path('youtube/economic-news/', views.search_youtube_videos_paginated, name='youtube_economic_news_paginated'),
    
    # GET /api/recommendations/youtube/popular-financial-videos/ - 인기 금융 YouTube 동영상 조회 (메인 페이지용)
    # views.py의 PopularFinancialVideosAPIView 클래스에 연결.
    path('youtube/popular-financial-videos/', views.PopularFinancialVideosAPIView.as_view(), name='youtube_popular_financial'),
] 