from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Follow

# accounts 앱의 Profile 모델 import (경로가 정확한지 확인 필요, 일반적으로 from accounts.models import Profile)
# 하지만 여기서는 UserSerializer 내에서 직접 접근하므로 별도 import는 필수는 아님

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()  # 프로필 이미지 필드 추가

    class Meta:
        model = User
        # fields 리스트에 'profile_image' 추가
        fields = [
            "id",
            "username",
            "email",
            "followers_count",
            "following_count",
            "is_following",
            "profile_image",
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False

    # 프로필 이미지를 가져오는 메소드
    def get_profile_image(self, obj):
        # User 객체(obj)에 profile (OneToOneField로 연결된 Profile 객체)이 있는지 확인
        if hasattr(obj, "profile") and obj.profile.profile_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile.profile_image.url)
            return (
                obj.profile.profile_image.url
            )  # request가 없으면 상대 경로 반환 (덜 이상적)
        return None  # 프로필이나 프로필 이미지가 없으면 None 반환


class ReplySerializer(
    serializers.ModelSerializer
):  # 대댓글 전용 시리얼라이저 (간단하게)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "content",
            "created_at",
            "parent_comment",
        ]  # parent_comment는 ID로


class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), allow_null=True, required=False
    )
    parent_comment_author_username = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "content",
            "created_at",
            "post",
            "parent",
            "replies",
            "parent_comment_author_username",
        ]
        read_only_fields = ["user", "replies", "post"]

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_parent_comment_author_username(self, obj):
        if obj.parent:
            return obj.parent.user.username
        return None


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # 이제 UserSerializer가 profile_image를 포함
    comments = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "image",
            "created_at",
            "comments",
            "likes_count",
            "is_liked",
        ]
        read_only_fields = ["user", "created_at"]

    def get_comments(self, obj):
        # obj는 현재 Post 인스턴스
        # 이 Post에 연결된 댓글 중 parent가 null인 댓글(최상위 댓글)만 필터링
        top_level_comments = obj.comments.filter(parent__isnull=True)
        # CommentSerializer를 사용하여 직렬화, context 전달
        return CommentSerializer(
            top_level_comments, many=True, context=self.context
        ).data

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False


class FollowSerializer(serializers.ModelSerializer):
    following = UserSerializer(read_only=True)
    follower = UserSerializer(read_only=True)
    following_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "following_id", "created_at"]
        read_only_fields = ["follower", "following", "created_at"]

    def validate_following_id(self, value):
        try:
            user = get_user_model().objects.get(id=value)
            if user == self.context["request"].user:
                raise serializers.ValidationError("자기 자신을 팔로우할 수 없습니다.")
            return value
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")

    def create(self, validated_data):
        following_id = validated_data.pop("following_id")
        following = get_user_model().objects.get(id=following_id)
        follower = self.context["request"].user

        # 이미 팔로우 중인지 확인
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("이미 팔로우 중인 사용자입니다.")

        return Follow.objects.create(following=following, follower=follower)
