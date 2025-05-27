from django.db import models

class MarketIndex(models.Model):
    name = models.CharField(max_length=20, unique=True)  # 'KOSPI', 'KOSDAQ' 등
    value = models.FloatField()  # 현재 지수
    change = models.FloatField()  # 전일 대비 변동폭
    rate = models.FloatField()  # 전일 대비 변동률 (%)
    last_updated = models.DateTimeField(auto_now=True)  # 마지막 업데이트 시간

    def __str__(self):
        return f"{self.name}: {self.value} ({self.change} / {self.rate}%)"

    class Meta:
        verbose_name = "시장 지수"
        verbose_name_plural = "시장 지수 목록"
        ordering = ['name'] 