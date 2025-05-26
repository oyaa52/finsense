import openai
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.core.cache import cache  # Django 캐시 임포트
from datetime import date  # 오늘 날짜를 알기 위해 임포트

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

        # 사용 가능한 상품 정보를 간단한 문자열로 변환
        products_description = "\n".join(
            [
                f"- 상품명: {p.get('name', 'N/A')}, 특징: {p.get('description', 'N/A')}"
                for p in available_products[:5]  # 최대 5개 상품 정보만 포함
            ]
        )

        # GPT에게 전달할 프롬프트 구성
        prompt_messages = [
            {
                "role": "system",
                "content": "당신은 사용자의 재정 상황과 목표에 맞는 금융 상품을 추천하는 전문 금융 어드바이저입니다. 사용자의 투자 및 저축 목적을 파악하고, 사용자의 현재 정보를 바탕으로 구체적이고 실질적인 상품을 추천 및 조언을 해주세요.",
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
                """,
            },
        ]

        completion = client.chat.completions.create(
            model="gpt-4o",
            messages=prompt_messages,
            temperature=0.7,
            max_tokens=1000,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

        if completion.choices and len(completion.choices) > 0:
            return completion.choices[0].message.content.strip()
        else:
            return "잠시 후 다시 시도해주세요."

    except openai.APIConnectionError as e:
        print(f"OpenAI API 연결 오류: {e}")
        return "서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요."
    except openai.RateLimitError as e:
        print(f"OpenAI API 요청 제한 초과: {e}")
        return "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
    except openai.APIStatusError as e:
        print(f"OpenAI API 오류: {e.status_code} - {e.response}")
        return f"오류가 발생했습니다 (오류 코드: {e.status_code}). 요청 내용을 확인해주세요."
    except Exception as e:
        print(f"GPT 추천 생성 중 예기치 않은 오류 발생: {e}")
        return "추천 생성 중 오류가 발생했습니다. 관리자에게 문의해주세요."


#  YouTube API 함수
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


def search_youtube_financial_videos(query, max_results=5):
    """
    YouTube API를 사용하여 금융 관련 주제로 영상을 검색합니다.
    이 함수는 get_popular_financial_videos에서 fallback으로 사용됩니다.
    """
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY,
        )

        search_response = (
            youtube.search()
            .list(
                q=f"{query} 금융 경제 투자 재테크",
                part="snippet",
                maxResults=max_results,
                type="video",
                relevanceLanguage="ko",
                regionCode="KR",
            )
            .execute()
        )

        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_data = {
                    "video_id": search_result["id"]["videoId"],
                    "title": search_result["snippet"]["title"],
                    "description": search_result["snippet"]["description"],
                    "thumbnail_url": search_result["snippet"]["thumbnails"]["default"][
                        "url"
                    ],
                    "channel_id": search_result["snippet"]["channelId"],
                    "channel_title": search_result["snippet"]["channelTitle"],
                    "publish_time": search_result["snippet"][
                        "publishTime"
                    ],  # YouTube API 'search' 엔드포인트는 'publishTime'을 반환
                }
                videos.append(video_data)

        return videos

    except HttpError as e:
        error_details = e.resp.status, e._get_reason()
        print(
            f"YouTube API HTTP 오류 발생 (search_youtube_financial_videos): {error_details}"
        )
        if e.resp.status == 403:
            return "YouTube API 요청 할당량을 초과했거나 API 키에 문제가 있습니다."
        return "YouTube API에서 오류가 발생했습니다."
    except Exception as e:
        print(
            f"YouTube 영상 검색 중 예기치 않은 오류 발생 (search_youtube_financial_videos): {e}"
        )
        return "YouTube 영상 검색 중 오류가 발생했습니다. 관리자에게 문의해주세요."


def get_youtube_videos(query, max_results=6, page_token=None):
    """
    YouTube API를 사용하여 영상을 검색합니다 (페이지네이션 지원).
    경제 뉴스 검색 기능에서 사용됩니다.
    데이터는 하루 동안 캐시됩니다.
    """
    # page_token이 None일 경우를 대비해 빈 문자열로 처리하여 캐시 키 일관성 유지
    page_token_str = page_token if page_token else ""
    cache_key = f"youtube_videos_{query}_{max_results}_{page_token_str}"

    cached_data = cache.get(cache_key)
    if cached_data:
        print(
            f"[CACHE] Returning youtube videos from cache for key: {cache_key}"
        )
        return cached_data
    
    print(
        f"[API] Fetching youtube videos from YouTube API for key: {cache_key}"
    )
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
        if page_token:
            search_params["pageToken"] = page_token

        search_response = youtube.search().list(**search_params).execute()

        videos = []
        for search_result in search_response.get("items", []):
            if search_result["id"]["kind"] == "youtube#video":
                video_data = {
                    "video_id": search_result["id"]["videoId"],
                    "title": search_result["snippet"]["title"],
                    "description": search_result["snippet"]["description"],
                    "thumbnail_url": search_result["snippet"]["thumbnails"]["medium"][
                        "url"
                    ],  # 경제 뉴스에서는 medium 사용
                    "channel_id": search_result["snippet"]["channelId"],
                    "channel_title": search_result["snippet"]["channelTitle"],
                    "publish_time": search_result["snippet"][
                        "publishTime"
                    ],  # YouTube API 'search' 엔드포인트는 'publishTime'을 반환
                }
                videos.append(video_data)

        actual_total_results = search_response.get("pageInfo", {}).get(
            "totalResults", 0
        )

        result_data = {
            "videos": videos,
            "nextPageToken": search_response.get("nextPageToken"),
            "prevPageToken": search_response.get("prevPageToken"),
            "totalResults": min(
                actual_total_results, 100
            ),
            "resultsPerPage": search_response.get("pageInfo", {}).get("resultsPerPage"),
            "error": None,
        }

        # 캐시 저장 (만료 시간: 24시간)
        if not result_data.get("error"): # API 에러가 없을 때만 캐시 저장
            cache.set(cache_key, result_data, timeout=60 * 60 * 24)
            print(f"[CACHE] Saved youtube videos to cache for key: {cache_key}")

        return result_data

    except HttpError as e:
        error_details = e.resp.status, e._get_reason()
        print(f"YouTube API HTTP 오류 발생 (get_youtube_videos): {error_details}")
        error_message = "YouTube API에서 오류가 발생했습니다."
        if e.resp.status == 403:
            error_message = (
                "YouTube API 요청 할당량을 초과했거나 API 키에 문제가 있습니다."
            )
        return {
            "error": error_message,
            "videos": [],
            "nextPageToken": None,
            "prevPageToken": None,
            "totalResults": 0,
            "resultsPerPage": 0,
        }
    except Exception as e:
        print(f"YouTube 영상 검색 중 예기치 않은 오류 발생 (get_youtube_videos): {e}")
        return {
            "error": "YouTube 영상 검색 중 오류가 발생했습니다. 관리자에게 문의해주세요.",
            "videos": [],
            "nextPageToken": None,
            "prevPageToken": None,
            "totalResults": 0,
            "resultsPerPage": 0,
        }


def get_popular_financial_videos(max_results=2):
    """
    YouTube API를 사용하여 인기 동영상 중 '금융' 관련 영상을 가져옵니다.
    결과가 부족할 경우 일반 '금융' 검색을 통해 추가로 영상을 확보합니다.
    메인 페이지에 금융 관련 인기 영상 2개를 표시하는 데 사용됩니다.
    데이터는 하루 동안 캐시됩니다.
    """
    today_str = date.today().isoformat()
    cache_key = f"popular_financial_videos_{today_str}_{max_results}"

    cached_data = cache.get(cache_key)
    if cached_data:
        print(
            f"[CACHE] Returning popular financial videos from cache for key: {cache_key}"
        )
        return cached_data

    print(
        f"[API] Fetching popular financial videos from YouTube API for key: {cache_key}"
    )
    try:
        youtube = build(
            YOUTUBE_API_SERVICE_NAME,
            YOUTUBE_API_VERSION,
            developerKey=settings.YOUTUBE_API_KEY,
        )

        # 카테고리 기반 인기 동영상 필터링 (현재는 "과학 및 기술" 카테고리 ID "28" 사용)
        # current_category_id = "28" # 또는 None으로 설정하여 전체 카테고리 대상
        # 특정 카테고리 ID를 사용하지 않고 전체 인기 동영상에서 필터링하도록 None으로 설정
        current_category_id = None

        request_params = {
            "part": "snippet,contentDetails,statistics",  # contentDetails(길이), statistics(조회수) 포함
            "chart": "mostPopular",
            "regionCode": "KR",
            "maxResults": 50,  # 내부 필터링을 위해 충분한 수의 인기 동영상을 가져옴 (최대 50개)
        }
        if (
            current_category_id
        ):  # current_category_id가 None이 아닐 경우에만 파라미터 추가
            request_params["videoCategoryId"] = current_category_id

        response = youtube.videos().list(**request_params).execute()

        processed_videos = []
        # 메인 페이지용 키워드 (이전 요청에 따라 ["금융", "적금", "투자", "주식"] 사용)
        keywords = ["금융", "적금", "투자", "주식"]

        for item in response.get("items", []):
            title = item.get("snippet", {}).get("title", "").lower()
            description = item.get("snippet", {}).get("description", "").lower()
            tags = [tag.lower() for tag in item.get("snippet", {}).get("tags", [])]

            is_financial_video = False
            for keyword in keywords:
                if keyword in title or keyword in description or keyword in tags:
                    is_financial_video = True
                    break

            if is_financial_video:
                video_data = {
                    "video_id": item["id"],
                    "title": item["snippet"]["title"],
                    "description": item["snippet"]["description"],
                    "thumbnail_url": item["snippet"]["thumbnails"]["medium"][
                        "url"
                    ],  # 메인에서는 medium 썸네일 사용
                    "channel_id": item["snippet"]["channelId"],
                    "channel_title": item["snippet"]["channelTitle"],
                    "publish_time": item["snippet"].get(
                        "publishedAt"
                    ),  # videos.list는 'publishedAt' 반환
                    "duration": item.get("contentDetails", {}).get("duration"),
                    "view_count": item.get("statistics", {}).get("viewCount"),
                }
                processed_videos.append(video_data)

        # 조회수 높은 순으로 정렬 후, 요청된 max_results 만큼 선택
        sorted_videos = sorted(
            processed_videos,
            key=lambda x: int(
                x.get("view_count", 0) or 0
            ),  # view_count가 없는 경우 0으로 처리
            reverse=True,
        )

        result_videos = sorted_videos[:max_results]

        # 요청된 영상 개수(max_results)보다 결과가 적으면, 일반 검색으로 추가 확보
        if len(result_videos) < max_results:
            needed_more = max_results - len(result_videos)
            existing_video_ids = {v["video_id"] for v in result_videos}

            fallback_query = "금융"  # fallback 검색 시 사용할 기본 키워드

            # search_youtube_financial_videos는 오류 시 문자열을 반환할 수 있음
            # 중복 가능성을 고려하여 필요한 개수보다 조금 더 요청
            fallback_search_results = search_youtube_financial_videos(
                fallback_query, max_results=needed_more + 5
            )

            if isinstance(fallback_search_results, list):
                for video in fallback_search_results:
                    if len(result_videos) >= max_results:
                        break
                    if video["video_id"] not in existing_video_ids:
                        # search_youtube_financial_videos의 결과에는 duration, view_count가 없을 수 있음.
                        # API 할당량 절약을 위해 여기서는 추가 API 호출 없이, 없는 정보는 None으로 채움.
                        result_videos.append(
                            {
                                "video_id": video["video_id"],
                                "title": video["title"],
                                "description": video["description"],
                                "thumbnail_url": video[
                                    "thumbnail_url"
                                ],  # search_youtube_financial_videos는 default 썸네일 반환
                                "channel_id": video["channel_id"],
                                "channel_title": video["channel_title"],
                                # search_youtube_financial_videos는 'publishTime', 여기서는 'publishedAt'과 호환되도록 처리
                                "publish_time": video.get("publish_time")
                                or video.get("publishedAt"),
                                "duration": None,
                                "view_count": None,
                            }
                        )
                        existing_video_ids.add(video["video_id"])

        final_result = {"videos": result_videos[:max_results], "error": None}
        # 캐시 저장 (만료 시간: 24시간)
        # 하루가 지나면 자동으로 캐시가 만료되지만, 정확히 자정에 맞추려면
        # cache.set(cache_key, final_result, timeout=remaining_seconds_till_midnight()) 같은 방식도 고려 가능
        cache.set(cache_key, final_result, timeout=60 * 60 * 24)
        print(f"[CACHE] Saved popular financial videos to cache for key: {cache_key}")
        return final_result

    except HttpError as e:
        error_details = e.resp.status, e._get_reason()
        print(
            f"YouTube API HTTP 오류 발생 (get_popular_financial_videos): {error_details}"
        )
        error_message = "YouTube API에서 오류가 발생했습니다."
        if e.resp.status == 403:
            error_message = (
                "YouTube API 요청 할당량을 초과했거나 API 키에 문제가 있습니다."
            )
        # API 오류 발생 시 캐시하지 않음
        return {"error": error_message, "videos": []}
    except Exception as e:
        print(
            f"인기 금융 영상 검색 중 예기치 않은 오류 발생 (get_popular_financial_videos): {e}"
        )
        # API 오류 발생 시 캐시하지 않음
        return {
            "error": "인기 금융 영상 검색 중 오류가 발생했습니다. 관리자에게 문의해주세요.",
            "videos": [],
        }
