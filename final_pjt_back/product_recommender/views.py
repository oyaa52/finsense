from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI, APIError as OpenAIAPIError
from django.conf import settings
import json
import os
import base64
import requests
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recommendations(request):
    logger.info("사용 중단된 추천 API (/api/recommender/recommendations/)가 호출되었습니다.")
    return Response({
        'status': 'deprecated',
        'message': '이 추천 기능은 더 이상 사용되지 않습니다. 대신 GPT 기반 추천 API (/api/recommender/gpt/)를 이용해 주십시오.'
    }, status=status.HTTP_410_GONE)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_gpt_recommendations(request):
    prompt = request.data.get('prompt')
    if not prompt:
        logger.warning("GPT 추천 요청 시 프롬프트가 누락되었습니다.")
        return Response({'status': 'error', 'message': '추천을 위한 프롬프트 내용이 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

    if not settings.GPT_API_KEY:
        logger.error("OpenAI API 키(GPT_API_KEY)가 설정되지 않아 GPT 추천을 생성할 수 없습니다.")
        return Response({'status': 'error', 'message': '서비스 환경 설정 오류: OpenAI API 키가 누락되었습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    logger.info(f"GPT 추천 요청 수신. 프롬프트: '{prompt[:50]}...' ")
    try:
        client = OpenAI(api_key=settings.GPT_API_KEY)
        completion_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 금융 상품 투자 추천 전문가입니다."},
                {"role": "user", "content": prompt}
            ]
        )
        
        gpt_response_content = completion_response.choices[0].message.content
        logger.info(f"GPT 추천 응답 수신 완료. 응답 길이: {len(gpt_response_content)}")
        return Response({
            'status': 'success',
            'response': gpt_response_content
        }, status=status.HTTP_200_OK)
        
    except OpenAIAPIError as e:
        logger.error(f"OpenAI API(GPT) 호출 중 오류 발생: {e}", exc_info=True)
        return Response({'status': 'error', 'message': f'GPT 기반 추천 생성 중 OpenAI 서비스 연동 오류가 발생했습니다: {e}'}, status=status.HTTP_502_BAD_GATEWAY)
    except Exception as e:
        logger.error(f"GPT 추천 API (/api/recommender/gpt/) 처리 중 예기치 않은 오류 발생: {e}", exc_info=True)
        return Response({'status': 'error', 'message': f'GPT 기반 추천 생성 중 알 수 없는 서버 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_image(request):
    prompt = request.data.get('prompt')
    image_type = request.data.get('type')
    
    logger.info(f"이미지 생성 요청 수신 - 프롬프트: '{prompt[:50]}...', 타입: {image_type}")
    
    if not prompt or not image_type:
        logger.warning("이미지 생성 요청 시 프롬프트 또는 타입이 누락되었습니다.")
        return Response({'status': 'error', 'message': '이미지 생성을 위한 프롬프트와 이미지 타입이 모두 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

    if not settings.GPT_API_KEY:
        logger.error("OpenAI API 키(GPT_API_KEY)가 설정되지 않아 이미지를 생성할 수 없습니다.")
        return Response({'status': 'error', 'message': '서비스 환경 설정 오류: OpenAI API 키가 누락되었습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    generated_image_url_for_error_log = 'N/A'
    try:
        logger.info("DALL-E API 호출 시작...")
        client = OpenAI(api_key=settings.GPT_API_KEY)
        image_generation_response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        generated_image_url = image_generation_response.data[0].url
        generated_image_url_for_error_log = generated_image_url
        logger.info(f"DALL-E API로부터 이미지 URL 수신: {generated_image_url}")

        save_dir = os.path.join(settings.MEDIA_ROOT, 'cute-3d')
        os.makedirs(save_dir, exist_ok=True)
        logger.info(f"이미지 저장 디렉토리: {save_dir}")

        safe_type = "".join(c for c in image_type if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_')
        image_filename = f"{safe_type}.png"
        image_path = os.path.join(save_dir, image_filename)
        logger.info(f"이미지 저장 경로: {image_path}")

        logger.info(f"이미지 다운로드 시작: {generated_image_url}")
        image_download_response = requests.get(generated_image_url, stream=True, timeout=30)
        image_download_response.raise_for_status()
        
        logger.info("이미지 다운로드 성공. 파일 저장 중...")
        with open(image_path, 'wb') as f:
            for chunk in image_download_response.iter_content(chunk_size=8192):
                f.write(chunk)
        logger.info(f"이미지 저장 완료: {image_path}")
        
        client_image_url = os.path.join(settings.MEDIA_URL, 'cute-3d', image_filename).replace('\\', '/')
        return Response({
            'status': 'success',
            'image_url': client_image_url
        }, status=status.HTTP_200_OK)

    except requests.exceptions.Timeout as e:
        logger.error(f"이미지 다운로드 시간 초과 (URL: {generated_image_url_for_error_log}): {e}", exc_info=True)
        return Response({'status': 'error', 'message': f'이미지 다운로드 중 시간 초과가 발생했습니다: {e}'}, status=status.HTTP_504_GATEWAY_TIMEOUT)
    except requests.exceptions.RequestException as e:
        logger.error(f"이미지 다운로드 중 오류 발생 (URL: {generated_image_url_for_error_log}): {e}", exc_info=True)
        return Response({'status': 'error', 'message': f'이미지 다운로드 중 오류가 발생했습니다: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except OpenAIAPIError as e:
        logger.error(f"OpenAI API(DALL-E) 호출 중 오류 발생: {e}", exc_info=True)
        error_message = f'이미지 생성 서비스(OpenAI) 호출 중 오류가 발생했습니다.'
        if hasattr(e, 'message') and e.message:
            error_message += f' ({e.message})'
        return Response({'status': 'error', 'message': error_message}, status=getattr(e, 'status_code', 502))
    except Exception as e:
        logger.error(f"이미지 생성 API (/api/recommender/generate-image/) 처리 중 예기치 않은 오류 발생: {e}", exc_info=True)
        return Response({'status': 'error', 'message': '이미지 생성 중 알 수 없는 서버 내부 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
