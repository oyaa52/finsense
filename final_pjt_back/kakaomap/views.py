from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings


# 카카오맵 JavaScript API 키 및 REST API 키 반환
# GET /api/kakaomap/apikey/
@api_view(['GET'])
def get_kakao_map_api_key(request):
    # settings.py에서 KAKAO_API_KEY (JavaScript용)와 KAKAO_REST_API_KEY (REST API용) 조회
    # 해당 설정이 없으면 None 반환
    js_api_key = getattr(settings, 'KAKAO_API_KEY', None)
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY', None)
    
    if js_api_key and rest_api_key:
        return Response({
            'kakaomap_api_key': js_api_key, 
            'kakaomap_rest_api_key': rest_api_key
        }, status=status.HTTP_200_OK)
    else:
        # 하나라도 키를 찾을 수 없는 경우 오류 응답
        missing_keys = []
        if not js_api_key:
            missing_keys.append('KAKAO_API_KEY (JavaScript용)')
        if not rest_api_key:
            missing_keys.append('KAKAO_REST_API_KEY (REST API용)')
        
        error_message = f"다음 카카오맵 API 키가 설정 파일(settings.py)에 없습니다: {', '.join(missing_keys)}"
        return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) # 서버 설정 문제이므로 500 사용
