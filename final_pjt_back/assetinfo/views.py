from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import AssetPrice  # models.py에 AssetPrice 모델이 정의되어 있어야 합니다.
from .serializers import (
    AssetPriceSerializer,
)  # serializers.py에 AssetPriceSerializer가 정의되어 있어야 합니다.
from datetime import datetime


# --- API View to serve data for Chart.js ---
@api_view(["GET"])
def asset_prices_for_chart(request):
    """
    Chart.js에서 사용할 자산 가격 데이터를 제공합니다.
    URL 파라미터로 'asset_name' (Gold 또는 Silver)을 받습니다.
    """
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
    """
    자산 가격 정보 목록을 제공하는 API 뷰입니다.
    Query Parameters를 통해 필터링 기능을 제공합니다:
    - asset_name: 'Gold' 또는 'Silver' (필수)
    - start_date: YYYY-MM-DD 형식의 시작 날짜 (선택)
    - end_date: YYYY-MM-DD 형식의 종료 날짜 (선택)
    """

    serializer_class = AssetPriceSerializer

    def get_queryset(self):
        queryset = AssetPrice.objects.all()
        asset_name = self.request.query_params.get("asset_name", None)
        start_date_str = self.request.query_params.get("start_date", None)
        end_date_str = self.request.query_params.get("end_date", None)

        if not asset_name:
            # asset_name이 제공되지 않으면 빈 쿼리셋 반환 또는 에러 처리
            # 명세서상 금/은 선택 버튼이 있으므로 asset_name은 필수적으로 받는 것이 좋아보임.
            # 여기서는 빈 쿼리셋을 반환하도록 처리 (또는 에러 응답을 보내도 됨)
            return AssetPrice.objects.none()

        queryset = queryset.filter(
            asset_name__iexact=asset_name
        )  # 대소문자 구분 없이 필터링

        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                # 날짜 형식이 잘못된 경우 일단 무시하거나 에러 처리 가능
                pass  # 또는 raise serializers.ValidationError({'start_date': 'Invalid date format. Use YYYY-MM-DD.'})

        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                # 날짜 형식이 잘못된 경우 일단 무시하거나 에러 처리 가능
                pass  # 또는 raise serializers.ValidationError({'end_date': 'Invalid date format. Use YYYY-MM-DD.'})

        return queryset

    def list(self, request, *args, **kwargs):
        asset_name = request.query_params.get("asset_name", None)
        if not asset_name:
            return Response(
                {
                    "error": "asset_name query parameter is required. (e.g., Gold or Silver)"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.get_queryset()
        if (
            not queryset.exists()
            and AssetPrice.objects.filter(asset_name__iexact=asset_name).exists()
        ):
            # asset_name은 맞지만 해당 기간 데이터가 없는 경우
            # 명세서의 "잘못된 날짜 선택 시 적절한 문구 출력"에 해당될 수 있도록 빈 리스트 반환
            # 또는 특정 메시지와 함께 200 OK 반환
            pass  # 그냥 serializer.data가 빈 리스트가 되도록 둠

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
