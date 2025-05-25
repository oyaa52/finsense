from django.db import models
from django.conf import settings


# 추상 기본 상품 클래스
class BaseProduct(models.Model):
    fin_prdt_cd = models.CharField(
        max_length=100, primary_key=True, help_text="금융상품 코드"
    )
    kor_co_nm = models.CharField(max_length=100, help_text="금융회사명")
    fin_prdt_nm = models.CharField(max_length=255, help_text="금융상품명")
    join_way = models.TextField(blank=True, null=True, help_text="가입 방법")
    mtrt_int = models.TextField(blank=True, null=True, help_text="만기 후 이자율 설명")
    spcl_cnd = models.TextField(blank=True, null=True, help_text="우대조건")
    join_deny = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="가입제한 (1:제한없음, 2:서민전용, 3:일부제한)",
    )
    join_member = models.TextField(blank=True, null=True, help_text="가입대상")
    etc_note = models.TextField(blank=True, null=True, help_text="기타 유의사항")
    max_limit = models.BigIntegerField(blank=True, null=True, help_text="최고한도")
    dcls_strt_day = models.CharField(
        max_length=8, blank=True, null=True, help_text="공시 시작일"
    )
    dcls_end_day = models.CharField(
        max_length=8, blank=True, null=True, help_text="공시 종료일"
    )
    fin_co_subm_day = models.CharField(
        max_length=12, blank=True, null=True, help_text="금융회사 제출일"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"[{self.kor_co_nm}] {self.fin_prdt_nm} ({self.fin_prdt_cd})"


# 추상 기본 옵션 클래스
class BaseOption(models.Model):
    intr_rate_type = models.CharField(
        max_length=1, help_text="이자율 종류 (S:단리, M:복리)"
    )
    intr_rate_type_nm = models.CharField(
        max_length=10, help_text="이자율 종류명 (단리/복리)"
    )
    save_trm = models.CharField(max_length=3, help_text="저축 기간 (개월)")
    intr_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="저축 금리 (소수점 2자리)",
    )
    intr_rate2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="최고 우대금리 (소수점 2자리)",
    )

    class Meta:
        abstract = True
        # 복합 기본키는 Django에서 직접 지원하지 않으므로, unique_together로 고유성 보장
        # 실제 API 데이터에서는 fin_prdt_cd, intr_rate_type, save_trm 이 복합키 역할을 할 수 있음
        # option_id를 별도로 두고, unique_together로 데이터 무결성을 높이는 방안을 고려할 수 있음
        # 또는 fin_prdt_cd + save_trm + intr_rate_type 조합으로 고유하게 관리

    def __str__(self):
        return f"{self.save_trm}개월 - {self.intr_rate_type_nm} (기본: {self.intr_rate}%, 우대: {self.intr_rate2}%)"


# 예금 상품
class DepositProduct(BaseProduct):
    # 예금 상품에만 특화된 필드가 있다면 여기에 추가
    pass


# 예금 상품 옵션
class DepositOption(BaseOption):
    product = models.ForeignKey(
        DepositProduct,
        on_delete=models.CASCADE,
        related_name="options",
        to_field="fin_prdt_cd",
        help_text="연관 예금상품 코드",
    )
    # option_id를 AutoField로 자동 생성되도록 하거나, 복합키 역할을 하는 필드들로 unique_together 설정
    # 여기서는 Django의 관례에 따라 AutoField를 PK로 사용하고, 필요시 unique_together 추가

    class Meta(BaseOption.Meta):  # 부모 Meta 상속
        unique_together = (
            ("product", "intr_rate_type", "save_trm"),
        )  # 상품 내에서 옵션 조합의 고유성

    def __str__(self):
        return f"{self.product.fin_prdt_nm} 옵션: {super().__str__()}"


# 적금 상품
class SavingProduct(BaseProduct):
    # 적금 상품에만 특화된 필드
    rsrv_type = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        help_text="적립 유형 (F:자유적립식, S:정액적립식)",
    )
    rsrv_type_nm = models.CharField(
        max_length=10, blank=True, null=True, help_text="적립 유형명"
    )
    # 추가적으로 적금에만 필요한 필드 정의
    pass


# 적금 상품 옵션
class SavingOption(BaseOption):
    product = models.ForeignKey(
        SavingProduct,
        on_delete=models.CASCADE,
        related_name="options",
        to_field="fin_prdt_cd",
        help_text="연관 적금상품 코드",
    )
    acc_type_nm = models.CharField(
        max_length=20, blank=True, null=True, help_text="적금 종류명(청년/일반 등)"
    )  # 금융감독원 API에 있는 필드

    class Meta(BaseOption.Meta):  # 부모 Meta 상속
        unique_together = (("product", "intr_rate_type", "save_trm"),)

    def __str__(self):
        return f"{self.product.fin_prdt_nm} 옵션: {super().__str__()}"


# 예금 상품 구독
class DepositSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposit_subscriptions",
    )
    product = models.ForeignKey(
        DepositProduct,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        to_field="fin_prdt_cd",
    )
    option = models.ForeignKey(
        DepositOption,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,  # 기존 데이터를 위해 null 허용
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0, default=0)  # 가입 금액

    class Meta:
        unique_together = (("user", "product", "option"),)
        ordering = ["-subscribed_at"]
        verbose_name = "예금 상품 구독"
        verbose_name_plural = "예금 상품 구독 목록"

    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"


# 적금 상품 구독
class SavingSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saving_subscriptions",
    )
    product = models.ForeignKey(
        SavingProduct,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        to_field="fin_prdt_cd",
    )
    option = models.ForeignKey(
        SavingOption,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,  # 기존 데이터를 위해 null 허용
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(max_digits=15, decimal_places=0, default=0)  # 가입 금액

    class Meta:
        unique_together = (("user", "product", "option"),)
        ordering = ["-subscribed_at"]
        verbose_name = "적금 상품 구독"
        verbose_name_plural = "적금 상품 구독 목록"

    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"
