from django.db import models

# 주요 시장 지수(KOSPI, KOSDAQ) 정보 모델
class MarketIndex(models.Model):
    name = models.CharField(max_length=20, unique=True, help_text="지수명 (예: KOSPI, KOSDAQ)")  # 지수 이름 (고유값)
    value = models.FloatField(help_text="현재 지수 값")  # 현재 지수
    change = models.FloatField(help_text="전일 대비 변동 값 (포인트)")  # 전일 대비 변동폭 (예: +10.5, -5.2)
    rate = models.FloatField(help_text="전일 대비 변동률 (단위: %)")  # 전일 대비 등락률 (예: +0.5%, -0.23%)
    last_updated = models.DateTimeField(auto_now=True, help_text="데이터 마지막 업데이트 일시")  # 레코드 저장/수정 시 자동 업데이트

    def __str__(self):
        return f"{self.name}: {self.value:.2f} (전일비: {self.change:+.2f} / {self.rate:+.2f}%)"

    class Meta:
        verbose_name = "시장 지수 정보" # 관리자 페이지 등에서 표시될 모델의 단수 이름
        verbose_name_plural = "시장 지수 정보 목록" # 관리자 페이지 등에서 표시될 모델의 복수 이름
        ordering = ['name'] # 이름순으로 정렬 