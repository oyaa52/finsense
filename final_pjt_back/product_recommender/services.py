from django.db.models import Q
from products.models import DepositProduct, SavingProduct
import openai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class ProductRecommender:
    def __init__(self, user):
        self.user = user
        self.profile = user.profile
        openai.api_key = settings.GPT_API_KEY
        
    def get_gpt_recommendation(self, product_info):
        """GPT를 사용하여 상품 추천 이유를 생성합니다."""
        try:
            prompt = f"""
            다음 사용자 프로필과 금융상품 정보를 바탕으로 맞춤형 추천 이유를 생성해주세요.
            
            사용자 프로필:
            - 투자 성향: {self.profile.investment_tendency}
            - 투자 기간: {self.profile.investment_term}개월
            - 투자 가능 금액: {self.profile.amount_available}원
            
            상품 정보:
            - 상품명: {product_info['name']}
            - 상품 유형: {product_info['type']}
            - 최고 금리: {product_info['max_rate']}%
            - 가입 기간: {product_info['term']}개월
            
            다음 형식으로 응답해주세요:
            1. 상품의 주요 장점
            2. 사용자 프로필과의 적합성
            3. 예상 수익률과 수익금 (가능하다면)
            4. 투자 시 고려사항 (리스크 포함)
            5. 간단한 금융 조언
            """
            
            logger.info(f"GPT 추천 이유 생성 요청: 사용자 ID {self.user.id}, 상품명 {product_info.get('name')}")
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "당신은 금융 전문 상담가입니다.\n"
                            "사용자가 제공한 프로필 정보(투자 가능 금액, 현재 자산, 투자 성향, 투자 기간, 투자 목적, 직업 등)를 바탕으로, "
                            "사용자에게 적합한 예적금 상품, 투자 상품, 주식, 포트폴리오 구성을 추천하고, "
                            "해당 추천이 어떻게 투자 목적을 달성할 수 있는지 구체적으로 설명해 주세요.\n"
                            "리스크 설명도 포함해 주세요.\n"
                            "마지막에는 향후 금융 행동에 대한 간단한 조언도 함께 주세요.\n\n"
                            "사용자 프로필은 다음과 같습니다:\n"
                            "• 투자 가능 금액: [예: 1,000만 원]\n"
                            "• 현재 자산: [예: 3,000만 원]\n"
                            "• 투자 성향: [예: 안정형 / 중립형 / 공격형]\n"
                            "• 투자 기간: [예: 3년]\n"
                            "• 투자 목적: [예: 결혼 자금 마련]\n"
                            "• 직업: [예: 공무원]\n"
                            "• 기타 특이사항: [예: 월 50만 원 자동이체 가능]"
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            recommendation_text = response.choices[0].message.content.strip()
            logger.info(f"GPT 추천 이유 생성 완료. 사용자 ID {self.user.id}, 상품명 {product_info.get('name')}, 응답 길이: {len(recommendation_text)}")
            return recommendation_text
            
        except Exception as e:
            logger.error(f"GPT API 호출 중 오류 발생 (get_gpt_recommendation): {e}", exc_info=True)
            logger.warning(f"GPT API 실패로 기본 추천 이유 생성. 사용자 ID {self.user.id}, 상품명 {product_info.get('name')}")
            return self._get_recommendation_reason(product_info, 0, product_info.get('type'))
        
    def calculate_deposit_score(self, product: DepositProduct):
        """예금 상품 점수 계산"""
        score = 0
        
        # 금리 점수 (최대 40점)
        max_rate = float(product.max_rate) if product.max_rate else 0.0
        score += min(max_rate * 4, 40)
        
        # 투자 성향 점수 (최대 30점)
        if self.profile.investment_tendency == 'stable':
            score += 30
        elif self.profile.investment_tendency == 'stable_seeking':
            score += 25
        elif self.profile.investment_tendency == 'neutral':
            score += 20
        elif self.profile.investment_tendency == 'aggressive':
            score += 15
            
        # 투자 기간 점수 (최대 20점)
        term = int(self.profile.investment_term)
        if term == 6:
            score += 10
        elif term == 12:
            score += 15
        elif term == 24:
            score += 20
        elif term == 36:
            score += 20
            
        # 금액 점수 (최대 10점)
        if self.profile.amount_available >= product.min_amount:
            score += 10
            
        return score
        
    def calculate_saving_score(self, product: SavingProduct):
        """적금 상품 점수 계산"""
        score = 0
        
        # 금리 점수 (최대 40점)
        max_rate = float(product.max_rate) if product.max_rate else 0.0
        score += min(max_rate * 4, 40)
        
        # 투자 성향 점수 (최대 30점)
        if self.profile.investment_tendency == 'stable':
            score += 25
        elif self.profile.investment_tendency == 'stable_seeking':
            score += 30
        elif self.profile.investment_tendency == 'neutral':
            score += 25
        elif self.profile.investment_tendency == 'aggressive':
            score += 20
            
        # 투자 기간 점수 (최대 20점)
        term = int(self.profile.investment_term)
        if term == 6:
            score += 10
        elif term == 12:
            score += 15
        elif term == 24:
            score += 20
        elif term == 36:
            score += 20
            
        # 금액 점수 (최대 10점)
        if self.profile.amount_available >= product.min_amount:
            score += 10
            
        return score
        
    def get_recommendations(self, limit=5):
        """추천 상품 목록 조회"""
        recommendations = []
        
        logger.info(f"금융 상품 추천 시작: 사용자 ID {self.user.id}, 요청 개수 {limit}")

        # 예금 상품 점수 계산
        deposit_products = DepositProduct.objects.all()
        logger.info(f"총 {deposit_products.count()}개의 예금 상품에 대해 점수 계산 및 추천 이유 생성 중...")
        for product in deposit_products:
            score = self.calculate_deposit_score(product)
            if score > 0:
                product_info = {
                    'name': product.name,
                    'type': 'deposit',
                    'max_rate': product.max_rate,
                    'term': product.term
                }
                
                # GPT를 사용하여 추천 이유 생성
                recommendation_reason = self.get_gpt_recommendation(product_info)
                
                recommendations.append({
                    'product_name': product.name,
                    'product_type': 'deposit',
                    'score': round(score, 1),
                    'max_rate': product.max_rate,
                    'term': f"{product.term}개월",
                    'reason': recommendation_reason,
                    'deposit_product': {
                        'id': product.id,
                        'name': product.name,
                        'max_rate': product.max_rate,
                        'term': product.term
                    }
                })
        
        # 적금 상품 점수 계산
        saving_products = SavingProduct.objects.all()
        logger.info(f"총 {saving_products.count()}개의 적금 상품에 대해 점수 계산 및 추천 이유 생성 중...")
        for product in saving_products:
            score = self.calculate_saving_score(product)
            if score > 0:
                product_info = {
                    'name': product.name,
                    'type': 'saving',
                    'max_rate': product.max_rate,
                    'term': product.term
                }
                
                # GPT를 사용하여 추천 이유 생성
                recommendation_reason = self.get_gpt_recommendation(product_info)
                
                recommendations.append({
                    'product_name': product.name,
                    'product_type': 'saving',
                    'score': round(score, 1),
                    'max_rate': product.max_rate,
                    'term': f"{product.term}개월",
                    'reason': recommendation_reason,
                    'saving_product': {
                        'id': product.id,
                        'name': product.name,
                        'max_rate': product.max_rate,
                        'term': product.term
                    }
                })
        
        # 점수 기준으로 정렬하고 상위 N개 반환
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        logger.info(f"총 {len(recommendations)}개의 추천 생성. 상위 {limit}개 반환.")
        return recommendations[:limit]
        
    def _get_recommendation_reason(self, product_info, score, product_type):
        """기본 추천 이유 생성 (GPT API 실패 시 사용)"""
        reasons = []
        
        # 금리 관련 이유
        max_rate_value = float(product_info.get('max_rate', 0))
        if max_rate_value >= 4.0:
            reasons.append("높은 금리를 제공합니다.")
        elif max_rate_value >= 3.0:
            reasons.append("비교적 좋은 금리를 제공합니다.")
            
        # 투자 성향 관련 이유
        if product_type == 'deposit':
            if self.profile.investment_tendency in ['stable', 'stable_seeking']:
                reasons.append("안정적인 투자를 선호하는 성향에 적합합니다.")
        elif product_type == 'saving':
            if self.profile.investment_tendency in ['stable_seeking', 'neutral']:
                reasons.append("꾸준히 목돈을 마련하려는 성향에 적합합니다.")
            
        # 기간 관련 이유
        product_term_str = str(product_info.get('term', ''))
        user_term_months = int(self.profile.investment_term)
        
        if product_term_str.isdigit():
            product_term_months = int(product_term_str)
            if user_term_months == product_term_months:
                reasons.append(f"선호하시는 {user_term_months}개월 투자 기간과 일치합니다.")
            elif abs(user_term_months - product_term_months) <= 6:
                reasons.append(f"선호하시는 투자 기간과 유사한 {product_term_months}개월 상품입니다.")
        
        if not reasons:
            return f"{product_info.get('name', '이 상품')}은(는) 관심을 가져볼 만한 상품입니다."
            
        return ", ".join(reasons) + " 등의 장점이 있습니다." 