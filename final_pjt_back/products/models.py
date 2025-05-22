from django.db import models

# Create your models here.


class DepositProduct(models.Model):
    fin_prdt_cd = models.CharField(max_length=50, primary_key=True)
    kor_co_nm = models.CharField(max_length=100)  # 은행명
    fin_prdt_nm = models.CharField(max_length=200)  # 상품명
    etc_note = models.TextField()  # 상품설명
    join_deny = models.IntegerField()  # 가입제한 여부
    join_member = models.CharField(max_length=100)  # 가입대상
    join_way = models.CharField(max_length=100)  # 가입경로
    spcl_cnd = models.CharField(max_length=200)  # 특별조건

    def __str__(self):
        return f"{self.kor_co_nm} - {self.fin_prdt_nm}"


class DepositOption(models.Model):
    option_id = models.AutoField(primary_key=True)
    fin_prdt_cd = models.ForeignKey(DepositProduct, on_delete=models.CASCADE)
    intr_rate_type_nm = models.CharField(max_length=50)  # 금리형태(단리/복리)
    save_trm = models.IntegerField()  # save_trm (개월)
    intr_rate = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # intr_rate (기본 금리)
    intr_rate2 = models.DecimalField(
        max_digits=5, decimal_places=2
    )  # intr_rate2 (우대 금리)

    def __str__(self):
        return f"{self.fin_prdt_cd.fin_prdt_nm} - {self.save_trm}개월"


class Subscription(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    fin_prdt_cd = models.ForeignKey(DepositProduct, on_delete=models.CASCADE)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "fin_prdt_cd")

    def __str__(self):
        return f"{self.user.username} - {self.fin_prdt_cd.fin_prdt_nm}"


class AssetPrice(models.Model):
    asset_name = models.CharField(max_length=50)
    date = models.DateField()
    price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ("asset_name", "date")

    def __str__(self):
        return f"{self.asset_name} - {self.date}"
