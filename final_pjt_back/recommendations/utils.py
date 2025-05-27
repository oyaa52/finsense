import openai
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.core.cache import cache  # Django 캐시 임포트
from datetime import date  # 오늘 날짜를 알기 위해 임포트
import logging # 로깅 모듈 임포트

logger = logging.getLogger(__name__) # 로거 인스턴스 생성

# OpenAI GPT를 사용하여 사용자 프로필 및 상품 목록 기반 금융 상품 추천 생성
# user_profile (dict): 사용자 프로필 정보 (age, occupation, monthly_income 등)
# available_products (list of dict): 추천 대상 금융 상품 목록 (name, description 등)
# 반환값 (str): GPT 생성 추천 텍스트 또는 사용자 친화적 오류 메시지
def get_financial_recommendations_from_gpt(user_profile, available_products):
    try:
        # OpenAI API 클라이언트 초기화
        client = openai.OpenAI(api_key=settings.GPT_API_KEY)

        # 추천 대상 상품 정보를 간단한 문자열로 변환 (최대 5개)
        products_description = "\n".join(
            [
                f"- 상품명: {p.get('name', 'N/A')}, 특징: {p.get('description', 'N/A')}"
                for p in available_products[:5]
            ]
        )

        # GPT API에 전달할 프롬프트 메시지 구성
        prompt_messages = [
            {
                "role": "system", # 시스템 역할: GPT의 페르소나 및 지침 정의
                "content": "당신은 사용자의 재정 상황과 목표에 맞는 금융 상품을 추천하는 전문 금융 어드바이저입니다. 사용자의 투자 및 저축 목적을 파악하고, 사용자의 현재 정보를 바탕으로 구체적이고 실질적인 상품을 추천 및 조언을 해주세요.",
            },
            {
                "role": "user", # 사용자 역할: 실제 사용자 데이터 및 요청 사항 전달
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
                """,
            },
        ]
        
        logger.info(f"OpenAI GPT 추천 요청 시작: 사용자 ID (알 수 없음 - user_profile에서 가져와야 함)") # 사용자 ID 로깅 추가 필요
        # OpenAI Chat Completions API 호출
        completion = client.chat.completions.create(
            model="gpt-4o",             # 사용할 모델
            messages=prompt_messages,   # 프롬프트 메시지
            temperature=0.7,            # 응답의 다양성 (0.0 ~ 1.0)
            max_tokens=1000,            # 최대 응답 토큰 수
            top_p=1.0,                  # 다음 토큰 선택 시 고려할 확률 분포의 누적 상위 %
            frequency_penalty=0.0,      # 반복적인 단어 사용 억제
            presence_penalty=0.0,       # 새로운 주제 도입 장려
        )

        if completion.choices and len(completion.choices) > 0:
            recommendation_text = completion.choices[0].message.content.strip()
            logger.info(f"OpenAI GPT 추천 생성 성공. 응답 길이: {len(recommendation_text)}")
            return recommendation_text
        else:
            logger.warning("OpenAI GPT 추천 응답이 비어있습니다.")
            return "추천 정보를 생성하지 못했습니다. 잠시 후 다시 시도해주세요."

    except openai.APIConnectionError as e:
        logger.error(f"OpenAI API 연결 오류: {e}", exc_info=True)
        return "OpenAI 서비스 연결에 실패했습니다. 네트워크 상태를 확인해주세요."
    except openai.RateLimitError as e:
        logger.error(f"OpenAI API 요청 제한 초과: {e}", exc_info=True)
        return "OpenAI 서비스 요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
    except openai.APIStatusError as e:
        logger.error(f"OpenAI API 상태 오류: {e.status_code} - {e.response}", exc_info=True)
        return f"OpenAI 서비스에서 오류가 발생했습니다 (오류 코드: {e.status_code}). 요청 내용을 확인하거나 잠시 후 다시 시도해주세요."
    except Exception as e:
        logger.error(f"GPT 추천 생성 중 예기치 않은 오류 발생: {e}", exc_info=True)
        return "추천 생성 중 시스템 오류가 발생했습니다. 관리자에게 문의해주세요."


# YouTube API 관련 상수
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# YouTube API를 사용하여 금융 관련 주제로 동영상 검색 (get_popular_financial_videos의 fallback으로 사용)
# query (str): 검색어
# max_results (int): 반환할 최대 결과 수
# 반환값 (list of dict 또는 str): 동영상 정보 리스트 또는 오류 메시지 문자열
def search_youtube_financial_videos(query, max_results=5):
    logger.info(f"YouTube 일반 검색 시작: query='{query}', max_results={max_results}")
    try:
        # YouTube API 서비스 빌드
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY,
        )

        # YouTube Search API 요청 파라미터 설정
        search_response = (
            youtube.search()
            .list(
                q=f"{query} 금융 경제 투자 재테크", # 검색어에 금융 관련 키워드 추가
                part="snippet",                 # 반환할 정보 부분 (기본 정보)
                maxResults=max_results,         # 결과 수
                type="video",                   # 검색 타입 (동영상)
                relevanceLanguage="ko",         # 관련성 높은 언어 (한국어)
                regionCode="KR",                # 지역 코드 (대한민국)
            )
            .execute()
        )

        videos = [] # 검색된 동영상 정보를 담을 리스트
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_data = {
                    "video_id": search_result["id"]["videoId"],
                    "title": search_result["snippet"]["title"],
                    "description": search_result["snippet"]["description"],
                    "thumbnail_url": search_result["snippet"]["thumbnails"]["default"]["url"], # 기본 썸네일
                    "channel_id": search_result["snippet"]["channelId"],
                    "channel_title": search_result["snippet"]["channelTitle"],
                    "publish_time": search_result["snippet"]["publishTime"], # search API는 'publishTime' 반환
                }
                videos.append(video_data)
        logger.info(f"YouTube 일반 검색 성공: {len(videos)}개 동영상 반환.")
        return videos

    except HttpError as e:
        error_status = e.resp.status
        error_reason = e._get_reason()
        logger.error(f"YouTube API HTTP 오류 (search_youtube_financial_videos): Status {error_status}, Reason: {error_reason}", exc_info=True)
        if error_status == 403:
            return "YouTube API 요청 할당량을 초과했거나 API 키 인증에 문제가 있습니다."
        return f"YouTube API 서비스에서 오류가 발생했습니다 (상태: {error_status})."
    except Exception as e:
        logger.error(f"YouTube 영상 검색 중 예기치 않은 오류 (search_youtube_financial_videos): {e}", exc_info=True)
        return "YouTube 영상 검색 중 시스템 오류가 발생했습니다. 관리자에게 문의해주세요."

# YouTube API를 사용하여 동영상 검색 (페이지네이션 지원, 경제 뉴스 검색용, 하루 캐시)
# query (str): 검색어
# max_results (int): 페이지당 결과 수
# page_token (str, optional): 다음/이전 페이지 토큰
# 반환값 (dict): 'videos', 'nextPageToken', 'prevPageToken', 'totalResults', 'resultsPerPage', 'error' 키를 포함한 딕셔너리
def get_youtube_videos(query, max_results=6, page_token=None):
    page_token_str = page_token if page_token else "" # 캐시 키 일관성을 위한 page_token 처리
    cache_key = f"youtube_videos_paginated_{query}_{max_results}_{page_token_str}"
    
    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug(f"[CACHE HIT] YouTube 검색 결과 반환 (paginated): key='{cache_key}'")
        return cached_data
    
    logger.info(f"[API CALL] YouTube 검색 실행 (paginated): query='{query}', max_results={max_results}, page_token='{page_token_str}'")
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY,
        )

        search_params = {
            "q": query,
            "part": "snippet",
            "maxResults": max_results,
            "type": "video",
            "relevanceLanguage": "ko",
            "regionCode": "KR",
        }
        if page_token: # 페이지 토큰이 있으면 파라미터에 추가
            search_params["pageToken"] = page_token

        search_response = youtube.search().list(**search_params).execute()

        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_data = {
                    "video_id": search_result["id"]["videoId"],
                    "title": search_result["snippet"]["title"],
                    "description": search_result["snippet"]["description"],
                    "thumbnail_url": search_result["snippet"]["thumbnails"]["medium"]["url"], # 경제 뉴스에서는 medium 썸네일 사용
                    "channel_id": search_result["snippet"]["channelId"],
                    "channel_title": search_result["snippet"]["channelTitle"],
                    "publish_time": search_result["snippet"]["publishTime"],
                }
                videos.append(video_data)

        actual_total_results = search_response.get("pageInfo", {}).get("totalResults", 0)
        # YouTube API는 totalResults를 매우 큰 값으로 반환할 수 있으나, 실제 접근 가능한 페이지는 제한적임. (여기서는 100개로 임의 제한)
        display_total_results = min(actual_total_results, 100) 

        result_data = {
            "videos": videos, # 현재 페이지 동영상 목록
            "nextPageToken": search_response.get("nextPageToken"), # 다음 페이지 토큰
            "prevPageToken": search_response.get("prevPageToken"), # 이전 페이지 토큰 (API에서 기본 제공 안함, 필요시 직접 구현)
            "totalResults": display_total_results, # 표시용 전체 결과 수 (API 값 또는 제한된 값)
            "resultsPerPage": search_response.get("pageInfo", {}).get("resultsPerPage"), # 페이지당 결과 수
            "error": None, # 오류 메시지 (성공 시 None)
        }
        
        # 오류가 없을 경우에만 결과 캐시 (24시간)
        cache.set(cache_key, result_data, timeout=60 * 60 * 24)
        logger.debug(f"[CACHE SET] YouTube 검색 결과 저장 (paginated): key='{cache_key}'")
        return result_data

    except HttpError as e:
        error_status = e.resp.status
        error_reason = e._get_reason()
        logger.error(f"YouTube API HTTP 오류 (get_youtube_videos): Status {error_status}, Reason: {error_reason}", exc_info=True)
        error_message = "YouTube API에서 오류가 발생했습니다."
        if error_status == 403:
            error_message = "YouTube API 요청 할당량을 초과했거나 API 키 인증에 문제가 있습니다."
        return { "error": error_message, "videos": [], "nextPageToken": None, "prevPageToken": None, "totalResults": 0, "resultsPerPage": 0, }
    except Exception as e:
        logger.error(f"YouTube 영상 검색 중 예기치 않은 오류 (get_youtube_videos): {e}", exc_info=True)
        return { "error": "YouTube 영상 검색 중 시스템 오류가 발생했습니다. 관리자에게 문의해주세요.", "videos": [], "nextPageToken": None, "prevPageToken": None, "totalResults": 0, "resultsPerPage": 0, }

# YouTube 인기 동영상 중 금융 관련 영상 조회 (메인 페이지용, 하루 캐시)
# max_results (int): 최종적으로 반환할 영상 수
# 반환값 (dict): 'videos', 'error' 키를 포함한 딕셔너리
def get_popular_financial_videos(max_results=2):
    today_str = date.today().isoformat() # 캐시 키용 오늘 날짜 문자열
    cache_key = f"popular_financial_videos_{today_str}_{max_results}"

    cached_data = cache.get(cache_key)
    if cached_data:
        logger.debug(f"[CACHE HIT] 인기 금융 영상 반환: key='{cache_key}'")
        return cached_data

    logger.info(f"[API CALL] 인기 금융 영상 조회 시작: max_results={max_results}")
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY,
        )

        # 1. YouTube 인기 동영상 목록 가져오기 (videos().list API 사용)
        # videoCategoryId: 특정 카테고리 지정 가능 (예: "10" 음악, "28" 과학기술). None이면 전체 카테고리.
        # 현재는 특정 카테고리 ID를 사용하지 않고 전체 인기 동영상에서 필터링 (current_category_id = None)
        current_category_id = None 
        request_params = {
            "part": "snippet,contentDetails,statistics", # snippet(기본정보), contentDetails(길이), statistics(조회수) 요청
            "chart": "mostPopular",                     # 인기 동영상 차트
            "regionCode": "KR",                         # 지역: 대한민국
            "maxResults": 50,                           # 내부 필터링을 위해 충분히 많은 수(최대 50)를 가져옴
        }
        if current_category_id: # 카테고리 ID가 있으면 파라미터에 추가
            request_params["videoCategoryId"] = current_category_id

        response = youtube.videos().list(**request_params).execute()

        processed_videos = [] # 금융 관련 필터링된 동영상 목록
        # 금융 관련 키워드 목록 (제목, 설명, 태그에서 검색)
        keywords = ["금융", "경제", "투자", "주식", "재테크", "펀드", "부동산", "코인", "금리", "환율", "예금", "적금", "대출"]

        for item in response.get("items", []):
            snippet = item.get("snippet", {})
            title = snippet.get("title", "").lower()
            description = snippet.get("description", "").lower()
            tags = [tag.lower() for tag in snippet.get("tags", [])]

            is_financial_video = False # 금융 관련 영상 여부 플래그
            for keyword in keywords:
                if keyword in title or keyword in description or keyword in " ".join(tags): # 태그는 공백으로 합쳐서 검색
                    is_financial_video = True
                    break
            
            if is_financial_video:
                video_data = {
                    "video_id": item["id"],
                    "title": snippet["title"],
                    "description": snippet.get("description"), # 원본 설명
                    "thumbnail_url": snippet.get("thumbnails", {}).get("medium", {}).get("url"), # medium 썸네일
                    "channel_id": snippet.get("channelId"),
                    "channel_title": snippet.get("channelTitle"),
                    "publish_time": snippet.get("publishedAt"), # videos.list API는 'publishedAt' 반환
                    "duration": item.get("contentDetails", {}).get("duration"), # ISO 8601 형식 (예: PT1M30S)
                    "view_count": item.get("statistics", {}).get("viewCount"), # 조회수
                }
                processed_videos.append(video_data)
        
        logger.info(f"인기 동영상 중 {len(processed_videos)}개의 금융 관련 영상 필터링 완료.")

        # 2. 필터링된 금융 관련 영상을 조회수 높은 순으로 정렬
        sorted_videos = sorted(
            processed_videos,
            key=lambda x: int(x.get("view_count", 0) or 0), # view_count가 없거나 None이면 0으로 처리
            reverse=True,
        )
        result_videos = sorted_videos[:max_results] # 요청된 개수만큼 선택

        # 3. 결과 영상 수가 부족하면, 일반 검색(search_youtube_financial_videos)으로 추가 확보 (fallback)
        if len(result_videos) < max_results:
            needed_more = max_results - len(result_videos)
            logger.info(f"인기 금융 영상 부족 ({len(result_videos)}/{max_results}). 일반 검색으로 {needed_more}개 추가 확보 시도.")
            existing_video_ids = {v["video_id"] for v in result_videos} # 중복 방지를 위한 ID 집합
            
            # fallback 검색은 좀 더 일반적인 키워드 사용
            fallback_query = "경제 금융 뉴스" 
            # 필요한 개수보다 조금 더 요청 (중복 및 오류 가능성 대비)
            fallback_search_results = search_youtube_financial_videos(
                fallback_query, max_results=needed_more + 5 
            )

            if isinstance(fallback_search_results, list): # 오류 없이 리스트가 반환된 경우
                for video in fallback_search_results:
                    if len(result_videos) >= max_results: # 필요한 개수만큼 채워졌으면 중단
                        break
                    if video["video_id"] not in existing_video_ids: # 중복 영상이 아니면 추가
                        # search_youtube_financial_videos 결과에는 duration, view_count가 없음
                        # API 할당량 절약을 위해 여기서는 추가 API 호출 없이, 없는 정보는 None으로 채움
                        result_videos.append({
                            "video_id": video["video_id"],
                            "title": video["title"],
                            "description": video["description"],
                            "thumbnail_url": video["thumbnail_url"], # search_youtube_financial_videos는 default 썸네일 반환
                            "channel_id": video["channel_id"],
                            "channel_title": video["channel_title"],
                            "publish_time": video.get("publish_time") or video.get("publishedAt"), # 호환성
                            "duration": None, # fallback 결과에는 없음
                            "view_count": None, # fallback 결과에는 없음
                        })
                        existing_video_ids.add(video["video_id"])
                logger.info(f"Fallback 검색 후 총 {len(result_videos)}개의 영상 확보.")
            else: # fallback 검색에서 오류 발생(문자열 반환) 시
                logger.warning(f"Fallback 검색(search_youtube_financial_videos) 중 오류 발생: {fallback_search_results}")


        final_result = {"videos": result_videos[:max_results], "error": None}
        
        # 결과 캐시 (24시간)
        cache.set(cache_key, final_result, timeout=60 * 60 * 24)
        logger.debug(f"[CACHE SET] 인기 금융 영상 저장: key='{cache_key}'")
        return final_result

    except HttpError as e:
        error_status = e.resp.status
        error_reason = e._get_reason()
        logger.error(f"YouTube API HTTP 오류 (get_popular_financial_videos): Status {error_status}, Reason: {error_reason}", exc_info=True)
        error_message = "YouTube API에서 오류가 발생했습니다."
        if error_status == 403:
            error_message = "YouTube API 요청 할당량을 초과했거나 API 키 인증에 문제가 있습니다."
        return {"error": error_message, "videos": []}
    except Exception as e:
        logger.error(f"인기 금융 영상 검색 중 예기치 않은 오류 (get_popular_financial_videos): {e}", exc_info=True)
        return {"error": "인기 금융 영상 검색 중 시스템 오류가 발생했습니다. 관리자에게 문의해주세요.", "videos": []}
