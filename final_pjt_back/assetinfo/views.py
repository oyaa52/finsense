from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import AssetPrice
from .serializers import AssetPriceSerializer
from datetime import datetime, timedelta
import requests # 외부 API 호출을 위해 추가

@api_view(["GET"])
def asset_prices_for_chart(request):
    asset_name_filter = request.GET.get("asset_name")
    if not asset_name_filter:
        return Response(
            {"error": "asset_name parameter is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    prices_queryset = AssetPrice.objects.filter(
        asset_name__iexact=asset_name_filter
    ).order_by("date")
    if not prices_queryset.exists():
        return Response(
            {"error": f"No data found for asset: {asset_name_filter}"},
            status=status.HTTP_404_NOT_FOUND,
        )
    serializer = AssetPriceSerializer(prices_queryset, many=True)
    labels = [item["date"] for item in serializer.data]
    data_points = [item["price"] for item in serializer.data]
    chart_data_response = {
        "labels": labels,
        "datasets": [
            {
                "label": f"{asset_name_filter.capitalize()} Price (Close/Last)",
                "data": data_points,
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
                "tension": 0.1,
                "fill": True,
            }
        ],
    }
    return Response(chart_data_response, status=status.HTTP_200_OK)

class AssetPriceListAPIView(generics.ListAPIView):
    serializer_class = AssetPriceSerializer
    def get_queryset(self):
        queryset = AssetPrice.objects.all()
        asset_name = self.request.query_params.get("asset_name", None)
        start_date_str = self.request.query_params.get("start_date", None)
        end_date_str = self.request.query_params.get("end_date", None)

        if not asset_name:
            return AssetPrice.objects.none()

        queryset = queryset.filter(asset_name__iexact=asset_name)

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        return queryset.order_by('date')

    def list(self, request, *args, **kwargs):
        asset_name = request.query_params.get("asset_name", None)
        if not asset_name:
            return Response(
                {"error": "asset_name query parameter is required. (e.g., Gold or Silver)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

@api_view(["GET"])
def get_koreaexgold_prices(request):
    """
    한국금거래소 API에서 금/은 시세를 가져옵니다.
    type (Au 또는 Ag), from (YYYY-MM-DD), to (YYYY-MM-DD) 파라미터를 사용합니다.
    """
    api_type = request.GET.get("type")  # Au 또는 Ag
    date_from_str = request.GET.get("from")
    date_to_str = request.GET.get("to")

    if not all([api_type, date_from_str, date_to_str]):
        return Response(
            {"error": "type, from, to 파라미터가 모두 필요합니다."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # 파라미터 검증 (type은 Au 또는 Ag, 날짜 형식은 YYYY-MM-DD)
    if api_type.upper() not in ["AU", "AG"]:
        return Response(
            {"error": "type 파라미터는 'Au' 또는 'Ag' 여야 합니다."},
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
        response = requests.get(API_URL, params=params, timeout=10) # timeout 설정
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        external_data = response.json()

        if not external_data.get("success"):
            return Response(
                {"error": f"외부 API 오류: {external_data.get('message', '알 수 없는 오류')}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 프론트엔드 차트 형식에 맞게 데이터 가공
        # 여기서는 domesticPriceDon을 사용 (그램당 가격은 domesticPrice)
        labels = [item["date"] for item in external_data.get("data", [])]
        data_points = [item["domesticPriceDon"] for item in external_data.get("data", [])]
        
        asset_name_display = "금 (Gold)" if api_type.upper() == "AU" else "은 (Silver)"
        border_color = ("rgb(255, 215, 0)" if api_type.upper() == "AU" else "rgb(192, 192, 192)")
        bg_color = ("rgba(255, 215, 0, 0.1)" if api_type.upper() == "AU" else "rgba(192, 192, 192, 0.1)")

        chart_data_response = {
            "labels": labels,
            "datasets": [
                {
                    "label": f"{asset_name_display} 시세 (돈)",
                    "data": data_points,
                    "borderColor": border_color,
                    "backgroundColor": bg_color,
                    "tension": 0.1,
                    "fill": True,
                }
            ],
        }
        return Response(chart_data_response, status=status.HTTP_200_OK)

    except requests.exceptions.RequestException as e:
        return Response(
            {"error": f"외부 API 호출 중 오류 발생: {str(e)}"},
            status=status.HTTP_502_BAD_GATEWAY,
        )
    except ValueError: # response.json() 실패 시
        return Response(
            {"error": "외부 API 응답을 파싱하는 중 오류 발생 (JSON 형식 오류)."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) 