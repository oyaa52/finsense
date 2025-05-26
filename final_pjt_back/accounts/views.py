from django.shortcuts import render, get_object_or_404
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Profile, FavoriteChannel, FavoriteVideo  # Profile 모델 임포트
from .serializers import ProfileSerializer, FavoriteChannelSerializer, FavoriteVideoSerializer, UserProfileSerializer

from dj_rest_auth.views import LoginView as DefaultLoginView
from dj_rest_auth.serializers import UserDetailsSerializer

from django.contrib.auth import get_user_model # User 모델 가져오기
from community.models import Post # Post 모델 가져오기 (사용되지는 않지만, UserProfileSerializer에서 간접적으로 필요할 수 있음)
# from community.serializers import PostSerializer # UserProfileSerializer 내부에서 사용

from django.http import JsonResponse
from django.views import View
# from django.conf import settings # settings 임포트는 SocialLoginCallbackView에서만 사용하므로 여기서는 불필요할 수 있음
# from django.shortcuts import redirect # redirect 임포트도 SocialLoginCallbackView 용도

from rest_framework.views import APIView # APIView 임포트
from django.core.cache import cache # Django 캐시 임포트

User = get_user_model()


class CustomLoginView(DefaultLoginView): # 다시 DefaultLoginView 상속
    def get_response_data(self, user):
        data = super().get_response_data(user)
        user_data = UserDetailsSerializer(user, context=self.get_serializer_context()).data
        data['user'] = user_data
        return data

class ProfileDetailAPIView(generics.RetrieveUpdateAPIView): # 원래대로 RetrieveUpdateAPIView
    """
    현재 로그인한 사용자의 프로필 정보를 조회하고 수정하는 API 뷰
    GET: 프로필 정보 조회
    PUT/PATCH: 프로필 정보 수정
    """
    serializer_class = ProfileSerializer # 원래 ProfileSerializer 사용
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

class UserProfileDetailAPIView(generics.RetrieveAPIView):
    """
    특정 사용자의 프로필 정보와 작성한 게시글 목록을 조회하는 API 뷰
    GET: /api/accounts/profile/<username>/
    """
    queryset = User.objects.prefetch_related('profile', 'posts__comments', 'posts__likes', 'followers', 'following').all()
    serializer_class = UserProfileSerializer
    lookup_field = 'username'
    permission_classes = [AllowAny] # AllowAny 사용

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

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

# Allauth 소셜 로그인 후, Vue 앱이 호출하여 세션에서 토큰을 가져갈 API 뷰 (주석 처리 또는 삭제)
# class GetAuthTokenFromSessionView(APIView):
#     permission_classes = [AllowAny]
#
#     def get(self, request, *args, **kwargs):
#         print(f"[DEBUG] GetAuthTokenFromSessionView called. Session items at start: {list(request.session.items())}") # 세션 전체 항목 출력
#
#         # pop 하기 전, session.get으로 확인
#         token_before_pop = request.session.get('api_auth_token')
#         user_id_before_pop = request.session.get('api_auth_token_user_id')
#         print(f"[DEBUG] Token in session (before pop): {token_before_pop}")
#         print(f"[DEBUG] User ID in session (before pop): {user_id_before_pop}")
#
#         api_token = request.session.pop('api_auth_token', None)
#         user_id = request.session.pop('api_auth_token_user_id', None)
#
#         print(f"[DEBUG] Token from session (after pop): {api_token}") # pop 이후의 토큰 값 출력
#         print(f"[DEBUG] User ID from session (after pop): {user_id}") # pop 이후의 사용자 ID 값 출력
#
#         if api_token and user_id:
#             return Response({
#                 'token': api_token,
#                 'user_id': user_id
#             }, status=status.HTTP_200_OK)
#         else:
#             return Response({
#                 'error': 'Authentication token not found in session. Please try logging in again.'
#             }, status=status.HTTP_400_BAD_REQUEST)

class GetTokenByOTTView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        one_time_token = request.query_params.get('ott', None)
        if not one_time_token:
            return Response({'error': 'OTT is required.'}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"ott_{one_time_token}"
        token_data = cache.get(cache_key)

        if token_data:
            cache.delete(cache_key) # 일회성 사용 후 캐시에서 삭제
            print(f"[DEBUG] GetTokenByOTTView: OTT '{one_time_token}' exchanged successfully for token: {token_data.get('api_token')[:5]}... and user_id: {token_data.get('user_id')}")
            return Response({
                'token': token_data.get('api_token'),
                'user_id': token_data.get('user_id')
            }, status=status.HTTP_200_OK)
        else:
            print(f"[DEBUG] GetTokenByOTTView: Invalid or expired OTT '{one_time_token}' provided.")
            return Response({'error': 'Invalid or expired OTT.'}, status=status.HTTP_400_BAD_REQUEST)


# class SocialLoginCallbackView(View): # 이 뷰는 현재 시나리오에서 사용하지 않으므로 주석 처리합니다.
#     def get(self, request, *args, **kwargs):
#         api_token = request.session.pop('api_auth_token', None)
#         user_id = request.session.pop('api_auth_token_user_id', None)
# 
#         if api_token and user_id:
#             # 프론트엔드의 특정 경로로 리디렉션하면서 토큰과 사용자 ID를 쿼리 파라미터로 전달
#             # LOGIN_REDIRECT_URL은 settings.py에 정의된 Vue 앱의 콜백 처리 경로
#             # 예: http://localhost:5173/social-callback?token=YOUR_API_TOKEN&user_id=USER_ID
#             redirect_url = f"{settings.LOGIN_REDIRECT_URL}?token={api_token}&user_id={user_id}"
#             return redirect(redirect_url)
#         else:
#             # 토큰이나 사용자 ID가 없으면 에러 또는 기본 페이지로 리디렉션
#             # 이 경우, 프론트엔드에서 에러를 적절히 처리해야 함
#             error_redirect_url = f"{settings.LOGIN_REDIRECT_URL}?error=authentication_failed" # LOGIN_REDIRECT_URL은 Vue 앱의 기본 주소 또는 에러 페이지로
#             # 또는 JsonResponse({'error': 'API token not found in session'}, status=400)
#             return redirect(error_redirect_url)