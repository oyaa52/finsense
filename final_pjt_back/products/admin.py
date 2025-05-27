from django.contrib import admin
from .models import (
    DepositProduct,
    DepositOption,
    SavingProduct,
    SavingOption,
    DepositSubscription,
    SavingSubscription,
)

# Django 관리자 페이지에 모델 등록
admin.site.register(DepositProduct)
admin.site.register(DepositOption)
admin.site.register(SavingProduct)
admin.site.register(SavingOption)
admin.site.register(DepositSubscription)
admin.site.register(SavingSubscription)
