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


# UserProfileSerializer 추가
class UserProfileSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    profile_image = serializers.CharField(source='profile.profile_image', allow_blank=True, allow_null=True, required=False)
    # profile_image = serializers.SerializerMethodField()
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

    # def get_profile_image(self, obj):
    #     if hasattr(obj, 'profile') and obj.profile.profile_image:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(obj.profile.profile_image.url)
    #         return obj.profile.profile_image.url
    #     return None

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        # 프로필 페이지의 주인이 현재 로그인한 유저와 같으면 is_following은 의미가 없으므로 False
        if request and request.user.is_authenticated and request.user != obj:
            # Follow 모델을 가져와야 함
            from community.models import Follow # Follow 모델 임포트 (위치 조정 필요)
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False

    def get_follow_id_for_current_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            from community.models import Follow
            follow_instance = Follow.objects.filter(follower=request.user, following=obj).first()
            if follow_instance:
                return follow_instance.id
        return None

    def get_followers_list(self, obj): 
        follower_users = [follow.follower for follow in obj.followers.all()]
        request = self.context.get('request')
        return CommunityUserSerializer(follower_users, many=True, context={'request': request}).data

    def get_followings_list(self, obj): 
        following_users = [follow.following for follow in obj.following.all()]
        request = self.context.get('request')
        return CommunityUserSerializer(following_users, many=True, context={'request': request}).data
