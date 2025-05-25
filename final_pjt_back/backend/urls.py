from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path("api/v1/accounts/", include("accounts.urls")),
    path("api/v1/products/", include("products.urls")),
    path("api/v1/kakaomap/", include("kakaomap.urls")),
    path("api/v1/assetinfo/", include("assetinfo.urls")),
    path("api/v1/recommendations/", include("recommendations.urls")),
    path("api/v1/community/", include("community.urls")),
]
