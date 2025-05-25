from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Follow
from .serializers import PostSerializer, CommentSerializer, FollowSerializer, UserSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        if request.user in post.likes.all():
            post.likes.remove(request.user)
            return Response({'status': 'unliked'})
        else:
            post.likes.add(request.user)
            return Response({'status': 'liked'})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_pk')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(user=self.request.user, post=post)

class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
        except serializers.ValidationError as e:
            raise serializers.ValidationError(e.detail)
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @action(detail=False, methods=['get'])
    def following(self, request):
        following = Follow.objects.filter(follower=request.user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        followers = Follow.objects.filter(following=request.user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def user_followers(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        followers = Follow.objects.filter(following=user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def user_following(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        following = Follow.objects.filter(follower=user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)
