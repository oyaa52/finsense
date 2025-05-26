from django.contrib import admin
from .models import (
    DepositProduct,
    DepositOption,
    SavingProduct,
    SavingOption,
    DepositSubscription,
    SavingSubscription,
)

# Register your models here.
admin.site.register(DepositProduct)
admin.site.register(DepositOption)
admin.site.register(SavingProduct)
admin.site.register(SavingOption)
admin.site.register(DepositSubscription)
admin.site.register(SavingSubscription)
