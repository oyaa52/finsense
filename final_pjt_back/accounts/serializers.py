from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from products.models import DepositProduct  # 실제 모델 import 필요

class CustomRegisterSerializer(RegisterSerializer):
    subscribed_products = serializers.PrimaryKeyRelatedField(
        queryset=DepositProduct.objects.all(),
        many=True,
        required=False
    )

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['subscribed_products'] = self.validated_data.get('subscribed_products', [])
        return data

    def save(self, request):
        user = super().save(request)
        subscribed_products = self.validated_data.get('subscribed_products', [])
        user.save()
        user.subscribed_products.set(subscribed_products)  # ManyToManyField 관계 설정
        return user