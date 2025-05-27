from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import search_youtube_financial_videos, get_youtube_videos, get_popular_financial_videos # utils 함수 임포트
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated # 필요시 인증에 사용
import logging # 로깅 모듈 임포트

logger = logging.getLogger(__name__) # 로거 인스턴스 생성

# Create your views here.

# (사용주의) GET /api/recommendations/youtube-search/ - YouTube 금융 동영상 검색 (페이지네이션 미지원, 사용처 불분명)
class YoutubeVideoSearchAPIView(APIView):
    # 이 API는 현재 명확한 사용처가 없거나 search_youtube_videos_paginated로 대체되었을 수 있습니다.
    # 호출 전 확인 필요. utils.search_youtube_financial_videos 사용.
    def get(self, request):
        query = request.query_params.get('query', None) # 검색어
        if not query:
            logger.warning("YoutubeVideoSearchAPIView: 'query' 파라미터 누락")
            return Response({"error": "검색어('query' 파라미터)가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 반환할 최대 결과 수 (기본값: 2, 범위: 1-50)
            max_results_str = request.query_params.get('max_results', '2') 
            max_results = int(max_results_str)
            if not (1 <= max_results <= 50): 
                logger.warning(f"YoutubeVideoSearchAPIView: max_results({max_results}) 범위 초과. 기본값 2로 설정.")
                max_results = 2 
        except ValueError:
            logger.warning(f"YoutubeVideoSearchAPIView: max_results 파라미터('{max_results_str}')가 유효하지 않은 정수. 기본값 2로 설정.")
            max_results = 2 

        logger.info(f"YoutubeVideoSearchAPIView: 검색 실행 - query: '{query}', max_results: {max_results}")
        videos = search_youtube_financial_videos(query, max_results=max_results)

        # utils.search_youtube_financial_videos 함수는 오류 시 문자열 반환 가능
        if isinstance(videos, str): 
            logger.error(f"YoutubeVideoSearchAPIView: utils.search_youtube_financial_videos 함수 오류 반환 - {videos}")
            # YouTube API 할당량 초과 또는 주요 API 오류 시 503 반환
            if "할당량을 초과했거나" in videos or "API에서 오류가 발생했습니다." in videos or "오류가 발생했습니다." in videos:
                return Response({"error": f"YouTube API 서비스에 문제가 발생했습니다: {videos}"}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            # 기타 내부 오류 시 500 반환
            return Response({"error": f"동영상 검색 중 내부 서버 오류가 발생했습니다: {videos}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        if not videos: # 검색 결과 없는 경우
            logger.info(f"YoutubeVideoSearchAPIView: 검색 결과 없음 - query: '{query}'")
            return Response({"message": f"'{query}'에 대한 금융 관련 영상을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        logger.info(f"YoutubeVideoSearchAPIView: 검색 성공 - {len(videos)}개 결과 반환.")
        return Response(videos, status=status.HTTP_200_OK)

# GET /api/recommendations/youtube-videos-paginated/ - YouTube 금융 동영상 검색 (페이지네이션 지원, 경제 뉴스 검색용)
@api_view(['GET']) # 이 뷰는 GET 요청만 허용
# @permission_classes([IsAuthenticated]) # 현재는 인증 불필요 (주석 처리 유지)
def search_youtube_videos_paginated(request):
    query = request.GET.get('query', '경제 뉴스') # 검색어 (기본값: '경제 뉴스')
    page_token = request.GET.get('pageToken', None) # 다음/이전 페이지 토큰
    
    try:
        # 반환할 최대 결과 수 (기본값: 6, 범위: 1-50)
        max_results_str = request.GET.get('max_results', '6') 
        try:
            max_results = int(max_results_str)
            if not (1 <= max_results <= 50): 
                logger.warning(f"search_youtube_videos_paginated: max_results({max_results}) 범위 초과. 기본값 6으로 설정.")
                max_results = 6
        except ValueError:
            logger.warning(f"search_youtube_videos_paginated: max_results 파라미터('{max_results_str}')가 유효하지 않은 정수. 기본값 6으로 설정.")
            max_results = 6

        logger.info(f"search_youtube_videos_paginated: 검색 실행 - query: '{query}', max_results: {max_results}, page_token: {page_token}")
        # utils.get_youtube_videos 호출 (페이지네이션 결과 반환)
        result_data = get_youtube_videos(query, max_results=max_results, page_token=page_token)
        
        # utils.get_youtube_videos 함수는 오류 발생 시 'error' 키를 포함한 dict 반환
        if result_data.get('error'):
            error_message = result_data['error']
            logger.error(f"search_youtube_videos_paginated: utils.get_youtube_videos 함수 오류 반환 - {error_message}")
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "할당량" in error_message else status.HTTP_500_INTERNAL_SERVER_ERROR
            return Response(result_data, status=status_code) # 에러 메시지가 포함된 전체 result_data 반환

        logger.info(f"search_youtube_videos_paginated: 검색 성공 - {len(result_data.get('videos',[]))}개 결과 반환.")
        return Response(result_data, status=status.HTTP_200_OK)
        
    except Exception as e: # utils.get_youtube_videos 내부에서 처리되지 않은 예외 발생 시
        logger.error(f"search_youtube_videos_paginated: 예기치 않은 오류 발생 - {e}", exc_info=True)
        # 클라이언트에게 반환할 표준 오류 응답 구조
        return Response({
            'error': f'동영상 검색 중 예기치 않은 서버 내부 오류가 발생했습니다: {str(e)}',
            'videos': [], 
            'nextPageToken': None, 
            'prevPageToken': None,
            'totalResults': 0,
            'resultsPerPage': 0
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# GET /api/recommendations/popular-financial-videos/ - 인기 금융 YouTube 동영상 조회 (메인 페이지용)
class PopularFinancialVideosAPIView(APIView):
    # utils.get_popular_financial_videos 사용.
    def get(self, request):
        logger.info("PopularFinancialVideosAPIView: 인기 금융 동영상 조회 요청 수신")
        try:
            result_data = get_popular_financial_videos() # max_results는 utils 함수 내부 기본값 사용

            # utils.get_popular_financial_videos 함수는 오류 발생 시 'error' 키를 포함한 dict 반환
            if result_data.get('error'):
                error_message = result_data['error']
                logger.error(f"PopularFinancialVideosAPIView: utils.get_popular_financial_videos 함수 오류 반환 - {error_message}")
                status_code = status.HTTP_503_SERVICE_UNAVAILABLE if "할당량" in error_message else status.HTTP_500_INTERNAL_SERVER_ERROR
                return Response(result_data, status=status_code)
            
            logger.info(f"PopularFinancialVideosAPIView: 인기 금융 동영상 조회 성공 - {len(result_data.get('videos',[]))}개 결과 반환.")
            return Response(result_data, status=status.HTTP_200_OK)

        except Exception as e: # utils.get_popular_financial_videos 내부에서 처리되지 않은 예외 발생 시
            logger.error(f"PopularFinancialVideosAPIView: 예기치 않은 오류 발생 - {e}", exc_info=True)
            return Response({
                'error': f'인기 금융 영상 조회 중 예기치 않은 서버 내부 오류가 발생했습니다: {str(e)}',
                'videos': [] # 오류 시 빈 비디오 리스트 반환
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
