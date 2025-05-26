from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _ # 다국어 지원을 위해 추가
from .models import (
    Profile,
    User,
    FavoriteChannel,
    FavoriteVideo,
)  # Profile 모델과 User 모델 임포트
from dj_rest_auth.serializers import UserDetailsSerializer


class CustomRegisterSerializer(RegisterSerializer):

    def validate_email(self, email):
        # 부모 클래스의 email 유효성 검사를 먼저 수행 (선택 사항, 하지만 일반적으로 좋음)
        # email 필드가 있는지, 그리고 값이 있는지 먼저 확인 (dj-rest-auth가 처리해주지만 명시적으로)
        if email and User.objects.filter(email__iexact=email).exists(): # 대소문자 구분 없이 비교
            raise serializers.ValidationError(_("이미 가입한 이메일입니다."))
 
        return email

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


class CustomUserDetailsSerializer(UserDetailsSerializer):
    class Meta(UserDetailsSerializer.Meta):
        fields = UserDetailsSerializer.Meta.fields + ("is_superuser", "is_staff")


class FavoriteChannelSerializer(serializers.ModelSerializer):
    # 읽기 전용으로 사용자 정보를 간단히 표시 (username만)
    user = serializers.StringRelatedField(read_only=True)
    # channel_id와 channel_title은 클라이언트에서 직접 제공받거나, YouTube API 통해 가져와 저장할 수 있음

    class Meta:
        model = FavoriteChannel
        fields = ("id", "user", "channel_id", "channel_title", "added_at")
        read_only_fields = ("user", "added_at")  # user와 added_at은 서버에서 자동 설정


class FavoriteVideoSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FavoriteVideo
        fields = (
            "id",
            "user",
            "video_id",
            "video_title",
            "thumbnail_url",
            "channel_title",
            "publish_time",
            "added_at",
        )
        read_only_fields = ("user", "added_at")
