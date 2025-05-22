from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    email = models.EmailField(unique=True)
    subscribed_products = models.ManyToManyField(
        'products.DepositProduct', blank=True, null=True
    )  # 쉼표로 구분된 상품 코드 저장


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(120)])
    gender = models.CharField(max_length=10)
    occupation = models.CharField(max_length=50)
    marital_status = models.CharField(max_length=20)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2)
    amount_available = models.DecimalField(max_digits=12, decimal_places=2)
    investment_purpose = models.CharField(max_length=100)
    investment_term = models.IntegerField()  # 개월 단위
    investment_tendency = models.CharField(
        max_length=20
    )  # 안정형, 안정추구형, 위험중립형, 적극투자형, 공격투자형

    def __str__(self):
        return f"{self.user.username}'s profile"
