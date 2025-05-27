# final-pjt/final_pjt_back/assetinfo/models.py
from django.db import models

# 자산 가격 정보 모델
class AssetPrice(models.Model):
    asset_name = models.CharField(max_length=50, help_text="자산명 (예: Gold, Silver)") # 자산의 이름
    date = models.DateField(help_text="가격 기준일") # 가격 데이터의 날짜
    price = models.DecimalField(max_digits=15, decimal_places=2, help_text="종가 또는 최종 가격") # 해당 날짜의 자산 가격

    class Meta:
        unique_together = ('asset_name', 'date') # (자산명, 날짜) 조합은 유일해야 함
        ordering = ['date'] # 날짜순으로 정렬
        verbose_name = "자산 가격 정보" # 관리자 페이지 등에서 표시될 모델의 단수 이름
        verbose_name_plural = "자산 가격 정보 목록" # 관리자 페이지 등에서 표시될 모델의 복수 이름

    def __str__(self):
        return f"{self.asset_name} ({self.date}): {self.price}"