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
    DepositSubscriptionSerializer,
    SavingSubscriptionSerializer,
)
import requests
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, FloatField
from django.db.models.functions import Cast
from rest_framework.filters import OrderingFilter
from django.db.models import F, ExpressionWrapper, Max

# 금융위원회 API 키 설정
FIN_API_KEY = settings.FIN_API_KEY


@api_view(["GET"])
@permission_classes([AllowAny])  # 인증 제외
def save_deposit_products(request):
    """
    금융위원회 API에서 예금 상품 정보를 가져와서 데이터베이스에 저장하는 함수
    """
    try:
        base_lst = []
        option_lst = []
        
        # 4페이지까지의 데이터를 가져옴
        for page_no in range(1, 5):  # 1~4 페이지까지 가져오기
            # 금융위원회 API 호출
            r = requests.get(
                f"http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={FIN_API_KEY}&topFinGrpNo=020000&pageNo={page_no}"
            )
            response = r.json()

            if "result" not in response:
                continue

            page_base_lst = response.get("result", {}).get("baseList", [])
            page_option_lst = response.get("result", {}).get("optionList", [])

            if page_base_lst and page_option_lst:
                base_lst.extend(page_base_lst)
                option_lst.extend(page_option_lst)

        if not base_lst or not option_lst:
            return Response(
                {"error": "No data available"}, status=status.HTTP_404_NOT_FOUND
            )

        result = save_deposit_data(base_lst, option_lst)

        return Response(
            {
                "message": f"예금 상품 정보 저장 성공",
                "details": {
                    "total_products": len(base_lst),
                    "new_products": result["new_products"],
                    "updated_products": result["updated_products"]
                }
            }, 
            status=status.HTTP_200_OK
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
    # 기존 상품 코드 목록 가져오기
    existing_product_codes = set(DepositProduct.objects.values_list('fin_prdt_cd', flat=True))
    
    # 새로운 상품 개수 카운트
    new_products_count = 0
    updated_products_count = 0
    
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
        
        # 상품 코드가 이미 존재하는지 확인
        is_new = entry["fin_prdt_cd"] not in existing_product_codes
        
        # 상품 생성 또는 업데이트
        product, created = DepositProduct.objects.update_or_create(
            fin_prdt_cd=entry["fin_prdt_cd"],
            defaults=product_data,
        )
        
        if created:
            new_products_count += 1
        else:
            updated_products_count += 1

    # 옵션 데이터 처리
    for entry in option_lst:
        try:
            parent_product = DepositProduct.objects.get(fin_prdt_cd=entry["fin_prdt_cd"])
            # DepositOption 모델 필드에 맞게 API 응답 필드 매핑
            option_data = {
                "intr_rate_type": entry.get("intr_rate_type"),
                "intr_rate_type_nm": entry.get("intr_rate_type_nm"),
                "save_trm": entry.get("save_trm"),
                "intr_rate": entry.get("intr_rate"),
                "intr_rate2": entry.get("intr_rate2"),
            }
            # 숫자형 필드, 필수 필드에 대한 유효성 검사 및 형 변환 강화
            for key in ["intr_rate", "intr_rate2"]:
                if option_data[key] is None:
                    option_data[key] = 0.0  # None 대신 0.0으로 설정
                else:
                    try:
                        option_data[key] = float(option_data[key])
                    except (ValueError, TypeError):
                        option_data[key] = 0.0

            DepositOption.objects.update_or_create(
                product=parent_product,
                intr_rate_type=option_data["intr_rate_type"],
                save_trm=option_data["save_trm"],
                defaults=option_data,
            )
        except DepositProduct.DoesNotExist:
            print(f"Warning: Product with code {entry['fin_prdt_cd']} not found for option")
            continue
        except Exception as e:
            print(f"Error saving option for product {entry['fin_prdt_cd']}: {str(e)}")
            continue
    
    return {
        "new_products": new_products_count,
        "updated_products": updated_products_count
    }


@api_view(["GET"])
@permission_classes([AllowAny])  # 인증 제외
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
    try:
        product = get_object_or_404(DepositProduct, fin_prdt_cd=fin_prdt_cd)
        user = request.user
        amount = request.data.get('amount', 0)

        # 상품의 첫 번째 옵션을 가져옴
        first_option = product.options.first()
        if not first_option:
            return Response(
                {"error": "상품 옵션을 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = DepositSubscription.objects.get_or_create(
            user=user,
            product=product,
            option=first_option,
            defaults={'amount': amount}
        )

        if created:
            return Response(
                {"message": f"'{product.fin_prdt_nm}' 상품에 가입되었습니다."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": f"이미 '{product.fin_prdt_nm}' 상품에 가입되어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        print(f"Subscription error: {str(e)}")  # 서버 로그에 에러 출력
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# 사용자가 특정 적금 상품에 가입
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def saving_product_subscribe(request, fin_prdt_cd):
    try:
        product = get_object_or_404(SavingProduct, fin_prdt_cd=fin_prdt_cd)
        user = request.user
        amount = request.data.get('amount', 0)

        subscription, created = SavingSubscription.objects.get_or_create(
            user=user,
            product=product,
            defaults={'amount': amount}
        )

        if created:
            return Response(
                {"message": f"'{product.fin_prdt_nm}' 상품에 가입되었습니다."},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": f"이미 '{product.fin_prdt_nm}' 상품에 가입되어 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number
        })

# 예금 상품 목록 및 상세 조회
class DepositProductListAPIView(generics.ListAPIView):
    serializer_class = DepositProductSerializer
    permission_classes = [AllowAny]  # 인증 제외
    pagination_class = StandardResultsSetPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['fin_prdt_nm', 'options__intr_rate']

    def get_queryset(self):
        queryset = DepositProduct.objects.all()
        
        # 은행 필터링
        bank_id = self.request.query_params.get('bank_id')
        if bank_id:
            bank_map = {
                '2': '국민은행',
                '3': '신한은행',
                '4': '우리은행',
                '5': '하나은행',
                '6': '농협은행'
            }
            bank_name = bank_map.get(bank_id)
            if bank_name:
                queryset = queryset.filter(kor_co_nm__icontains=bank_name)  # 부분 일치로 변경
        
        # 기간 필터링 (period가 'all'이거나 없을 때는 모든 기간의 상품을 보여줌)
        period = self.request.query_params.get('period')
        if period and period != 'all':
            period_map = {
                '6': '6',
                '12': '12',
                '24': '24',
                '36': '36'
            }
            period_value = period_map.get(period)
            if period_value:
                queryset = queryset.filter(options__save_trm=period_value)
        
        # 정렬
        sort_by = self.request.query_params.get('sort_by')
        if sort_by == 'rate':
            # 금리를 숫자로 변환하여 정렬
            from django.db.models import F, ExpressionWrapper, FloatField
            queryset = queryset.annotate(
                rate_value=Cast('options__intr_rate', FloatField())
            ).order_by(
                F('rate_value').desc(nulls_last=True),
                'kor_co_nm'
            )
        else:
            queryset = queryset.order_by('kor_co_nm')
        
        # SQLite에서 작동하는 방식으로 중복 제거
        return queryset.distinct()


class DepositProductDetailAPIView(generics.RetrieveAPIView):
    queryset = DepositProduct.objects.all()
    serializer_class = DepositProductSerializer
    lookup_field = "fin_prdt_cd"  # URL에서 상품 코드로 조회
    permission_classes = [AllowAny]  # 모든 유저에게 조회 기능 제공


# 적금 상품 목록 및 상세 조회
class SavingProductListAPIView(generics.ListAPIView):
    queryset = SavingProduct.objects.all()
    serializer_class = SavingProductSerializer
    permission_classes = [AllowAny]  # 인증 제외
    pagination_class = StandardResultsSetPagination


class SavingProductDetailAPIView(generics.RetrieveAPIView):
    queryset = SavingProduct.objects.all()
    serializer_class = SavingProductSerializer
    lookup_field = "fin_prdt_cd"  # URL에서 상품 코드로 조회
    permission_classes = [AllowAny]  # 모든 유저에게 조회 기능 제공


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_deposit(request, product_id, option_id):
    try:
        product = DepositProduct.objects.get(fin_prdt_cd=product_id)
        option = DepositOption.objects.get(id=option_id, product=product)
        amount = request.data.get('amount', 0)

        subscription, created = DepositSubscription.objects.get_or_create(
            user=request.user,
            product=product,
            option=option,
            defaults={'amount': amount}
        )

        if not created:
            return Response(
                {'message': '이미 가입한 상품입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = DepositSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except DepositProduct.DoesNotExist:
        return Response(
            {'error': '상품을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except DepositOption.DoesNotExist:
        return Response(
            {'error': '상품 옵션을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_saving(request, product_id, option_id):
    try:
        product = SavingProduct.objects.get(fin_prdt_cd=product_id)
        option = SavingOption.objects.get(id=option_id, product=product)
        amount = request.data.get('amount', 0)

        subscription, created = SavingSubscription.objects.get_or_create(
            user=request.user,
            product=product,
            option=option,
            defaults={'amount': amount}
        )

        if not created:
            return Response(
                {'message': '이미 가입한 상품입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SavingSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except SavingProduct.DoesNotExist:
        return Response(
            {'error': '상품을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )
    except SavingOption.DoesNotExist:
        return Response(
            {'error': '상품 옵션을 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_subscriptions(request):
    deposit_subscriptions = DepositSubscription.objects.filter(user=request.user)
    saving_subscriptions = SavingSubscription.objects.filter(user=request.user)

    deposit_serializer = DepositSubscriptionSerializer(deposit_subscriptions, many=True)
    saving_serializer = SavingSubscriptionSerializer(saving_subscriptions, many=True)

    return Response({
        'deposit_subscriptions': deposit_serializer.data,
        'saving_subscriptions': saving_serializer.data
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_subscriptions(request):
    try:
        user = request.user
        
        # 예금 상품 구독 조회
        deposit_subscriptions = DepositSubscription.objects.filter(user=user).select_related(
            'product', 'option'
        ).values(
            'id',
            'subscribed_at',
            product_name=F('product__fin_prdt_nm'),
            bank_name=F('product__kor_co_nm'),
            interest_rate=F('option__intr_rate'),
            period=F('option__save_trm')
        )
        
        # 적금 상품 구독 조회
        saving_subscriptions = SavingSubscription.objects.filter(user=user).select_related(
            'product', 'option'
        ).values(
            'id',
            'subscribed_at',
            product_name=F('product__fin_prdt_nm'),
            bank_name=F('product__kor_co_nm'),
            interest_rate=F('option__intr_rate'),
            period=F('option__save_trm')
        )
        
        return Response({
            'deposit_subscriptions': list(deposit_subscriptions),
            'saving_subscriptions': list(saving_subscriptions)
        })
    except Exception as e:
        print(f"Error in get_user_subscriptions: {str(e)}")
        return Response(
            {'error': '구독 정보를 가져오는 중 오류가 발생했습니다.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


