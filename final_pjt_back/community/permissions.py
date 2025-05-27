from rest_framework import permissions

# 커스텀 권한: 객체 소유자 또는 슈퍼유저만 수정/삭제 가능, 그 외 읽기만 허용
class IsOwnerOrReadOnly(permissions.BasePermission):
    # 모델 인스턴스에 'user' 속성이 있다고 가정

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS 요청 (읽기 권한)은 항상 허용
        if request.method in permissions.SAFE_METHODS:
            return True

        # 쓰기 권한 (수정/삭제 등)은 객체의 소유자 또는 슈퍼유저에게만 허용
        # 슈퍼유저인 경우 모든 권한 허용
        if request.user and request.user.is_superuser:
            return True
        
        # 그 외의 경우, 요청 사용자와 객체 소유자가 동일해야 쓰기 권한 허용
        return obj.user == request.user 