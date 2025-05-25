from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import search_youtube_financial_videos, get_youtube_videos # get_youtube_videos 임포트 확인
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated # 필요에 따라 사용
# from django.conf import settings # settings는 utils에서 사용
# import requests # requests는 현재 이 파일에서 사용 안 함

# Create your views here.

class YoutubeVideoSearchAPIView(APIView):
    # 이 APIView는 MainPageDefaultView에서 max_results=2로 사용 중.
    # 페이지네이션이 필요 없으므로 search_youtube_financial_videos 함수를 그대로 사용.
    def get(self, request):
        query = request.query_params.get('query', None)
        if not query:
            return Response({"error": "검색어('query' 파라미터)가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            max_results_str = request.query_params.get('max_results', '2') # 기본값 2
            max_results = int(max_results_str)
            if not (1 <= max_results <= 50): 
                max_results = 2 
        except ValueError:
            max_results = 2 

        videos = search_youtube_financial_videos(query, max_results=max_results)

        if isinstance(videos, str): 
            if "할당량을 초과했거나" in videos or "API에서 오류가 발생했습니다." in videos or "오류가 발생했습니다." in videos:
                return Response({"error": videos}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            return Response({"error": videos}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not videos:
            return Response({"message": "요청하신 검색어에 대한 금융 관련 영상을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response(videos, status=status.HTTP_200_OK)

@api_view(['GET'])
# @permission_classes([IsAuthenticated]) # EconomicNewsView는 누구나 볼 수 있으므로 인증 제거 또는 선택적 적용
def search_youtube_videos_paginated(request): # 함수 이름 변경으로 기존 API와 구분
    query = request.GET.get('query', '경제 뉴스') 
    page_token = request.GET.get('pageToken', None)
    
    try:
        max_results_str = request.GET.get('max_results', '6') 
        try:
            max_results = int(max_results_str)
            if not (1 <= max_results <= 50): # YouTube API maxResults는 1-50 사이 (0도 가능하지만 일반적으로 1 이상)
                max_results = 6 
        except ValueError:
            max_results = 6

        # 수정된 get_youtube_videos 함수 호출
        result_data = get_youtube_videos(query, max_results=max_results, page_token=page_token)
        
        # utils 함수에서 에러를 dict 형태로 반환하므로, 해당 'error' 키로 확인
        if result_data.get('error'):
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "할당량" in result_data['error'] else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(result_data, status=status_code) # 에러 메시지 포함된 전체 dict 반환

        return Response(result_data, status=status.HTTP_200_OK)
        
    except Exception as e: # 혹시 모를 다른 예외 처리
        # 일반적인 500 에러 메시지 (이 경우는 utils에서 처리되지 않은 예외)
        return Response({
            'error': f'서버 내부 오류가 발생했습니다: {str(e)}',
            'videos': [], 
            'nextPageToken': None, 
            'prevPageToken': None,
            'totalResults': 0,
            'resultsPerPage': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 기존 search_youtube_videos 함수는 혹시 다른 곳에서 사용될 수 있으므로, 
# 새 함수 search_youtube_videos_paginated를 만들었습니다.
# 만약 기존 함수를 대체하는 것이라면, urls.py에서 연결을 새 함수로 변경해야 합니다.
