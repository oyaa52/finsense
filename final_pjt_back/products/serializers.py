from rest_framework import serializers
from .models import (
    DepositProduct,
    DepositOption,
    SavingProduct,
    SavingOption,
    DepositSubscription,
    SavingSubscription,
)


class DepositOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOption
        # product 필드는 DepositProductSerializer에서 역참조하므로 여기서는 제외하거나 읽기 전용으로 설정 가능
        # 여기서는 모든 필드를 포함시키되, 상품 상세 조회 시 옵션만 필요하다면 fields 조정 가능
        fields = "__all__"
        read_only_fields = ("product",)


class DepositProductSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)  # 중첩 시리얼라이저

    class Meta:
        model = DepositProduct
        fields = "__all__"  # 모든 필드를 포함하고, options 필드를 통해 관련 옵션들을 함께 보여줌


class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = "__all__"
        read_only_fields = ("product",)


class SavingProductSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)  # 중첩 시리얼라이저

    class Meta:
        model = SavingProduct
        fields = "__all__"


class DepositSubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.fin_prdt_nm', read_only=True)
    bank_name = serializers.CharField(source='product.kor_co_nm', read_only=True)
    interest_rate = serializers.DecimalField(source='option.intr_rate', max_digits=5, decimal_places=2, read_only=True)
    period = serializers.CharField(source='option.save_trm', read_only=True)

    class Meta:
        model = DepositSubscription
        fields = ['id', 'product_name', 'bank_name', 'interest_rate', 'period', 'amount', 'subscribed_at']
        read_only_fields = ['subscribed_at']


class SavingSubscriptionSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.fin_prdt_nm', read_only=True)
    bank_name = serializers.CharField(source='product.kor_co_nm', read_only=True)
    interest_rate = serializers.DecimalField(source='option.intr_rate', max_digits=5, decimal_places=2, read_only=True)
    period = serializers.CharField(source='option.save_trm', read_only=True)

    class Meta:
        model = SavingSubscription
        fields = ['id', 'product_name', 'bank_name', 'interest_rate', 'period', 'amount', 'subscribed_at']
        read_only_fields = ['subscribed_at']
