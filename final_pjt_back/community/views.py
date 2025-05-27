from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Follow
from .serializers import (
    PostSerializer,
    CommentSerializer,
    FollowSerializer,
    UserSerializer,
)
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .permissions import IsOwnerOrReadOnly

User = get_user_model()


# 페이지네이션 클래스 정의
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10  # 기본 페이지 크기
    page_size_query_param = (
        "page_size"  # 클라이언트가 page_size를 변경할 수 있도록 허용
    )
    max_page_size = 100  # 클라이언트가 요청할 수 있는 최대 page_size


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by("-created_at")
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        elif self.action in ["create", "like", "comment"]:
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def like(self, request, pk=None):
        post = self.get_object()
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            liked = False
        else:
            post.likes.add(user)
            liked = True
        return Response(
            {"liked": liked, "likes_count": post.likes.count()},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="comments",
        permission_classes=[IsAuthenticated],
    )
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = CommentSerializer(
            data=request.data, context={"request": request, "post": post}
        )
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by("created_at")
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action in ["create"]:
            return [permissions.IsAuthenticated()]
        elif self.action in ["update", "partial_update", "destroy"]:
            return [IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ["user_followers_list", "user_following_list"]:
            return [permissions.IsAuthenticated()]
        elif self.action == "create":
            return [permissions.IsAuthenticated()]
        elif self.action == "destroy":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        return Follow.objects.filter(follower=self.request.user)

    def perform_create(self, serializer):
        try:
            serializer.save(follower=self.request.user)
        except serializers.ValidationError as e:
            raise e
        except Exception as e:
            raise serializers.ValidationError(str(e))

    @action(detail=False, methods=["get"], url_path="my-following")
    def my_following_list(self, request):
        following_relations = self.get_queryset()
        serializer = self.get_serializer(following_relations, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="my-followers")
    def my_followers_list(self, request):
        follower_relations = Follow.objects.filter(following=request.user)
        serializer = self.get_serializer(follower_relations, many=True)
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"], url_path="user/(?P<user_pk>[^/.]+)/followers"
    )
    def user_followers_list(self, request, user_pk=None):
        user = get_object_or_404(User, pk=user_pk)
        followers_relations = Follow.objects.filter(following=user)
        follower_users = [relation.follower for relation in followers_relations]
        serializer = UserSerializer(
            follower_users, many=True, context={"request": request}
        )
        return Response(serializer.data)

    @action(
        detail=False, methods=["get"], url_path="user/(?P<user_pk>[^/.]+)/following"
    )
    def user_following_list(self, request, user_pk=None):
        user = get_object_or_404(User, pk=user_pk)
        following_relations = Follow.objects.filter(follower=user)
        followed_users = [relation.following for relation in following_relations]
        serializer = UserSerializer(
            followed_users, many=True, context={"request": request}
        )
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        following_id = request.data.get("following_id")
        if not following_id:
            return Response(
                {"detail": "following_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            following_user = User.objects.get(id=following_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User to follow not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        follower_user = request.user

        if follower_user == following_user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Follow.objects.filter(
            follower=follower_user, following=following_user
        ).exists():
            return Response(
                {"detail": "Already following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        follow_instance = Follow.objects.create(
            follower=follower_user, following=following_user
        )
        return Response(
            FollowSerializer(follow_instance, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.follower != request.user:
            return Response(
                {
                    "detail": "You do not have permission to perform this action. Only the follower can unfollow."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
