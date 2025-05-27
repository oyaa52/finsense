from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"

    def ready(self):
        # 애플리케이션이 준비되었을 때 시그널을 import.
        import accounts.signals
