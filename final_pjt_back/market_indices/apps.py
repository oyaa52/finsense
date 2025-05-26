from django.apps import AppConfig
import os

class MarketIndicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market_indices'

    def ready(self):
        # Django 개발 서버 자동 리로더는 ready()를 두 번 호출할 수 있습니다.
        # 스케줄러 중복 실행을 방지하기 위해 jobs.py의 start_scheduler 내부에
        # scheduler.running 확인 및 add_job의 replace_existing=True 옵션을 사용합니다.
        # 보다 확실한 제어를 위해서는 RUN_MAIN 환경 변수 사용 등을 고려할 수 있습니다.
        # (예: if os.environ.get('RUN_MAIN') == 'true':)
        # 또는 Werkzeug 리로더 환경 변수 체크 (개발 서버용):
        # if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not settings.DEBUG:

        # 현재는 jobs.py의 방어 로직을 신뢰하고 바로 호출합니다.
        from .jobs import start_scheduler
        print("MarketIndicesConfig: Initializing scheduler...") 
        start_scheduler() 