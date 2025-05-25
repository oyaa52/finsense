from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from .models import Profile, User, FavoriteChannel, FavoriteVideo  # Profile 모델과 User 모델 임포트


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


class FavoriteChannelSerializer(serializers.ModelSerializer):
    # 읽기 전용으로 사용자 정보를 간단히 표시 (username만)
    user = serializers.StringRelatedField(read_only=True)
    # channel_id와 channel_title은 클라이언트에서 직접 제공받거나, YouTube API 통해 가져와 저장할 수 있음

    class Meta:
        model = FavoriteChannel
        fields = ('id', 'user', 'channel_id', 'channel_title', 'added_at')
        read_only_fields = ('user', 'added_at') # user와 added_at은 서버에서 자동 설정


class FavoriteVideoSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FavoriteVideo
        fields = ('id', 'user', 'video_id', 'video_title', 'thumbnail_url', 'channel_title', 'publish_time', 'added_at')
        read_only_fields = ('user', 'added_at')