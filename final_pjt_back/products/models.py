from django.db import models
from django.conf import settings
from .utils import get_subscribers_and_send_emails


# 금융 상품 기본 정보 (추상 모델)
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
    max_limit = models.BigIntegerField(blank=True, null=True, help_text="최고한도(원)")
    dcls_strt_day = models.CharField(
        max_length=8, blank=True, null=True, help_text="공시 시작일 (YYYYMMDD)"
    )
    dcls_end_day = models.CharField(
        max_length=8, blank=True, null=True, help_text="공시 종료일 (YYYYMMDD)"
    )
    fin_co_subm_day = models.CharField(
        max_length=12, blank=True, null=True, help_text="금융회사 제출일 (YYYYMMDDHHMM)"
    )

    class Meta:
        abstract = True

    def __str__(self):
        return f"[{self.kor_co_nm}] {self.fin_prdt_nm} ({self.fin_prdt_cd})"


# 금융 상품 옵션 기본 정보 (추상 모델)
class BaseOption(models.Model):
    intr_rate_type = models.CharField(
        max_length=1, help_text="이자율 종류 (S: 단리, M: 복리)"
    )
    intr_rate_type_nm = models.CharField(
        max_length=10, help_text="이자율 종류명 (예: 단리, 복리)"
    )
    save_trm = models.CharField(max_length=3, help_text="저축 기간 (단위: 개월)")
    intr_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="저축 금리 (연, 단위: %)",
    )
    intr_rate2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="최고 우대금리 (연, 단위: %)",
    )

    class Meta:
        abstract = True
        # Django에서 복합 기본키는 직접 지원하지 않으므로 unique_together로 고유성 보장.
        # API 데이터에서 fin_prdt_cd, intr_rate_type, save_trm 조합이 복합키 역할을 할 수 있음.
        # option_id를 별도로 두거나, unique_together로 데이터 무결성 강화 가능.

    def __str__(self):
        return f"{self.save_trm}개월 - {self.intr_rate_type_nm} (기본: {self.intr_rate}%, 우대: {self.intr_rate2}%)"


# 예금 상품 모델
class DepositProduct(BaseProduct):
    # BaseProduct 상속, 예금 상품 특화 필드 필요시 여기에 추가
    pass


# 예금 상품 옵션 모델
class DepositOption(BaseOption):
    product = models.ForeignKey(
        DepositProduct,
        on_delete=models.CASCADE,
        related_name="options",
        to_field="fin_prdt_cd",
        help_text="연관 예금상품 (DepositProduct의 fin_prdt_cd 참조)",
    )
    # AutoField (id)가 PK로 자동 생성. 필요시 unique_together 추가.

    def save(self, *args, **kwargs):
        old_instance = None
        if self.pk:  # 기존 인스턴스 업데이트 시
            try:
                old_instance = DepositOption.objects.get(pk=self.pk)
            except DepositOption.DoesNotExist:
                pass  # 없는 경우 새로 생성되는 것과 동일하게 처리 (이론상 발생X)

        super().save(*args, **kwargs)  # DB에 먼저 저장 (self.pk 확정)

        if old_instance:  # 기존 인스턴스가 있었고, 금리 변경이 있다면
            changes = {}
            if old_instance.intr_rate != self.intr_rate:
                changes["기본 금리"] = (
                    (
                        f"{old_instance.intr_rate:.2f}"
                        if old_instance.intr_rate is not None
                        else "-"
                    ),
                    f"{self.intr_rate:.2f}" if self.intr_rate is not None else "-",
                )
            if old_instance.intr_rate2 != self.intr_rate2:
                changes["최고 우대금리"] = (
                    (
                        f"{old_instance.intr_rate2:.2f}"
                        if old_instance.intr_rate2 is not None
                        else "-"
                    ),
                    f"{self.intr_rate2:.2f}" if self.intr_rate2 is not None else "-",
                )

            if changes:  # 변경 사항이 있을 경우에만 이메일 발송 로직 호출
                get_subscribers_and_send_emails(self, changes)

    class Meta(BaseOption.Meta):  # BaseOption의 Meta 정보 상속
        unique_together = (
            ("product", "intr_rate_type", "save_trm"),
        )  # 한 상품 내에서 (이자율타입, 저축기간) 조합은 유일해야 함

    def __str__(self):
        return f"{self.product.fin_prdt_nm} 옵션: {super().__str__()}"


# 적금 상품 모델
class SavingProduct(BaseProduct):
    # BaseProduct 상속, 적금 상품 특화 필드
    rsrv_type = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        help_text="적립 유형 (F: 자유적립식, S: 정액적립식)",
    )
    rsrv_type_nm = models.CharField(
        max_length=10, blank=True, null=True, help_text="적립 유형명 (예: 자유적립식)"
    )
    pass


# 적금 상품 옵션 모델
class SavingOption(BaseOption):
    product = models.ForeignKey(
        SavingProduct,
        on_delete=models.CASCADE,
        related_name="options",
        to_field="fin_prdt_cd",
        help_text="연관 적금상품 (SavingProduct의 fin_prdt_cd 참조)",
    )
    acc_type_nm = models.CharField(
        max_length=20, blank=True, null=True, help_text="적금 종류명 (예: 청년우대형)"
    )

    def save(self, *args, **kwargs):
        old_instance = None
        if self.pk:  # 기존 인스턴스 업데이트 시
            try:
                old_instance = SavingOption.objects.get(pk=self.pk)
            except SavingOption.DoesNotExist:
                pass

        super().save(*args, **kwargs)  # DB에 먼저 저장 (self.pk 확정)

        if old_instance:  # 기존 인스턴스가 있었고, 금리 변경이 있다면
            changes = {}
            if old_instance.intr_rate != self.intr_rate:
                changes["기본 금리"] = (
                    (
                        f"{old_instance.intr_rate:.2f}"
                        if old_instance.intr_rate is not None
                        else "-"
                    ),
                    f"{self.intr_rate:.2f}" if self.intr_rate is not None else "-",
                )
            if old_instance.intr_rate2 != self.intr_rate2:
                changes["최고 우대금리"] = (
                    (
                        f"{old_instance.intr_rate2:.2f}"
                        if old_instance.intr_rate2 is not None
                        else "-"
                    ),
                    f"{self.intr_rate2:.2f}" if self.intr_rate2 is not None else "-",
                )

            if changes:  # 변경 사항이 있을 경우에만 이메일 발송 로직 호출
                get_subscribers_and_send_emails(self, changes)

    class Meta(BaseOption.Meta):  # BaseOption의 Meta 정보 상속
        unique_together = (("product", "intr_rate_type", "save_trm"),)

    def __str__(self):
        return f"{self.product.fin_prdt_nm} 옵션: {super().__str__()}"


# 예금 상품 구독 정보 모델
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
        null=True,
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(
        max_digits=15, decimal_places=0, default=0, help_text="가입 금액 (단위: 원)"
    )

    class Meta:
        unique_together = (("user", "product", "option"),)
        ordering = ["-subscribed_at"]
        verbose_name = "예금 상품 구독 정보"
        verbose_name_plural = "예금 상품 구독 정보 목록"

    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"


# 적금 상품 구독 정보 모델
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
        null=True,
    )
    subscribed_at = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(
        max_digits=15, decimal_places=0, default=0
    )

    class Meta:
        unique_together = (("user", "product", "option"),)
        ordering = ["-subscribed_at"]
        verbose_name = "적금 상품 구독 정보"
        verbose_name_plural = "적금 상품 구독 정보 목록"

    def __str__(self):
        return f"{self.user.username} - {self.product.fin_prdt_nm}"
