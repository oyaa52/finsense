from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Profile  # Profile 모델 임포트
from .serializers import ProfileSerializer  # ProfileSerializer 임포트

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
