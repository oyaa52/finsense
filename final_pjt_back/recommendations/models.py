from django.db import models
from django.conf import settings

# Create your models here.


class RecommendationHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recommended_products = models.TextField()  # 추천된 상품 코드들 (쉼표로 구분)
    created_at = models.DateTimeField(auto_now_add=True)
    recommendation_reason = models.TextField()  # 추천 이유

    def __str__(self):
        return f"Recommendation for {self.user.username} at {self.created_at}"
