from rest_framework import serializers
from .models import MarketIndex

# 시장 지수(MarketIndex) 정보 시리얼라이저
class MarketIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        # API를 통해 노출할 필드: 지수명, 현재가, 전일비, 등락률, 마지막 업데이트 일시
        fields = ['name', 'value', 'change', 'rate', 'last_updated'] 