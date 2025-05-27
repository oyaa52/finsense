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
    # 현재 사용자의 해당 상품 구독 여부를 반환하는 필드 추가
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = DepositProduct
        fields = "__all__"  # 모든 필드를 포함하고, options 필드를 통해 관련 옵션들을 함께 보여줌

    def get_is_subscribed(self, obj):
        # 시리얼라이저가 호출될 때 context에서 request 객체를 가져옴
        request = self.context.get('request')
        # request가 있고, 사용자가 인증된 경우에만 구독 여부 확인
        if request and hasattr(request, "user") and request.user.is_authenticated:
            # obj는 현재 DepositProduct 인스턴스
            return DepositSubscription.objects.filter(user=request.user, product=obj).exists()
        return False # 사용자가 인증되지 않았거나 request 객체가 없으면 False 반환


class SavingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOption
        fields = "__all__"
        read_only_fields = ("product",)


class SavingProductSerializer(serializers.ModelSerializer):
    options = SavingOptionSerializer(many=True, read_only=True)  # 중첩 시리얼라이저
    # 현재 사용자의 해당 상품 구독 여부를 반환하는 필드 추가
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = SavingProduct
        fields = "__all__"

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, "user") and request.user.is_authenticated:
            # obj는 현재 SavingProduct 인스턴스
            return SavingSubscription.objects.filter(user=request.user, product=obj).exists()
        return False


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
