import requests
from bs4 import BeautifulSoup
import re

def get_market_indices():
    """
    네이버 금융에서 코스피, 코스닥 지수를 크롤링하여 반환합니다.
    Returns:
        list: 각 지수 정보를 담은 딕셔너리의 리스트.
              예: [{'name': 'KOSPI', 'value': 2700.00, 'change': 5.23, 'rate': 0.19}, ...]
              오류 발생 시 빈 리스트 반환.
    """
    indices_data = []
    urls = {
        'KOSPI': 'https://finance.naver.com/sise/sise_index.naver?code=KOSPI',
        'KOSDAQ': 'https://finance.naver.com/sise/sise_index.naver?code=KOSDAQ',
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for index_name, url in urls.items():
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            now_value_element = soup.select_one('#now_value')
            quotient_div = soup.select_one('div#quotient')

            if not now_value_element or not quotient_div:
                # print(f"[{index_name}] 지수 값(#now_value) 또는 기준 div(#quotient)를 찾을 수 없습니다. HTML 구조를 확인해주세요.")
                # print(f"Debug: now_value_element is None? {now_value_element is None}")
                # print(f"Debug: quotient_div is None? {quotient_div is None}")
                # if quotient_div:
                #      print(f"Debug: quotient_div HTML: {str(quotient_div)}")
                # elif now_value_element:
                #      print(f"Debug: now_value_element's parent HTML: {str(now_value_element.parent)}")
                continue

            current_value = float(now_value_element.text.replace(',', ''))

            change_info_span = quotient_div.select_one('span#change_value_and_rate')
            if not change_info_span:
                # print(f"[{index_name}] 변동 정보 상세(span#change_value_and_rate)를 찾을 수 없습니다.")
                # print(f"Debug: quotient_div HTML for {index_name}: {str(quotient_div)}")
                continue

            change_status_text = "보합"
            quotient_classes = quotient_div.get('class', [])
            if 'up' in quotient_classes:
                change_status_text = "상승"
            elif 'down' in quotient_classes:
                change_status_text = "하락"
            elif 'keep' in quotient_classes:
                change_status_text = "보합"
            
            blind_span = change_info_span.select_one('span.blind')
            if blind_span and blind_span.text in ["상승", "하락", "보합"]:
                change_status_text = blind_span.text.strip()

            change_value_raw_element = change_info_span.find('span', recursive=False)
            if not change_value_raw_element :
                 change_value_raw_element = change_info_span.find('span')

            if not change_value_raw_element:
                # print(f"[{index_name}] 변동 값(숫자)을 포함하는 span 요소를 change_info_span 내부에서 찾을 수 없습니다.")
                # print(f"Debug: change_info_span HTML: {str(change_info_span)}")
                continue
            
            change_value_str = change_value_raw_element.text.strip().replace(',', '')
            change_value = float(change_value_str)

            if change_status_text == "하락":
                change_value *= -1
            elif change_status_text == "보합":
                change_value = 0.0
            
            full_text_in_change_info = change_info_span.text
            text_for_rate = full_text_in_change_info.replace(change_value_raw_element.text, "")
            if blind_span:
                text_for_rate = text_for_rate.replace(blind_span.text, "")
            
            rate_text_with_percent = text_for_rate.strip()

            match_rate = re.search(r"([+-]?[\d.]+%)", rate_text_with_percent)
            if not match_rate:
                # print(f"[{index_name}] 등락률 파싱 실패: '{rate_text_with_percent}' (원본: '{full_text_in_change_info}')")
                # print(f"Debug: change_value_raw_element.text: {change_value_raw_element.text}")
                # if blind_span: print(f"Debug: blind_span.text: {blind_span.text}")
                change_rate = 0.0
            else:
                change_rate_str = match_rate.group(1).replace('%', '').replace('+', '')
                change_rate = float(change_rate_str)
                if change_status_text == "하락" and change_rate > 0:
                    change_rate *= -1
                elif change_status_text == "상승" and change_rate < 0:
                    change_rate *= -1

            indices_data.append({
                'name': index_name,
                'value': current_value,
                'change': change_value,
                'rate': change_rate,
            })
            # print(f"Successfully crawled {index_name}: value={current_value}, change={change_value}, rate={change_rate} (status: {change_status_text})")

        except requests.exceptions.RequestException as e:
            print(f"[{index_name}] 요청 중 오류 발생: {e}") # 실제 운영시에는 로깅 등으로 대체
        except AttributeError as e:
            print(f"[{index_name}] HTML 요소 접근 중 오류 (구조 변경 가능성): {e}") # 실제 운영시에는 로깅 등으로 대체
        except ValueError as e:
            print(f"[{index_name}] 데이터 변환 중 오류: {e}") # 실제 운영시에는 로깅 등으로 대체
        except Exception as e:
            print(f"[{index_name}] 알 수 없는 오류 발생: {e}") # 실제 운영시에는 로깅 등으로 대체
            
    return indices_data

if __name__ == '__main__':
    data = get_market_indices()
    if data:
        for item in data:
            print(item)
    # else:
    #     print("데이터를 가져오지 못했습니다.")
