from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Follow

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'followers_count', 'following_count', 'is_following']

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'content', 'image', 'created_at', 
                 'comments', 'likes_count', 'is_liked']
        read_only_fields = ['user', 'created_at']
    
    def get_likes_count(self, obj):
        return obj.likes.count()
    
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False

class FollowSerializer(serializers.ModelSerializer):
    following = UserSerializer(read_only=True)
    follower = UserSerializer(read_only=True)
    following_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'following_id', 'created_at']
        read_only_fields = ['follower', 'following', 'created_at']

    def validate_following_id(self, value):
        try:
            user = get_user_model().objects.get(id=value)
            if user == self.context['request'].user:
                raise serializers.ValidationError("자기 자신을 팔로우할 수 없습니다.")
            return value
        except get_user_model().DoesNotExist:
            raise serializers.ValidationError("존재하지 않는 사용자입니다.")

    def create(self, validated_data):
        following_id = validated_data.pop('following_id')
        following = get_user_model().objects.get(id=following_id)
        follower = self.context['request'].user
        
        # 이미 팔로우 중인지 확인
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("이미 팔로우 중인 사용자입니다.")
            
        return Follow.objects.create(following=following, follower=follower) 