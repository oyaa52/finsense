from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, generics
from .models import AssetPrice
from .serializers import AssetPriceSerializer
from datetime import datetime

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