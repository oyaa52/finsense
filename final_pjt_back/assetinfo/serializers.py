# final-pjt/final_pjt_back/assetinfo/serializers.py
from rest_framework import serializers
from .models import AssetPrice # AssetPrice 모델 임포트

# 자산 가격(AssetPrice) 정보 시리얼라이저
class AssetPriceSerializer(serializers.ModelSerializer):
    # Chart.js 등에서 사용될 'date'와 'price' 필드만 직렬화
    class Meta:
        model = AssetPrice
        fields = ['date', 'price'] # API를 통해 노출할 필드 목록
        # 만약 다른 필드(예: open_price, high_price, low_price, volume)도 API를 통해
        # 전달하고 싶다면 fields 리스트에 추가하면 됩니다.
        # fields = ['date', 'price', 'open_price', 'high_price', 'low_price']