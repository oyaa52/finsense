from rest_framework import serializers
from .models import MarketIndex

class MarketIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketIndex
        fields = ['name', 'value', 'change', 'rate', 'last_updated'] 