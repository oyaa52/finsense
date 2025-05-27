from django.utils import timezone
from .models import MarketIndex
from .utils import get_market_indices
import logging
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


def update_market_indices_job():
    """
    네이버 금융에서 시장 지수(KOSPI, KOSDAQ)를 크롤링하여 DB에 업데이트하는 스케줄링 작업.
    """
    logger.info("시장 지수 DB 업데이트 작업 시작...")
    indices_data = get_market_indices()

    if not indices_data:
        logger.warning("크롤링된 시장 지수 데이터가 없어 DB 업데이트를 건너뜁니다.")
        return

    for index_info in indices_data:
        index_name = index_info.get("name")
        current_value = index_info.get("value")
        change_val = index_info.get("change")
        rate_val = index_info.get("rate")

        # 크롤링 데이터 유효성 확인 (필수 필드 누락 시 건너뛰기)
        if not all([index_name, current_value is not None, change_val is not None, rate_val is not None]):
            logger.error(f"크롤링 데이터에 필수 필드가 누락되어 처리를 건너뜁니다: {index_info}")
            continue

        try:
            # MarketIndex 모델 객체 가져오거나 새로 생성 (name 기준)
            index, created = MarketIndex.objects.get_or_create(
                name=index_name,
                defaults={
                    "value": current_value,
                    "change": change_val,
                    "rate": rate_val,
                    "last_updated": timezone.now(), # 생성 시 last_updated 설정
                },
            )

            if not created: # 기존 객체가 있다면 필드 값 업데이트
                index.value = current_value
                index.change = change_val
                index.rate = rate_val
                # index.last_updated = timezone.now() # auto_now=True 필드는 save() 시 자동 업데이트됨
                index.save() # 변경사항 저장

            if created:
                logger.info(f"새로운 시장 지수 [{index_name}] DB 추가 완료.")
            else:
                logger.info(f"시장 지수 [{index_name}] DB 업데이트 완료.")

        except Exception as e:
            logger.error(f"시장 지수 [{index_name}] DB 업데이트 중 오류 발생: {e}", exc_info=True)
            continue # 특정 지수 업데이트 실패 시 다음 지수로 계속 진행

    logger.info("시장 지수 DB 업데이트 작업 완료.")


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def start_scheduler():
    """
    스케줄러를 시작하고, 시장 지수 업데이트 작업을 등록
    앱 준비 시 호출
    """
    try:

        scheduler.add_job(
            update_market_indices_job,
            trigger="interval",
            hours=1,  # 매 1시간마다 실행
            id="update_market_indices_job",
            replace_existing=True,
            misfire_grace_time=3600,  # 작업이 지연되었을 때 1시간 내에는 실행
        )
        logger.info(
            "시장 지수 업데이트 작업이 스케줄러에 등록되었습니다 (매 1시간 실행)."
        )

        if not scheduler.running:
            scheduler.start()
            logger.info("스케줄러를 시작합니다.")


    except Exception as e:
        logger.error(f"스케줄러 시작 또는 작업 등록 중 오류 발생: {e}", exc_info=True)


def schedule_market_indices_update():
    """
    매일 오전 9시에 시장 지수 업데이트 작업을 스케줄링.
    """
