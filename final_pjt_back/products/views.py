from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from django.conf import settings
from .models import (
    DepositProduct,
    DepositOption,
    SavingProduct,
    SavingOption,
    DepositSubscription,
    SavingSubscription,
)
from .serializers import (
    DepositProductSerializer,
    DepositOptionSerializer,
    SavingProductSerializer,
    SavingOptionSerializer,
)
import requests
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

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

        if "result" not in response:
            return Response(
                {"error": "Invalid API response format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        base_lst = response.get("result", {}).get("baseList", [])
        option_lst = response.get("result", {}).get("optionList", [])

        if not base_lst or not option_lst:
            return Response(
                {"error": "No data available"}, status=status.HTTP_404_NOT_FOUND
            )

        save_deposit_data(
            base_lst, option_lst
        )  # 함수 이름 명확하게 변경: save -> save_deposit_data

        return Response(
            {"message": "예금 상품 정보 저장 성공"}, status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        return Response(
            {"error": "Failed to fetch data from API"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def save_deposit_data(base_lst, option_lst):
    """
    API에서 받아온 예금 상품 정보를 데이터베이스에 저장하는 함수
    """
    for entry in base_lst:
        # DepositProduct 모델 필드에 맞게 API 응답 필드 매핑
        product_data = {
            "kor_co_nm": entry.get("kor_co_nm"),
            "fin_prdt_nm": entry.get("fin_prdt_nm"),
            "join_way": entry.get("join_way"),
            "mtrt_int": entry.get("mtrt_int"),
            "spcl_cnd": entry.get("spcl_cnd"),
            "join_deny": entry.get("join_deny"),
            "join_member": entry.get("join_member"),
            "etc_note": entry.get("etc_note"),
            "max_limit": entry.get("max_limit"),
            "dcls_strt_day": entry.get("dcls_strt_day"),
            "dcls_end_day": entry.get("dcls_end_day"),
            "fin_co_subm_day": entry.get("fin_co_subm_day"),
        }
        # null=True, blank=True가 아닌 필드 중 API에 없을 수 있는 필드는 .get(key, default_value) 처리 필요
        DepositProduct.objects.update_or_create(
            fin_prdt_cd=entry["fin_prdt_cd"],
            defaults=product_data,
        )

    for entry in option_lst:
        try:
            parent_product = DepositProduct.objects.get(
                fin_prdt_cd=entry["fin_prdt_cd"]
            )
            # DepositOption 모델 필드에 맞게 API 응답 필드 매핑
            option_data = {
                "intr_rate_type": entry.get("intr_rate_type"),
                "intr_rate_type_nm": entry.get("intr_rate_type_nm"),
                "save_trm": entry.get("save_trm"),
                "intr_rate": entry.get("intr_rate"),
                "intr_rate2": entry.get("intr_rate2"),
            }
            # 숫자형 필드, 필수 필드에 대한 유효성 검사 및 형 변환 강화 권장
            # 예를 들어, intr_rate, intr_rate2가 null일 경우 Decimal로 변환 시 오류 방지
            for key in ["intr_rate", "intr_rate2"]:
                if option_data[key] is None:
                    option_data[key] = None  # 또는 Decimal('0.00') 등 기본값

            DepositOption.objects.update_or_create(
                product=parent_product,
                intr_rate_type=option_data["intr_rate_type"],
                save_trm=option_data["save_trm"],
                defaults=option_data,
            )
        except DepositProduct.DoesNotExist:
            continue  # 해당 상품이 없으면 옵션 저장 건너뛰기
        except Exception as e:
            continue


@api_view(["GET"])
def save_saving_products(request):
    """
    금융위원회 API에서 적금 상품 정보를 가져와서 데이터베이스에 저장하는 함수
    """
    api_url = f"http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={FIN_API_KEY}&topFinGrpNo=020000&pageNo=1"
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        data = response.json()

        if "result" not in data:
            return Response(
                {"error": "Invalid API response format from savingProductsSearch"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        base_list = data.get("result", {}).get("baseList", [])
        option_list = data.get("result", {}).get("optionList", [])

        if not base_list:
            return Response(
                {"error": "No base data available for saving products"},
                status=status.HTTP_404_NOT_FOUND,
            )
        # 옵션 리스트는 비어있을 수도 있음 (상품은 있으나 옵션 정보가 없는 경우)

        save_saving_data(base_list, option_list)

        return Response(
            {"message": "적금 상품 정보 저장 성공"}, status=status.HTTP_200_OK
        )
    except requests.exceptions.RequestException as e:
        return Response(
            {"error": f"Failed to fetch saving products data from API: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    except Exception as e:
        return Response(
            {
                "error": f"An unexpected error occurred while saving saving products: {str(e)}"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


def save_saving_data(base_list, option_list):
    """
    API에서 받아온 적금 상품 정보를 데이터베이스에 저장하는 함수
    """
    for entry in base_list:
        product_data = {
            "kor_co_nm": entry.get("kor_co_nm"),
            "fin_prdt_nm": entry.get("fin_prdt_nm"),
            "join_way": entry.get("join_way"),
            "mtrt_int": entry.get("mtrt_int"),
            "spcl_cnd": entry.get("spcl_cnd"),
            "join_deny": entry.get("join_deny"),
            "join_member": entry.get("join_member"),
            "etc_note": entry.get("etc_note"),
            "max_limit": entry.get("max_limit"),
            "dcls_strt_day": entry.get("dcls_strt_day"),
            "dcls_end_day": entry.get("dcls_end_day"),
            "fin_co_subm_day": entry.get("fin_co_subm_day"),
            # 적금 특화 필드 추가
            "rsrv_type": entry.get("rsrv_type"),
            "rsrv_type_nm": entry.get("rsrv_type_nm"),
        }
        SavingProduct.objects.update_or_create(
            fin_prdt_cd=entry["fin_prdt_cd"],
            defaults=product_data,
        )

    for entry in option_list:
        try:
            parent_product = SavingProduct.objects.get(fin_prdt_cd=entry["fin_prdt_cd"])
            option_data = {
                "intr_rate_type": entry.get("intr_rate_type"),
                "intr_rate_type_nm": entry.get("intr_rate_type_nm"),
                "save_trm": entry.get("save_trm"),
                "intr_rate": entry.get("intr_rate"),
                "intr_rate2": entry.get("intr_rate2"),
                # 적금 옵션 특화 필드 추가
                "acc_type_nm": entry.get("acc_type_nm"),
            }
            for key in ["intr_rate", "intr_rate2"]:
                if option_data[key] is None:
                    option_data[key] = None

            SavingOption.objects.update_or_create(
                product=parent_product,
                intr_rate_type=option_data["intr_rate_type"],
                save_trm=option_data["save_trm"],
                defaults=option_data,
            )
        except SavingProduct.DoesNotExist:
            # 로깅 권장: print(f"Warning: Saving product with code {entry['fin_prdt_cd']} not found for option. Skipping option.")
            continue
        except Exception as e:
            # 로깅 권장: print(f"Error saving saving option for product {entry['fin_prdt_cd']}: {str(e)}")
            continue

# 사용자가 특정 예금 상품에 가입
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def deposit_product_subscribe(request, fin_prdt_cd):
    product = get_object_or_404(DepositProduct, fin_prdt_cd=fin_prdt_cd)
    user = request.user

    subscription, created = DepositSubscription.objects.get_or_create(
        user=user, deposit_product=product
    )

    if created:
        return Response(
            {"message": f"'{product.fin_prdt_nm}' 상품에 가입되었습니다."},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(
            {"message": f"이미 '{product.fin_prdt_nm}' 상품에 가입되어 있습니다."},
            status=status.HTTP_200_OK,
        )

# 사용자가 특정 적금 상품에 가입

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def saving_product_subscribe(request, fin_prdt_cd):
    product = get_object_or_404(SavingProduct, fin_prdt_cd=fin_prdt_cd)
    user = request.user

    subscription, created = SavingSubscription.objects.get_or_create(
        user=user, saving_product=product
    )

    if created:
        return Response(
            {"message": f"'{product.fin_prdt_nm}' 상품에 가입되었습니다."},
            status=status.HTTP_201_CREATED,
        )
    else:
        return Response(
            {"message": f"이미 '{product.fin_prdt_nm}' 상품에 가입되어 있습니다."},
            status=status.HTTP_200_OK,
        )


# 가입한 상품 목록 조회 API (FBV)도 여기에 추가될 예정


# 현재 로그인한 사용자가 가입한 예금 상품 목록을 조회
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscribed_deposit_products_list(request):
    user = request.user
    subscriptions = DepositSubscription.objects.filter(user=user)
    subscribed_products = [sub.deposit_product for sub in subscriptions]
    serializer = DepositProductSerializer(subscribed_products, many=True)
    return Response(serializer.data)


# 현재 로그인한 사용자가 가입한 적금 상품 목록을 조회
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def subscribed_saving_products_list(request):
    user = request.user
    subscriptions = SavingSubscription.objects.filter(user=user)
    subscribed_products = [sub.saving_product for sub in subscriptions]
    serializer = SavingProductSerializer(subscribed_products, many=True)
    return Response(serializer.data)


# 예금 상품 목록 및 상세 조회
class DepositProductListAPIView(generics.ListAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
    permission_classes = [AllowAny]  # 모든 유저에게 조회 기능 제공


class DepositProductDetailAPIView(generics.RetrieveAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
    lookup_field = "fin_prdt_cd"  # URL에서 상품 코드로 조회
    permission_classes = [AllowAny]  # 모든 유저에게 조회 기능 제공


# 적금 상품 목록 및 상세 조회
class SavingProductListAPIView(generics.ListAPIView):
    queryset = SavingProduct.objects.all()
    serializer_class = SavingProductSerializer
    permission_classes = [AllowAny]  # 모든 유저에게 조회 기능 제공


class SavingProductDetailAPIView(generics.RetrieveAPIView):
    queryset = SavingProduct.objects.all()
    serializer_class = SavingProductSerializer
    lookup_field = "fin_prdt_cd"  # URL에서 상품 코드로 조회
    permission_classes = [AllowAny]  # 모든 유저에게 조회 기능 제공


