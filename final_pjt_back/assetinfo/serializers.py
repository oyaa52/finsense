# final-pjt/final_pjt_back/assetinfo/serializers.py
from rest_framework import serializers
from .models import AssetPrice # 같은 앱 내의 models.py에서 AssetPrice 모델을 가져옵니다.

class AssetPriceSerializer(serializers.ModelSerializer):
    """
    AssetPrice 모델 인스턴스를 JSON 형태로 변환하거나,
    JSON 형태의 데이터를 AssetPrice 모델 인스턴스로 변환하기 위한 Serializer입니다.
    """
    class Meta:
        model = AssetPrice
        # API를 통해 보여줄 필드를 지정합니다.
        # 여기서는 Chart.js에서 사용할 'date'와 'price'만 포함합니다.
        fields = ['date', 'price'] 
        # 만약 다른 필드(예: open_price, high_price, low_price, volume)도 API를 통해
        # 전달하고 싶다면 fields 리스트에 추가하면 됩니다.
        # 예: fields = ['date', 'price', 'open_price', 'high_price', 'low_price']