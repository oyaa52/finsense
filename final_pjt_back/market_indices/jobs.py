from django.utils import timezone
from .models import MarketIndex
from .utils import get_market_indices
import logging
from django_apscheduler.jobstores import DjangoJobStore

# from django_apscheduler.models import DjangoJobExecution # DjangoJobExecution은 직접 사용하지 않으므로 주석 처리 가능
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


def update_market_indices_job():
    """
    네이버 금융에서 시장 지수(KOSPI, KOSDAQ)를 크롤링하여 DB에 업데이트하는 스케줄링 작업.
    """
    logger.info("시장 지수 업데이트 작업을 시작합니다...")
    indices_data = get_market_indices()

    if not indices_data:
        logger.warning("크롤링된 시장 지수 데이터가 없습니다.")
        return

    for index_info in indices_data:
        index_name = index_info["name"]
        current_value = index_info["value"]
        change_val = index_info["change"]
        rate_val = index_info["rate"]

        try:
            index, created = MarketIndex.objects.get_or_create(
                name=index_name,
                defaults={
                    "value": current_value,
                    "change": change_val,
                    "rate": rate_val,
                    "last_updated": timezone.now(),
                },
            )

            if not created:
                index.value = current_value
                index.change = change_val
                index.rate = rate_val
                index.last_updated = timezone.now()
                index.save()

            if created:
                logger.info(
                    f"새로운 시장 지수 [{index_name}]가 데이터베이스에 추가되었습니다."
                )
            else:
                logger.info(f"시장 지수 [{index_name}]가 업데이트되었습니다.")

        except Exception as e:
            logger.error(f"[{index_name}] 시장 지수 DB 업데이트 중 오류 발생: {e}")
            continue

    logger.info("시장 지수 업데이트 작업이 완료되었습니다.")


scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")


def start_scheduler():
    """
    스케줄러를 시작하고, 시장 지수 업데이트 작업을 등록합니다.
    앱 준비 시 호출됩니다.
    """
    try:
        # 스케줄러가 이미 실행 중이고, 작업이 이미 등록되어 있을 수 있으므로,
        # 중복 실행을 피하기 위해 명시적으로 시작하기 전에 상태를 확인하거나,
        # add_job의 replace_existing=True에 의존합니다.
        # Django 개발 서버는 리로딩 시 여러번 실행될 수 있으므로 주의가 필요합니다.
        # 실제 운영 환경에서는 uWSGI 등의 --lazy-apps 옵션으로 한번만 실행되도록 보장하는 것이 좋습니다.

        # 기존 작업 확인 (선택적: 더 강력한 제어를 원할 경우)
        # if scheduler.get_job('update_market_indices_job') is not None:
        #     logger.info("이미 'update_market_indices_job' 작업이 스케줄러에 존재합니다.")
        # else:
        scheduler.add_job(
            update_market_indices_job,
            trigger="interval",
            minutes=1,
            # hours=1,  # 매 1시간마다 실행
            id="update_market_indices_job",
            replace_existing=True,
            misfire_grace_time=60,  # 작업이 지연되었을 때 1시간 내에는 실행
        )
        logger.info(
            "시장 지수 업데이트 작업이 스케줄러에 등록되었습니다 (매 시간 실행)."
        )

        if not scheduler.running:
            scheduler.start()
            logger.info("스케줄러를 시작합니다.")
        # else:
        # logger.info("스케줄러가 이미 실행 중입니다.") # 이미 실행중이면 시작하지 않음

    except Exception as e:
        logger.error(f"스케줄러 시작 또는 작업 등록 중 오류 발생: {e}")


def schedule_market_indices_update():
    """
    매일 오전 9시에 시장 지수 업데이트 작업을 스케줄링.
    """
