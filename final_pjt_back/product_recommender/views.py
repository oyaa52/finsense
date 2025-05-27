from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
from django.conf import settings
import json
import os
import base64

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    """
    사용자의 프로필 정보를 기반으로 실시간으로 금융상품을 추천합니다.
    """
    try:
        return Response({
            'status': 'success',
            'message': 'This endpoint is deprecated. Please use the GPT endpoint instead.'
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_gpt_recommendations(request):
    """GPT를 사용하여 금융상품 추천을 생성합니다."""
    try:
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({'status': 'error', 'message': '프롬프트가 필요합니다.'}, status=400)

        client = OpenAI(api_key=settings.GPT_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a financial advisor who provides investment recommendations."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return Response({
            'status': 'success',
            'response': response.choices[0].message.content
        })
        
    except Exception as e:
        print(f"GPT API 에러: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_image(request):
    try:
        prompt = request.data.get('prompt')
        image_type = request.data.get('type')
        
        print(f"이미지 생성 요청 받음 - 프롬프트: {prompt}, 타입: {image_type}")
        
        if not prompt or not image_type:
            return Response({'status': 'error', 'message': '프롬프트와 이미지 타입이 필요합니다.'}, status=400)

        print("DALL-E API 호출 시작")
        client = OpenAI(api_key=settings.GPT_API_KEY)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        print(f"DALL-E API 응답: {response}")
        image_url = response.data[0].url
        print(f"생성된 이미지 URL: {image_url}")

        # 이미지 저장 경로 수정
        save_dir = os.path.join(settings.BASE_DIR, 'media', 'cute-3d')
        os.makedirs(save_dir, exist_ok=True)
        print(f"저장 디렉토리: {save_dir}")

        # 파일명에서 특수문자 제거
        safe_type = "".join(c for c in image_type if c.isalnum() or c in (' ', '-', '_')).strip()
        image_filename = f"{safe_type}.png"
        image_path = os.path.join(save_dir, image_filename)
        print(f"저장할 이미지 경로: {image_path}")

        import requests
        print("이미지 다운로드 시작")
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            print("이미지 다운로드 성공")
            with open(image_path, 'wb') as f:
                f.write(image_response.content)
            print("이미지 저장 완료")
            
            # URL 경로 수정
            image_url = f"/media/cute-3d/{image_filename}"
            return Response({
                'status': 'success',
                'image_url': image_url
            })
        else:
            print(f"이미지 다운로드 실패 - 상태 코드: {image_response.status_code}")
            return Response({'status': 'error', 'message': '이미지 다운로드 실패'}, status=500)

    except Exception as e:
        print(f"DALL-E API 에러: {str(e)}")
        return Response({'status': 'error', 'message': str(e)}, status=500)
