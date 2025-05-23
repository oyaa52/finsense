from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Profile  # Profile 모델 임포트 (이미 있다면 생략 가능)
from .serializers import ProfileSerializer  # ProfileSerializer 임포트

# Create your views here.


class ProfileDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    현재 로그인한 사용자의 프로필 정보를 조회하고 수정하는 API 뷰입니다.
    GET: 프로필 정보 조회
    PUT/PATCH: 프로필 정보 수정
    """

    # queryset = Profile.objects.all() # get_object에서 직접 객체를 반환하므로 queryset은 필수는 아님
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get_object(self):
        """
        요청을 보낸 사용자에 해당하는 Profile 객체를 반환합니다.
        Profile이 없는 경우 (매우 드문 케이스, 시그널로 생성되므로) 404가 발생할 수 있습니다.
        """
        # User 모델에는 Profile과의 OneToOne 관계가 'profile'이라는 related_name으로 설정되어 있다고 가정합니다.
        # 만약 User 모델에 profile = OneToOneField(Profile, ...) 와 같이 직접 정의되어 있지 않고,
        # Profile 모델에 user = OneToOneField(User, ...) 만 있다면, 아래와 같이 접근합니다.
        return self.request.user.profile
