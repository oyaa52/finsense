from rest_framework import serializers
from .models import DepositProduct, DepositOption

class DepositProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProduct
        fields = '__all__'

class DepositOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        fields = '__all__'

