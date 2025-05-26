from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import MarketIndex
from .serializers import MarketIndexSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
def get_latest_market_indices(request):
    """
    데이터베이스에 저장된 최신 KOSPI 및 KOSDAQ 지수 정보를 반환합니다.
    """
    try:
        kospi = MarketIndex.objects.filter(name='KOSPI').order_by('-last_updated').first()
        kosdaq = MarketIndex.objects.filter(name='KOSDAQ').order_by('-last_updated').first()

        data_to_serialize = []
        if kospi:
            data_to_serialize.append(kospi)
        if kosdaq:
            data_to_serialize.append(kosdaq)

        if not data_to_serialize:
            logger.info("요청된 시장 지수 정보가 DB에 아직 없습니다.")
            return Response([], status=200)

        serializer = MarketIndexSerializer(data_to_serialize, many=True)
        return Response(serializer.data)

    except Exception as e:
        logger.error(f"최신 시장 지수 API 요청 처리 중 오류 발생: {e}")
        return Response({"error": "지수 정보를 가져오는 중 서버에서 오류가 발생했습니다."}, status=500) 