from django.urls import path
from . import views

app_name = 'product_recommender'

urlpatterns = [
    path('recommendations/', views.get_recommendations, name='get_recommendations'),
    path('gpt/', views.get_gpt_recommendations, name='get_gpt_recommendations'),
    path('generate-image/', views.generate_image, name='generate_image'),
] 