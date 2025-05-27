# final-pjt/final_pjt_back/assetinfo/models.py
from django.db import models

class AssetPrice(models.Model): # 클래스 이름이 AssetPrice 인지 확인
    asset_name = models.CharField(max_length=50)
    date = models.DateField()
    price = models.DecimalField(max_digits=15, decimal_places=2)

    class Meta:
        unique_together = ('asset_name', 'date')
        ordering = ['date']
        verbose_name = "자산 가격"
        verbose_name_plural = "자산 가격들"

    def __str__(self):
        return f"{self.asset_name} - {self.date} - {self.price}"