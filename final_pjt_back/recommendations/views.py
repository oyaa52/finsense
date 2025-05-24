from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import search_youtube_financial_videos # 만들어둔 유틸리티 함수 임포트
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
import requests
from .utils import get_youtube_videos

# Create your views here.

class YoutubeVideoSearchAPIView(APIView):
    def get(self, request):
        query = request.query_params.get('query', None)
        if not query:
            return Response({"error": "검색어('query' 파라미터)가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 검색 결과 개수 (기본값 2개, 요청 시 최대 12개까지 가능하도록 수정, 메인 페이지에선 2개만 나오므로)
        try:
            max_results_str = request.query_params.get('max_results')
            if max_results_str is not None:
                max_results = int(max_results_str)
                if max_results <= 0 or max_results > 12: # 유효 범위: 1부터 12까지
                    max_results = 2 # 범위를 벗어나면 기본값 2로 설정
            else:
                max_results = 2 # 파라미터가 없으면 기본값 2로 설정
        except ValueError:
            max_results = 2 # 숫자로 변환할 수 없으면 기본값 2로 설정

        videos = search_youtube_financial_videos(query, max_results=max_results)

        if isinstance(videos, str): # 유틸리티 함수에서 오류 메시지를 문자열로 반환하는 경우
            if "할당량을 초과했거나" in videos or "API에서 오류가 발생했습니다." in videos or "오류가 발생했습니다." in videos:
                return Response({"error": videos}, status=status.HTTP_503_SERVICE_UNAVAILABLE) # 서비스 문제
            return Response({"error": videos}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # 일반 서버 오류
        
        if not videos:
            return Response({"message": "요청하신 검색어에 대한 금융 관련 영상을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        return Response(videos, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_youtube_videos(request):
    query = request.GET.get('query', '')
    if not query:
        return Response({'error': '검색어를 입력해주세요.'}, status=400)
    
    try:
        videos = get_youtube_videos(query)
        return Response(videos)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
