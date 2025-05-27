from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # 앱 준비 시 시그널 임포트 (예: 사용자 생성 시 프로필 자동 생성)
        import accounts.signals
