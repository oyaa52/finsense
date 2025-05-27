from django.db import models
from django.conf import settings

# 사용자에게 제공된 금융 상품 추천 내역을 기록하는 모델
class RecommendationHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        verbose_name="사용자",
        help_text="추천을 받은 사용자"
    )
    recommended_products = models.TextField(
        verbose_name="추천 상품 목록",
        help_text="추천된 금융 상품의 코드들을 쉼표(,)로 구분하여 저장합니다. 예: DP001,SP002"
    )  
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="추천 시각",
        help_text="추천이 생성된 날짜 및 시각"
    )
    recommendation_reason = models.TextField(
        verbose_name="추천 이유",
        help_text="상품 추천에 대한 전반적인 이유 또는 GPT가 생성한 설명"
    )

    # 관리자 페이지 등에서 객체를 문자열로 표시할 때 사용
    def __str__(self):
        return f"{self.user.username}님에 대한 추천 (생성 시각: {self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    class Meta:
        verbose_name = "금융 상품 추천 기록"
        verbose_name_plural = "금융 상품 추천 기록 목록"
        ordering = ["-created_at"] # 최신 추천 순으로 정렬
