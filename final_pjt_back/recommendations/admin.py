from django.contrib import admin
from .models import RecommendationHistory

# Django 관리자 페이지에서 RecommendationHistory 모델을 관리하기 위한 설정
@admin.register(RecommendationHistory)
class RecommendationHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_recommended_product_count', 'created_at', 'get_reason_preview')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'recommended_products', 'recommendation_reason')
    readonly_fields = ('user', 'recommended_products', 'created_at', 'recommendation_reason')
    date_hierarchy = 'created_at'

    def get_recommended_product_count(self, obj):
        if obj.recommended_products:
            return f"{len(obj.recommended_products.split(','))}개 상품"
        return "0개 상품"
    get_recommended_product_count.short_description = '추천 상품 수'

    def get_reason_preview(self, obj):
        if obj.recommendation_reason:
            return (obj.recommendation_reason[:50] + '...') if len(obj.recommendation_reason) > 50 else obj.recommendation_reason
        return "-"
    get_reason_preview.short_description = '추천 이유 (일부)'
