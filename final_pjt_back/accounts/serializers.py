from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import Profile  # Profile 모델 임포트


class CustomRegisterSerializer(RegisterSerializer):

    def save(self, request):
        # super().save(request) = User 객체를 생성하고 반환
        user = super().save(request)

        return user


# 사용자 프로필 정보를 위한 시리얼라이저
class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = "__all__"  # 프로필의 모든 필드를 포함
        read_only_fields = (
            "user",
        )  # user 필드는 읽기 전용으로 설정 (API를 통해 변경 불가)
