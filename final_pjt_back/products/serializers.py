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
        # product 필드는 역참조되므로 제외 또는 읽기 전용 설정 가능
        # 여기서는 모든 필드 포함, 필요시 fields 조정
        fields = "__all__"
        read_only_fields = ("product",)


class DepositProductSerializer(serializers.ModelSerializer):
    options = DepositOptionSerializer(many=True, read_only=True)  # 옵션 정보 중첩
    is_subscribed = serializers.SerializerMethodField() # 현재 사용자의 상품 구독 여부

    class Meta:
        model = DepositProduct
        fields = "__all__"  # 모든 필드 포함, options 통해 관련 옵션 표시

    def get_is_subscribed(self, obj):
        # context에서 request 객체 가져오기
        request = self.context.get('request')
        # 사용자가 인증된 경우 구독 여부 확인
        if request and hasattr(request, "user") and request.user.is_authenticated:
            # obj: 현재 DepositProduct 인스턴스
            return DepositSubscription.objects.filter(user=request.user, product=obj).exists()
        return False # 미인증 또는 request 객체 없으면 False


class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = "__all__"
        read_only_fields = ("product",)


class SavingProductSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)  # 옵션 정보 중첩
    is_subscribed = serializers.SerializerMethodField() # 현재 사용자의 상품 구독 여부

    class Meta:
        model = SavingProduct
        fields = "__all__"

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            # obj: 현재 SavingProduct 인스턴스
            return SavingSubscription.objects.filter(user=request.user, product=obj).exists()
        return False


class DepositSubscriptionSerializer(serializers.ModelSerializer):
    # 상품 및 옵션 정보 source 통해 접근
    product_name = serializers.CharField(source='product.fin_prdt_nm', read_only=True)
    bank_name = serializers.CharField(source='product.kor_co_nm', read_only=True)
    interest_rate = serializers.DecimalField(source='option.intr_rate', max_digits=5, decimal_places=2, read_only=True)
    period = serializers.CharField(source='option.save_trm', read_only=True)

    class Meta:
        model = DepositSubscription
        fields = ['id', 'product_name', 'bank_name', 'interest_rate', 'period', 'amount', 'subscribed_at']
        read_only_fields = ['subscribed_at']


class SavingSubscriptionSerializer(serializers.ModelSerializer):
    # 상품 및 옵션 정보 source 통해 접근
    product_name = serializers.CharField(source='product.fin_prdt_nm', read_only=True)
    bank_name = serializers.CharField(source='product.kor_co_nm', read_only=True)
    interest_rate = serializers.DecimalField(source='option.intr_rate', max_digits=5, decimal_places=2, read_only=True)
    period = serializers.CharField(source='option.save_trm', read_only=True)

    class Meta:
        model = SavingSubscription
        fields = ['id', 'product_name', 'bank_name', 'interest_rate', 'period', 'amount', 'subscribed_at']
        read_only_fields = ['subscribed_at']
