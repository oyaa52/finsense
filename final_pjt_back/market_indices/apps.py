from django.apps import AppConfig
import os
import logging # 로깅 모듈 임포트

logger = logging.getLogger(__name__) # 로거 인스턴스 생성

# market_indices 앱 설정 클래스
class MarketIndicesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'market_indices'

    # 앱 준비 완료 시 실행되는 메소드
    def ready(self):
        # Django 개발 서버의 자동 리로더는 ready()를 두 번 호출할 수 있어 스케줄러가 중복 실행될 수 있음.
        # 이를 방지하기 위해:
        # 1. jobs.py의 start_scheduler 함수 내에서 scheduler.running 확인 및 add_job의 replace_existing=True 사용 (현재 방식).
        # 2. (보다 확실한 방법) 메인 프로세스에서만 스케줄러가 시작되도록 환경 변수(RUN_MAIN 등)를 확인.
        #    예: if os.environ.get('RUN_MAIN') == 'true' or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # 현재는 jobs.py 내의 방어 로직을 활용하여 스케줄러 시작.

        from .jobs import start_scheduler # 스케줄러 시작 함수 임포트
        logger.info("MarketIndicesConfig: 시장 지수 업데이트 스케줄러 초기화 시작...")
        start_scheduler() # 스케줄러 시작 및 작업 등록
        logger.info("MarketIndicesConfig: 시장 지수 업데이트 스케줄러 초기화 완료.") 