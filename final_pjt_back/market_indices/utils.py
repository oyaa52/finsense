import requests
from bs4 import BeautifulSoup
import re
import logging # 로깅 모듈 임포트

logger = logging.getLogger(__name__) # 로거 인스턴스 생성

# 네이버 금융에서 KOSPI, KOSDAQ 지수 정보를 크롤링하여 반환
def get_market_indices():
    # 반환값: 각 지수 정보를 담은 딕셔너리 리스트 (오류 시 빈 리스트)
    # 예: [{'name': 'KOSPI', 'value': 2700.00, 'change': 5.23, 'rate': 0.19}, ...]
    indices_data = []
    # 크롤링 대상 URL 딕셔너리 (지수명: URL)
    urls = {
        'KOSPI': 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI',
        'KOSDAQ': 'https://finance.naver.com/sise/sise_index.naver?code=KOSDAQ',
    }

    # 요청 헤더 (User-Agent 설정으로 차단 방지)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for index_name, url in urls.items():
        try:
            # 웹 페이지 요청 (timeout 10초)
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() # HTTP 오류 발생 시 예외 발생
            soup = BeautifulSoup(response.text, 'html.parser') # HTML 파싱

            # 현재 지수 값 요소 선택
            now_value_element = soup.select_one('#now_value')
            # 전일비, 등락률 포함하는 부모 요소 선택
            quotient_div = soup.select_one('div#quotient')

            if not now_value_element or not quotient_div:
                logger.warning(f"[{index_name}] 지수 값(#now_value) 또는 기준 div(#quotient)를 찾을 수 없습니다. HTML 구조 변경 가능성이 있습니다.")
                continue

            # 현재 지수 값 추출 및 형 변환 (쉼표 제거)
            current_value = float(now_value_element.text.replace(',', ''))

            # 전일비 및 등락률 상세 정보 포함하는 span 요소 선택
            change_info_span = quotient_div.select_one('span#change_value_and_rate')
            if not change_info_span:
                logger.warning(f"[{index_name}] 변동 정보 상세(span#change_value_and_rate)를 찾을 수 없습니다. HTML 구조 변경 가능성이 있습니다.")
                continue

            # 등락 상태 텍스트 초기화 (기본: 보합)
            change_status_text = "보합"
            quotient_classes = quotient_div.get('class', []) # 부모 div의 class 속성으로 1차 판단
            if 'up' in quotient_classes:
                change_status_text = "상승"
            elif 'down' in quotient_classes:
                change_status_text = "하락"
            # 'keep' 클래스는 네이버 금융에서 명시적으로 사용하지 않을 수 있음, blind span으로 재확인
            
            # 더 정확한 등락 상태는 내부 blind span 텍스트로 확인
            blind_span = change_info_span.select_one('span.blind')
            if blind_span and blind_span.text in ["상승", "하락", "보합"]:
                change_status_text = blind_span.text.strip()

            # 전일비 값(숫자)을 포함하는 span 요소 탐색
            # 바로 다음 자식 span을 우선 찾고, 없으면 내부의 첫번째 span을 찾음
            change_value_raw_element = change_info_span.find('span', recursive=False)
            if not change_value_raw_element:
                 change_value_raw_element = change_info_span.find('span') # 내부의 모든 span 중 첫번째

            if not change_value_raw_element:
                logger.warning(f"[{index_name}] 전일비 값(숫자) span 요소를 찾을 수 없습니다. HTML 구조 변경 가능성이 있습니다.")
                continue
            
            # 전일비 값 추출 및 부호 처리
            change_value_str = change_value_raw_element.text.strip().replace(',', '')
            change_value = float(change_value_str)

            if change_status_text == "하락":
                change_value *= -1 # 하락 시 음수로
            elif change_status_text == "보합":
                change_value = 0.0 # 보합 시 0
            
            # 등락률 추출 로직 (전체 텍스트에서 전일비 값, blind 텍스트 제거 후 정규표현식 사용)
            full_text_in_change_info = change_info_span.text
            text_for_rate = full_text_in_change_info.replace(change_value_raw_element.text, "")
            if blind_span:
                text_for_rate = text_for_rate.replace(blind_span.text, "")
            
            rate_text_with_percent = text_for_rate.strip()

            # 정규표현식으로 등락률 숫자 부분 추출 (예: "+0.25%", "-1.3%", "0.0%")
            match_rate = re.search(r"([+-]?[\d.]+%)", rate_text_with_percent)
            if not match_rate:
                logger.warning(f"[{index_name}] 등락률 파싱 실패. 텍스트: '{rate_text_with_percent}'. HTML 구조 변경 가능성이 있습니다.")
                change_rate = 0.0 # 파싱 실패 시 0.0으로 처리
            else:
                change_rate_str = match_rate.group(1).replace('%', '').replace('+', '') # %, + 기호 제거
                change_rate = float(change_rate_str)
                # 등락 상태와 부호 일치 작업 (가끔 네이버 HTML에서 부호가 다를 수 있음)
                if change_status_text == "하락" and change_rate > 0:
                    change_rate *= -1
                elif change_status_text == "상승" and change_rate < 0:
                    change_rate *= -1 # 실제로는 양수여야 함
                elif change_status_text == "보합":
                    change_rate = 0.0

            indices_data.append({
                'name': index_name,
                'value': current_value,
                'change': change_value,
                'rate': change_rate,
            })
            logger.info(f"크롤링 성공: {index_name} - 값: {current_value}, 변동: {change_value}, 비율: {change_rate}% (상태: {change_status_text})")

        except requests.exceptions.Timeout:
            logger.error(f"[{index_name}] 요청 시간 초과 (Timeout): {url}", exc_info=True)
        except requests.exceptions.RequestException as e:
            logger.error(f"[{index_name}] 요청 중 오류 발생: {url} - {e}", exc_info=True)
        except AttributeError as e:
            logger.error(f"[{index_name}] HTML 요소 접근 중 오류 (구조 변경 가능성): {url} - {e}", exc_info=True)
        except ValueError as e:
            logger.error(f"[{index_name}] 데이터 변환 중 오류 (숫자 형식 등): {url} - {e}", exc_info=True)
        except Exception as e:
            logger.error(f"[{index_name}] 알 수 없는 오류 발생: {url} - {e}", exc_info=True)
            
    return indices_data

# 아래 if __name__ == '__main__': 블록은 Django 앱 컨텍스트와 무관하게
# 이 파일을 직접 실행할 때만 사용되는 테스트 코드이므로, 일반적으로는 제거하거나
# Django management command로 분리하는 것이 좋습니다. 여기서는 제거합니다.
