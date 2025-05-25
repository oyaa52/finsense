from django.shortcuts import render
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Profile, FavoriteChannel, FavoriteVideo  # Profile 모델 임포트
from .serializers import ProfileSerializer, FavoriteChannelSerializer, FavoriteVideoSerializer

from dj_rest_auth.views import LoginView as DefaultLoginView
from dj_rest_auth.serializers import UserDetailsSerializer


class CustomLoginView(DefaultLoginView): # 다시 DefaultLoginView 상속
    def get_response_data(self, user):
        data = super().get_response_data(user)
        user_data = UserDetailsSerializer(user, context=self.get_serializer_context()).data
        data['user'] = user_data
        return data

class ProfileDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    현재 로그인한 사용자의 프로필 정보를 조회하고 수정하는 API 뷰
    GET: 프로필 정보 조회
    PUT/PATCH: 프로필 정보 수정
    """

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get_object(self):
        """
        요청을 보낸 사용자에 해당하는 Profile 객체를 반환.
        Profile이 없는 경우 (매우 드문 케이스, 시그널로 생성되므로) 404가 발생할 수 있음.
        """
        return self.request.user.profile


class FavoriteChannelViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteChannelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # 현재 로그인한 사용자의 즐겨찾는 채널만 반환
        return FavoriteChannel.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 생성 시 현재 로그인한 사용자를 user 필드에 할당
        serializer.save(user=self.request.user)

    # 즐겨찾기 여부 확인을 위한 별도 액션 (GET /api/accounts/favorite-channels/is_favorite/?channel_id=...)
    @action(detail=False, methods=['get'])
    def is_favorite(self, request):
        channel_id = request.query_params.get('channel_id', None)
        if not channel_id:
            return Response({"error": "channel_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        favorite_channel = FavoriteChannel.objects.filter(user=request.user, channel_id=channel_id).first()
        if favorite_channel:
            return Response({'is_favorite': True, 'id': favorite_channel.id, 'channel_id': channel_id}, status=status.HTTP_200_OK)
        else:
            return Response({'is_favorite': False, 'channel_id': channel_id}, status=status.HTTP_200_OK)


class FavoriteVideoViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteVideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FavoriteVideo.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # 즐겨찾기 여부 확인을 위한 별도 액션 (GET /api/accounts/favorite-videos/is_favorite/?video_id=...)
    @action(detail=False, methods=['get'])
    def is_favorite(self, request):
        video_id = request.query_params.get('video_id', None)
        if not video_id:
            return Response({"error": "video_id가 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        favorite_video = FavoriteVideo.objects.filter(user=request.user, video_id=video_id).first()
        if favorite_video:
            return Response({'is_favorite': True, 'id': favorite_video.id, 'video_id': video_id}, status=status.HTTP_200_OK)
        else:
            return Response({'is_favorite': False, 'video_id': video_id}, status=status.HTTP_200_OK)
