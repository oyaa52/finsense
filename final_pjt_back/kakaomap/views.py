
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings


# 카카오맵 API 키를 반환하는 뷰
@api_view(['GET'])
def get_kakao_map_api_key(request):
    api_key = getattr(settings, 'KAKAO_API_KEY', None)
    rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY', None)
    if api_key and rest_api_key:
        return Response({'kakaomap_api_key': api_key, 'kakaomap_rest_api_key': rest_api_key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Kakao MAP API Key not found in settings.'}, status=status.HTTP_404_NOT_FOUND)
