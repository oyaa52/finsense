from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MarketIndex
from .serializers import MarketIndexSerializer
import logging

logger = logging.getLogger(__name__)

# DB에 저장된 최신 KOSPI 및 KOSDAQ 지수 정보 반환
# GET /api/market-indices/latest/
@api_view(['GET'])
def get_latest_market_indices(request):
    try:
        # 각 지수별로 마지막 업데이트된 데이터 조회
        kospi = MarketIndex.objects.filter(name='KOSPI').order_by('-last_updated').first()
        kosdaq = MarketIndex.objects.filter(name='KOSDAQ').order_by('-last_updated').first()

        data_to_serialize = [] # 직렬화할 데이터를 담을 리스트
        if kospi:
            data_to_serialize.append(kospi)
        if kosdaq:
            data_to_serialize.append(kosdaq)

        # 조회된 지수 정보가 없는 경우 (DB에 데이터가 아직 없는 초기 상태 등)
        if not data_to_serialize:
            logger.info("요청된 시장 지수(KOSPI, KOSDAQ) 정보가 데이터베이스에 존재하지 않습니다.")
            return Response([], status=200) # 빈 리스트와 200 OK 반환 (의도된 동작)

        # 조회된 지수 정보 직렬화
        serializer = MarketIndexSerializer(data_to_serialize, many=True)
        return Response(serializer.data)

    except Exception as e:
        # API 처리 중 예기치 않은 오류 발생 시 로깅 및 500 오류 응답
        logger.error(f"최신 시장 지수 API(/api/market-indices/latest/) 요청 처리 중 오류 발생: {e}", exc_info=True)
        return Response({"error": "최신 지수 정보를 가져오는 중 서버 내부 오류가 발생했습니다."}, status=500) 