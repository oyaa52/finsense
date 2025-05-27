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
from community.serializers import PostSerializer  # PostSerializer 임포트
from community.serializers import UserSerializer as CommunityUserSerializer # UserSerializer 임포트 (이름 충돌 방지)


class CustomRegisterSerializer(RegisterSerializer):

    def validate_email(self, email):
        # 이메일 유효성 검사: dj-rest-auth 기본 검사 외 중복 이메일 확인 (대소문자 무관)
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(_("이미 가입한 이메일입니다."))
        return email

    def save(self, request):
        # 부모 save 호출하여 User 객체 생성 및 반환
        user = super().save(request)
        # Profile.objects.create(user=user) # Profile 자동 생성 로직은 signals.py로 이동
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


# UserProfileSerializer 추가
class UserProfileSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    profile_image = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    follow_id_for_current_user = serializers.SerializerMethodField()
    followers_list = serializers.SerializerMethodField()
    followings_list = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email',
            'profile_image',
            'followers_count', 'following_count', 'is_following', 'follow_id_for_current_user',
            'followers_list', 'followings_list',
            'posts'
        ]

    def get_profile_image(self, obj):
        # 프로필 이미지가 존재하면 절대 경로 URL 반환, 없으면 None
        if hasattr(obj, 'profile') and obj.profile.profile_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile.profile_image.url) # 절대 URI 생성
            return obj.profile.profile_image.url # request 없을 시 상대 경로
        return None

    def get_followers_count(self, obj):
        # 팔로워 수 반환
        return obj.followers.count()

    def get_following_count(self, obj):
        # 팔로잉 수 반환
        return obj.following.count()

    def get_is_following(self, obj):
        # 현재 로그인 사용자가 obj 유저를 팔로우하는지 여부
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            from community.models import Follow # 순환 참조 방지를 위해 메소드 내에서 import
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False

    def get_follow_id_for_current_user(self, obj):
        # 현재 로그인 사용자와 obj 유저 간의 Follow 인스턴스 ID 반환 (없으면 None)
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            from community.models import Follow # 순환 참조 방지를 위해 메소드 내에서 import
            follow_instance = Follow.objects.filter(follower=request.user, following=obj).first()
            if follow_instance:
                return follow_instance.id
        return None

    def get_followers_list(self, obj):
        # 팔로워 사용자 목록을 CommunityUserSerializer로 직렬화하여 반환
        follower_users = [follow.follower for follow in obj.followers.all()]
        request = self.context.get('request')
        return CommunityUserSerializer(follower_users, many=True, context={'request': request}).data

    def get_followings_list(self, obj):
        # 팔로잉 사용자 목록을 CommunityUserSerializer로 직렬화하여 반환
        following_users = [follow.following for follow in obj.following.all()]
        request = self.context.get('request')
        return CommunityUserSerializer(following_users, many=True, context={'request': request}).data
