import openai
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# OpenAI API 클라이언트 초기화

def get_financial_recommendations_from_gpt(user_profile, available_products):
    """
    사용자 프로필과 금융 상품 목록을 기반으로 OpenAI GPT를 사용하여 금융 상품 추천을 받습니다.

    :param user_profile: dict, 사용자 프로필 정보 (예: 나이, 소득, 투자 성향 등)
    :param available_products: list of dict, 추천 대상 금융 상품 목록
    :return: str, GPT가 생성한 추천 텍스트 또는 오류 메시지
    """
    try:
        client = openai.OpenAI(api_key=settings.GPT_API_KEY)

        # 사용 가능한 상품 정보를 간단한 문자열로 변환 (더 정교하게 구성해야 함)
        products_description = "\n".join([
            f"- 상품명: {p.get('name', 'N/A')}, 특징: {p.get('description', 'N/A')}" 
            for p in available_products[:5] # 최대 5개 상품 정보만 포함
        ])

        # GPT에게 전달할 프롬프트 구성
        prompt_messages = [
            {
                "role": "system",
                "content": "당신은 사용자의 재정 상황과 목표에 맞는 금융 상품을 추천하는 전문 금융 어드바이저입니다. 사용자의 투자 및 저축 목적을 파악하고, 사용자의 현재 정보를 바탕으로 구체적이고 실질적인 상품을 추천 및 조언을 해주세요."
            },
            {
                "role": "user",
                "content": f"""
                다음은 제 프로필 정보입니다:
                - 나이: {user_profile.get('age', '제공되지 않음')}
                - 직업: {user_profile.get('occupation', '제공되지 않음')}
                - 월 소득: {user_profile.get('monthly_income', '제공되지 않음')} 원
                - 투자 목표: {user_profile.get('investment_purpose', '제공되지 않음')}
                - 투자 가능 기간: {user_profile.get('investment_term', '제공되지 않음')}
                - 투자 성향: {user_profile.get('investment_tendency', '제공되지 않음')}

                추천 가능한 금융 상품 목록은 다음과 같습니다:
                {products_description}

                위 정보를 바탕으로 저에게 가장 적합한 금융 상품 2-3가지와 그 이유를 설명해주세요.
                만약 정보가 부족하다면 어떠한 정보를 프로필에 추가해야 하는지 알려주세요.
                """
            }
        ]

        # OpenAI API 호출 (ChatCompletion 사용)
        # 모델은 필요에 따라 변경가능
        completion = client.chat.completions.create(
            model="gpt-4o", # 또는 "gpt-4o"
            messages=prompt_messages,
            temperature=0.7, # 답변의 창의성 (0.0 ~ 2.0)
            max_tokens=1000,  # 최대 응답 길이
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # 추천 결과 반환
        if completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content.strip()
        else:
            return "잠시 후 다시 시도해주세요."

    except openai.APIConnectionError as e:
        # 네트워크 연결 문제
        print(f"OpenAI API 연결 오류: {e}")
        return "서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요."
    except openai.RateLimitError as e:
        # API 요청 제한 초과
        print(f"OpenAI API 요청 제한 초과: {e}")
        return "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
    except openai.APIStatusError as e:
        # API 관련 기타 오류 (예: 인증 오류, 잘못된 요청 등)
        print(f"OpenAI API 오류: {e.status_code} - {e.response}")
        return f"오류가 발생했습니다 (오류 코드: {e.status_code}). 요청 내용을 확인해주세요."
    except Exception as e:
        # 기타 예외 처리
        print(f"GPT 추천 생성 중 예기치 않은 오류 발생: {e}")
        return "추천 생성 중 오류가 발생했습니다. 관리자에게 문의해주세요."


#  YouTube API 함수 
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

def search_youtube_financial_videos(query, max_results=5):
    """
    YouTube API를 사용하여 금융 관련 주제로 영상을 검색

    :param query: str, 검색할 키워드 (예: "주식 투자 방법", "금리 인상 영향")
    :param max_results: int, 가져올 최대 결과 수
    :return: list of dict, 검색된 영상 정보 리스트 또는 오류 시 빈 리스트
    """
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                        developerKey=settings.YOUTUBE_API_KEY)

        # 검색 실행
        # part='snippet'은 영상의 기본 정보(제목, 설명, 썸네일 등)를 가져옴.
        # q에는 검색어, type='video'는 동영상만 검색하도록 함.
        # relevanceLanguage와 regionCode는 검색 결과의 관련성을 높이는 데 도움이 될 수 있음.
        # 금융 관련 필터링을 위해서는 검색어(query) 자체를 정교하게 구성하는 것이 중요.

        search_response = youtube.search().list(
            q=f"{query} 금융 경제 투자 재테크", # 검색어에 금융 관련 키워드 추가하여 관련성 높임.
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='ko', # 한국어 영상 우선
            regionCode='KR'       # 한국 지역 결과 우선
        ).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                video_data = {
                    'video_id': search_result['id']['videoId'],
                    'title': search_result['snippet']['title'],
                    'description': search_result['snippet']['description'],
                    'thumbnail_url': search_result['snippet']['thumbnails']['default']['url'],
                    'channel_id': search_result['snippet']['channelId'],
                    'channel_title': search_result['snippet']['channelTitle'],
                    'publish_time': search_result['snippet']['publishTime']
                }
                videos.append(video_data)
        
        return videos

    except HttpError as e:
        # Google API HTTP 오류 처리
        error_details = e.resp.status, e._get_reason()
        print(f"YouTube API HTTP 오류 발생: {error_details}")
        if e.resp.status == 403: # 할당량 초과 또는 API 키 관련 문제일 가능성
            return "YouTube API 요청 할당량을 초과했거나 API 키에 문제가 있습니다."
        return "YouTube API에서 오류가 발생했습니다."
    except Exception as e:
        # 기타 예외 처리
        print(f"YouTube 영상 검색 중 예기치 않은 오류 발생: {e}")
        return "YouTube 영상 검색 중 오류가 발생했습니다. 관리자에게 문의해주세요."

def get_youtube_videos(query, max_results=6, page_token=None):
    """
    YouTube API를 사용하여 영상을 검색 (페이지네이션 지원)

    :param query: str, 검색할 키워드
    :param max_results: int, 가져올 최대 결과 수 (기본값: 6)
    :param page_token: str, 특정 페이지를 요청하기 위한 토큰
    :return: dict, 검색된 영상 정보 및 페이지네이션 정보 포함
    """
    try:
        youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, 
                        developerKey=settings.YOUTUBE_API_KEY)

        search_params = {
            'q': query,
            'part': 'snippet',
            'maxResults': max_results,
            'type': 'video',
            'relevanceLanguage': 'ko',
            'regionCode': 'KR'
        }
        if page_token:
            search_params['pageToken'] = page_token

        search_response = youtube.search().list(**search_params).execute()

        videos = []
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                video_data = {
                    'video_id': search_result['id']['videoId'],
                    'title': search_result['snippet']['title'],
                    'description': search_result['snippet']['description'],
                    'thumbnail_url': search_result['snippet']['thumbnails']['medium']['url'],
                    'channel_id': search_result['snippet']['channelId'],
                    'channel_title': search_result['snippet']['channelTitle'],
                    'publish_time': search_result['snippet']['publishTime']
                }
                videos.append(video_data)
        
        actual_total_results = search_response.get('pageInfo', {}).get('totalResults', 0)

        return {
            'videos': videos,
            'nextPageToken': search_response.get('nextPageToken'),
            'prevPageToken': search_response.get('prevPageToken'), 
            'totalResults': min(actual_total_results, 100), # 실제 totalResults와 100 중 작은 값을 사용
            'resultsPerPage': search_response.get('pageInfo', {}).get('resultsPerPage'),
            'error': None # 성공 시 에러 없음 명시
        }

    except HttpError as e:
        error_details = e.resp.status, e._get_reason()
        print(f"YouTube API HTTP 오류 발생 (get_youtube_videos): {error_details}")
        error_message = "YouTube API에서 오류가 발생했습니다."
        if e.resp.status == 403:
            error_message = "YouTube API 요청 할당량을 초과했거나 API 키에 문제가 있습니다."
        # 일관된 반환 형식 유지
        return {'error': error_message, 'videos': [], 'nextPageToken': None, 'prevPageToken': None, 'totalResults': 0, 'resultsPerPage': 0}
    except Exception as e:
        print(f"YouTube 영상 검색 중 예기치 않은 오류 발생 (get_youtube_videos): {e}")
        # 일관된 반환 형식 유지
        return {'error': "YouTube 영상 검색 중 오류가 발생했습니다. 관리자에게 문의해주세요.", 'videos': [], 'nextPageToken': None, 'prevPageToken': None, 'totalResults': 0, 'resultsPerPage': 0}


