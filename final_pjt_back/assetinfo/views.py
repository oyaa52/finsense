from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import AssetPrice # models.py에 AssetPrice 모델이 정의되어 있어야 합니다.
from .serializers import AssetPriceSerializer # serializers.py에 AssetPriceSerializer가 정의되어 있어야 합니다.


# --- API View to serve data for Chart.js ---
@api_view(['GET'])
def asset_prices_for_chart(request):
    """
    Chart.js에서 사용할 자산 가격 데이터를 제공합니다.
    URL 파라미터로 'asset_name' (Gold 또는 Silver)을 받습니다.
    """
    asset_name_filter = request.GET.get('asset_name') 
    
    if not asset_name_filter:
        return Response({'error': 'asset_name parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

    prices_queryset = AssetPrice.objects.filter(asset_name__iexact=asset_name_filter).order_by('date')
    
    if not prices_queryset.exists():
        return Response({'error': f'No data found for asset: {asset_name_filter}'}, status=status.HTTP_404_NOT_FOUND)

    serializer = AssetPriceSerializer(prices_queryset, many=True)
    
    labels = [item['date'] for item in serializer.data]
    data_points = [item['price'] for item in serializer.data]
    
    chart_data_response = {
        'labels': labels,
        'datasets': [
            {
                'label': f'{asset_name_filter.capitalize()} Price (Close/Last)',
                'data': data_points,
                'borderColor': 'rgb(255, 215, 0)' if asset_name_filter.lower() == 'gold' else 'rgb(192, 192, 192)',
                'backgroundColor': 'rgba(255, 215, 0, 0.1)' if asset_name_filter.lower() == 'gold' else 'rgba(192, 192, 192, 0.1)',
                'tension': 0.1,
                'fill': True,
            }
        ]
    }
    
    return Response(chart_data_response, status=status.HTTP_200_OK)