from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import AssetPrice
from .serializers import AssetPriceSerializer
from datetime import datetime, timedelta
import requests # 외부 API 호출을 위해 추가

# 특정 자산(asset_name)의 가격 정보를 차트용으로 가공하여 반환
# GET /api/assetinfo/chart-prices/?asset_name=<asset_name>
@api_view(["GET"])
def asset_prices_for_chart(request):
    asset_name_filter = request.GET.get("asset_name")
    if not asset_name_filter:
        return Response(
            {"error": "필수 파라미터 'asset_name'이 누락되었습니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    # asset_name으로 필터링하고 날짜순으로 정렬
    prices_queryset = AssetPrice.objects.filter(
        asset_name__iexact=asset_name_filter
    ).order_by("date")
    
    if not prices_queryset.exists():
        return Response(
            {"error": f"'{asset_name_filter}'에 대한 데이터를 찾을 수 없습니다."},
            status=status.HTTP_404_NOT_FOUND,
        )
        
    serializer = AssetPriceSerializer(prices_queryset, many=True)
    
    # Chart.js 형식에 맞게 데이터 재구성
    labels = [item["date"] for item in serializer.data] # 날짜 리스트 (x축)
    data_points = [item["price"] for item in serializer.data] # 가격 리스트 (y축)
    
    chart_data_response = {
        "labels": labels,
        "datasets": [
            {
                "label": f"{asset_name_filter.capitalize()} 가격 (종가/최종가)", # 자산명 첫 글자 대문자
                "data": data_points,
                # 자산명에 따라 차트 색상 동적 설정
                "borderColor": (
                    "rgb(255, 215, 0)"
                    if asset_name_filter.lower() == "gold"
                    else "rgb(192, 192, 192)"
                ),
                "backgroundColor": (
                    "rgba(255, 215, 0, 0.1)"
                    if asset_name_filter.lower() == "gold"
                    else "rgba(192, 192, 192, 0.1)"
                ),
                "tension": 0.1, # 선 곡률
                "fill": True, # 영역 채우기
            }
        ],
    }
    return Response(chart_data_response, status=status.HTTP_200_OK)

# 자산 가격 목록 조회 API (필터링 지원)
# GET /api/assetinfo/prices/?asset_name=<name>&start_date=<YYYY-MM-DD>&end_date=<YYYY-MM-DD>
class AssetPriceListAPIView(generics.ListAPIView):
    serializer_class = AssetPriceSerializer
    
    def get_queryset(self):
        queryset = AssetPrice.objects.all()
        asset_name = self.request.query_params.get("asset_name", None) # 자산명 필터
        start_date_str = self.request.query_params.get("start_date", None) # 시작일 필터
        end_date_str = self.request.query_params.get("end_date", None) # 종료일 필터

        if not asset_name: # 자산명 없으면 빈 쿼리셋 반환
            return AssetPrice.objects.none()

        queryset = queryset.filter(asset_name__iexact=asset_name) # 대소문자 무관 자산명 필터링

        # 시작일 필터링
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError: # 날짜 형식 오류 시 무시
                pass

        # 종료일 필터링
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError: # 날짜 형식 오류 시 무시
                pass
        return queryset.order_by('date') # 날짜순 정렬

    def list(self, request, *args, **kwargs):
        asset_name = request.query_params.get("asset_name", None)
        if not asset_name:
            return Response(
                {"error": "필수 쿼리 파라미터 'asset_name'이 누락되었습니다. (예: Gold 또는 Silver)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

# 한국금거래소 API를 통해 금/은 시세를 가져와 차트용으로 반환
# GET /api/assetinfo/koreaexgold/?type=<Au|Ag>&from=<YYYY-MM-DD>&to=<YYYY-MM-DD>
@api_view(["GET"])
def get_koreaexgold_prices(request):
    api_type = request.GET.get("type")  # Au (금) 또는 Ag (은)
    date_from_str = request.GET.get("from") # 조회 시작일
    date_to_str = request.GET.get("to") # 조회 종료일

    # 필수 파라미터 검증
    if not all([api_type, date_from_str, date_to_str]):
        return Response(
            {"error": "필수 파라미터 'type', 'from', 'to'가 모두 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 파라미터 유효성 검증
    if api_type.upper() not in ["AU", "AG"]:
        return Response(
            {"error": "'type' 파라미터는 'Au' 또는 'Ag' 여야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        datetime.strptime(date_from_str, "%Y-%m-%d")
        datetime.strptime(date_to_str, "%Y-%m-%d")
    except ValueError:
        return Response(
            {"error": "날짜 파라미터는 'YYYY-MM-DD' 형식이어야 합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    API_URL = "https://prod-api.exgold.co.kr/api/v1/main/chart/period/price/domestic"
    params = {
        "type": api_type.upper(),
        "from": date_from_str,
        "to": date_to_str,
    }

    try:
        # 외부 API 호출 (timeout 10초 설정)
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()  # HTTP 오류 시 예외 발생 (4xx, 5xx)
        external_data = response.json()

        # 외부 API 응답 성공 여부 확인
        if not external_data.get("success"):
            return Response(
                {"error": f"외부 API 처리 실패: {external_data.get('message', '알 수 없는 오류')}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR, # API 내부 오류일 수 있으므로 500 사용
            )

        # 차트 데이터 형식으로 가공 (한국금거래소는 돈 단위 가격 사용)
        labels = [item["date"] for item in external_data.get("data", [])]
        data_points = [item["domesticPriceDon"] for item in external_data.get("data", [])]
        
        asset_name_display = "금 (Gold)" if api_type.upper() == "AU" else "은 (Silver)"
        border_color = ("rgb(255, 215, 0)" if api_type.upper() == "AU" else "rgb(192, 192, 192)")
        bg_color = ("rgba(255, 215, 0, 0.1)" if api_type.upper() == "AU" else "rgba(192, 192, 192, 0.1)")

        chart_data_response = {
            "labels": labels,
            "datasets": [
                {
                    "label": f"{asset_name_display} 시세 (1돈)", # 단위 명시
                    "data": data_points,
                    "borderColor": border_color,
                    "backgroundColor": bg_color,
                    "tension": 0.1,
                    "fill": True,
                }
            ],
        }
        return Response(chart_data_response, status=status.HTTP_200_OK)

    except requests.exceptions.Timeout:
        return Response(
            {"error": "외부 API 호출 시간 초과 (Timeout)."},
            status=status.HTTP_504_GATEWAY_TIMEOUT,
        )
    except requests.exceptions.RequestException as e:
        # 그 외 requests 관련 예외 (연결 오류 등)
        return Response(
            {"error": f"외부 API 호출 중 오류 발생: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY, # 게이트웨이 오류로 처리
        )
    except ValueError: # JSON 디코딩 실패
        return Response(
            {"error": "외부 API 응답을 처리하는 중 오류 발생 (잘못된 JSON 형식)."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 