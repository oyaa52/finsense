from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings
from .models import DepositProduct, DepositOption
from .serializers import DepositProductsSerializer, DepositOptionsSerializer
import requests

# 금융위원회 API 키 설정
FIN_API_KEY = settings.FIN_API_KEY

@api_view(["GET"])
def save_deposit_products(request):
    """
    금융위원회 API에서 예금 상품 정보를 가져와서 데이터베이스에 저장하는 함수
    """
    try:
        # 금융위원회 API 호출
        r = requests.get(
            f"http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={FIN_API_KEY}&topFinGrpNo=020000&pageNo=1"
        )
        response = r.json()
        print("API Response:", response)

        # API 응답 형식 검증
        if 'result' not in response:
            print("Error: 'result' key not found in response")
            return Response({"error": "Invalid API response format"}, status=status.HTTP_400_BAD_REQUEST)

        # 기본 상품 정보와 옵션 정보 추출
        base_lst = response.get("result", {}).get("baseList", [])
        option_lst = response.get("result", {}).get("optionList", [])

        # 데이터 존재 여부 확인
        if not base_lst or not option_lst:
            print("Error: No data in baseList or optionList")
            return Response({"error": "No data available"}, status=status.HTTP_404_NOT_FOUND)

        # 데이터베이스에 저장
        save(base_lst, option_lst)

        return Response(response, status=status.HTTP_200_OK)
    except requests.exceptions.RequestException as e:
        print("Request Error:", str(e))
        return Response({"error": "Failed to fetch data from API"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        print("Unexpected Error:", str(e))
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def save(base_lst, option_lst):
    """
    API에서 받아온 예금 상품 정보를 데이터베이스에 저장하는 함수
    
    Args:
        base_lst (list): 기본 상품 정보 리스트
        option_lst (list): 상품 옵션 정보 리스트
    """
    # 기본 상품 정보 저장
    for entry in base_lst:
        DepositProduct.objects.update_or_create(
            fin_prdt_cd=entry['fin_prdt_cd'],
            defaults={
                "kor_co_nm": entry["kor_co_nm"],        # 은행명
                "fin_prdt_nm": entry["fin_prdt_nm"],    # 상품명
                "etc_note": entry["etc_note"],          # 상품설명
                "join_deny": entry["join_deny"],        # 가입제한
                "join_member": entry["join_member"],    # 가입대상
                "join_way": entry["join_way"],          # 가입방법
                "spcl_cnd": entry["spcl_cnd"],          # 특별조건
            }
        )

    # 상품 옵션 정보 저장
    for entry in option_lst:
        # 해당 상품 찾기
        parent = DepositProduct.objects.get(fin_prdt_cd=entry['fin_prdt_cd'])

        # save_trm 값 처리 (숫자형으로 변환, None 또는 빈 문자열일 경우 기본값 0 사용)
        raw_save_trm = entry.get('save_trm')
        if raw_save_trm is None or str(raw_save_trm).strip() == '':
            processed_save_trm = 0
        else:
            try:
                processed_save_trm = int(raw_save_trm)
            except (ValueError, TypeError):
                print(f"Warning: Invalid save_trm value '{raw_save_trm}' for option linked to product {entry['fin_prdt_cd']}. Using default 0.")
                processed_save_trm = 0
        
        # intr_rate 값 처리 (숫자형으로 변환, None 또는 빈 문자열일 경우 기본값 -1.0 사용)
        raw_intr_rate = entry.get('intr_rate')
        if raw_intr_rate is None or str(raw_intr_rate).strip() == '':
            processed_intr_rate = -1.0
        else:
            try:
                processed_intr_rate = float(raw_intr_rate)
            except (ValueError, TypeError):
                print(f"Warning: Invalid intr_rate value '{raw_intr_rate}' for option linked to product {entry['fin_prdt_cd']}. Using default -1.0.")
                processed_intr_rate = -1.0

        # intr_rate2 값 처리 (숫자형으로 변환, None 또는 빈 문자열일 경우 기본값 -1.0 사용)
        raw_intr_rate2 = entry.get('intr_rate2')
        if raw_intr_rate2 is None or str(raw_intr_rate2).strip() == '':
            processed_intr_rate2 = -1.0
        else:
            try:
                processed_intr_rate2 = float(raw_intr_rate2)
            except (ValueError, TypeError):
                print(f"Warning: Invalid intr_rate2 value '{raw_intr_rate2}' for option linked to product {entry['fin_prdt_cd']}. Using default -1.0.")
                processed_intr_rate2 = -1.0
        
        # 옵션 정보 저장 또는 업데이트
        DepositOption.objects.update_or_create(
            fin_prdt_cd=parent,
            intr_rate_type_nm=entry['intr_rate_type_nm'], # 이 값은 항상 유효하다고 가정
            save_trm=processed_save_trm, # 처리된 정수 값 사용
            defaults={
                "fin_prdt_cd": parent,
                "intr_rate_type_nm": entry["intr_rate_type_nm"],
                "intr_rate": processed_intr_rate,       # 처리된 실수 값 사용
                "intr_rate2": processed_intr_rate2,     # 처리된 실수 값 사용
                "save_trm": processed_save_trm,         # 처리된 정수 값 사용
            }
        )

# @api_view(['GET'])
# def deposit_product_options(request, fin_prdt_cd):
#     """
#     특정 예금 상품의 옵션 정보를 조회하는 함수
    
#     Args:
#         request: HTTP 요청 객체
#         fin_prdt_cd (str): 상품 코드
#     """
#     product = DepositProduct.objects.get(fin_prdt_cd=fin_prdt_cd)
#     option = DepositOption.objects.filter(fin_prdt_cd=product)  # 필드명을 fin_prdt_cd로 수정
#     serializer = DepositOptionsSerializer(option, many=True)
#     return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def top_rate(request):
#     """
#     가장 높은 우대금리를 가진 예금 상품 정보를 조회하는 함수
#     """
#     high_rate_option = DepositOption.objects.order_by('-intr_rate2').first()
#     high_rate_product = DepositProduct.objects.get(fin_prdt_cd=high_rate_option.fin_prdt_cd)  # 필드명 수정
#     data = {
#         'product': DepositProductsSerializer(high_rate_product).data,
#         'option': DepositOptionsSerializer(high_rate_option).data
#     }
#     return Response(data)

# @api_view(['GET', 'POST'])
# def deposit_products(request):
#     """
#     예금 상품 목록을 조회하거나 새로운 상품을 등록하는 함수
    
#     GET: 모든 예금 상품 목록 조회
#     POST: 새로운 예금 상품 등록
#     """
#     if request.method == 'GET':
#         products = DepositProduct.objects.all()
#         serializer = DepositProductsSerializer(products, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#     elif request.method == 'POST':
#         serializer = DepositProductsSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(
#             {"message": "이미 있는 데이터이거나, 데이터가 잘못 입력되었습니다."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

# 카카오맵 API 키를 반환하는 뷰
@api_view(['GET'])
def get_kakao_map_api_key(request):
    api_key = getattr(settings, 'KAKAO_MAP_API_KEY', None)
    if api_key:
        return Response({'kakao_map_api_key': api_key}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Kakao MAP API Key not found in settings.'}, status=status.HTTP_404_NOT_FOUND)
