from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Follow


User = get_user_model()


# 사용자 정보 기본 시리얼라이저 (팔로우/팔로잉 목록 등에서 사용)
class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField() # 팔로워 수
    following_count = serializers.SerializerMethodField() # 팔로잉 수
    is_following = serializers.SerializerMethodField() # 현재 로그인 사용자의 팔로우 여부
    profile_image = serializers.SerializerMethodField()  # 프로필 이미지 URL
    follow_id_for_current_user = serializers.SerializerMethodField() # 현재 로그인 사용자와의 팔로우 관계 ID (있을 경우)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "followers_count",
            "following_count",
            "is_following",
            "profile_image",
            "follow_id_for_current_user",
        ]

    def get_followers_count(self, obj):
        # obj: User 인스턴스
        return obj.followers.count()

    def get_following_count(self, obj):
        # obj: User 인스턴스
        return obj.following.count()

    def get_is_following(self, obj):
        # obj: 대상 User 인스턴스, context의 request.user: 현재 로그인 사용자
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False

    def get_profile_image(self, obj):
        # obj: User 인스턴스. 프로필 이미지가 있으면 절대 URL 반환, 없으면 None
        if hasattr(obj, "profile") and obj.profile.profile_image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.profile.profile_image.url) # 전체 URI
            return obj.profile.profile_image.url # 상대 경로 (대안)
        return None

    def get_follow_id_for_current_user(self, obj):  # obj: 대상 사용자 (targetUser)
        # 현재 로그인 사용자가 obj 사용자를 팔로우하고 있다면 해당 Follow 인스턴스의 ID 반환
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            try:
                follow_instance = Follow.objects.get(
                    follower=request.user, following=obj
                )
                return follow_instance.id
            except Follow.DoesNotExist:
                return None # 팔로우하고 있지 않으면 None
        return None


# 대댓글(Reply) 정보 시리얼라이저 (CommentSerializer 내에서 사용)
class ReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # 작성자 정보

    class Meta:
        model = Comment
        fields = [
            "id",
            "user",
            "content",
            "created_at",
            "parent_comment", # 부모 댓글 ID
        ]


# 댓글(Comment) 정보 시리얼라이저 (대댓글 포함)
class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True) # 작성자 정보
    replies = serializers.SerializerMethodField() # 대댓글 목록
    parent = serializers.PrimaryKeyRelatedField( # 부모 댓글 ID (대댓글인 경우)
        queryset=Comment.objects.all(), allow_null=True, required=False
    )
    parent_comment_author_username = serializers.SerializerMethodField() # 부모 댓글 작성자명 (대댓글인 경우)

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
        # obj: Comment 인스턴스. 해당 댓글의 대댓글들을 직렬화하여 반환
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_parent_comment_author_username(self, obj):
        # obj: Comment 인스턴스. 대댓글일 경우 부모 댓글 작성자의 username 반환
        if obj.parent:
            return obj.parent.user.username
        return None


# 게시글(Post) 정보 시리얼라이저 (댓글, 좋아요 정보 포함)
class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # 작성자 정보 (프로필 이미지 포함)
    comments = serializers.SerializerMethodField() # 게시글의 최상위 댓글 목록
    likes_count = serializers.SerializerMethodField() # 좋아요 수
    is_liked = serializers.SerializerMethodField() # 현재 로그인 사용자의 좋아요 여부

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
        # obj: Post 인스턴스. 해당 게시글의 최상위 댓글만 필터링하여 직렬화
        top_level_comments = obj.comments.filter(parent__isnull=True)
        return CommentSerializer(
            top_level_comments, many=True, context=self.context
        ).data

    def get_likes_count(self, obj):
        # obj: Post 인스턴스. 좋아요 수 반환
        return obj.likes.count()

    def get_is_liked(self, obj):
        # obj: Post 인스턴스. 현재 로그인 사용자가 해당 게시글을 좋아요 했는지 여부
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False


# 팔로우(Follow) 관계 정보 시리얼라이저
class FollowSerializer(serializers.ModelSerializer):
    following = UserSerializer(read_only=True) # 팔로우 대상 사용자 정보
    follower = UserSerializer(read_only=True) # 팔로우 하는 사용자 정보
    following_id = serializers.IntegerField(write_only=True) # 팔로우할 사용자의 ID (생성 시 사용)

    class Meta:
        model = Follow
        fields = ["id", "follower", "following", "following_id", "created_at"]
        read_only_fields = ["follower", "following", "created_at"]

    def validate_following_id(self, value):
        # 팔로우 대상 ID 유효성 검사
        try:
            user_to_follow = get_user_model().objects.get(id=value)
            # 자기 자신 팔로우 방지
            if user_to_follow == self.context["request"].user:
                raise serializers.ValidationError("자기 자신을 팔로우할 수 없습니다.")
            return value # 유효한 사용자 ID 반환
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("팔로우할 사용자를 찾을 수 없습니다.")

    def create(self, validated_data):
        # 팔로우 관계 생성
        following_id = validated_data.pop("following_id")
        following_user = get_user_model().objects.get(id=following_id)
        follower_user = self.context["request"].user

        # 이미 팔로우 중인지 확인 후 중복 생성 방지
        if Follow.objects.filter(follower=follower_user, following=following_user).exists():
            raise serializers.ValidationError("이미 팔로우하고 있는 사용자입니다.")

        return Follow.objects.create(following=following_user, follower=follower_user)
