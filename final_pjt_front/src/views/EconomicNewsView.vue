<template>
  <div class="economic-news-container" data-aos="fade-up">
    <div class="search-section">
      <h2 class="section-title">경제 뉴스 검색</h2>
      <p class="search-guide">원하시는 검색어 입력 시 금융 관련 내용만 찾아서 보여드립니다.</p>
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="관심 있는 경제 키워드를 입력하세요 (예: 금리, 주식, 부동산, 환율 등)"
          @keyup.enter="handleSearch"
          :disabled="isLoading"
        />
        <button @click="handleSearch" :disabled="isLoading">
          {{ isLoading && currentPage === 1 ? '검색 중...' : (isLoading ? '로딩 중...' : '검색') }}
        </button>
      </div>
    </div>

    <div v-if="isLoading && youtubeVideos.length === 0 && currentPage === 1" class="loading-indicator">
      <div class="spinner"></div>
      <p>경제 뉴스를 검색 중입니다...</p>
    </div>

    <div v-if="error && youtubeVideos.length === 0" class="error-message">
      <p>{{ error }}</p>
      <button v-if="searchQuery.trim()" @click="handleSearch" class="retry-button">다시 검색</button>
    </div>

    <div v-if="youtubeVideos.length > 0" class="youtube-results">
      <h3 v-if="initialSearchPerformed && totalResults > 0" class="results-title">
        '{{ searchQuery }}' (금융 경제 뉴스) 관련 영상
      </h3>
      <div class="youtube-grid">
        <div v-for="video in youtubeVideos" :key="video.video_id" class="youtube-video-item" data-aos="zoom-in-up">
          <div class="video-thumbnail-wrapper">
            <img :src="video.thumbnail" :alt="video.title" class="video-thumbnail" @click="openVideoModal(video.video_id)"/>
            <button class="play-button" @click="openVideoModal(video.video_id)">&#9658;</button>
          </div>
          <h4 class="video-title" :title="video.title" @click="openVideoModal(video.video_id)">{{ video.title }}</h4>
          <p class="video-channel">{{ video.channel_title }}</p>
          <p class="video-publish-time">{{ formatPublishTime(video.publish_time) }}</p>
        </div>
      </div>
      
      <div v-if="totalPages > 0" class="pagination-controls">
        <button @click="goToPrevPage" :disabled="isLoading || currentPage === 1" class="prev-button">
          이전
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }} 페이지</span>
        <button @click="goToNextPage" :disabled="isLoading || !nextPageToken" class="next-button">
          다음
        </button>
      </div>
    </div>

    <div v-if="!isLoading && initialSearchPerformed && youtubeVideos.length === 0 && !error" class="no-results">
      <p>'{{ searchQuery }}' (금융 경제 뉴스) 관련 검색 결과가 없습니다.</p>
      <p>다른 키워드로 검색해보세요.</p>
    </div>

    <!-- Video Modal -->
    <div v-if="selectedVideoId" class="video-modal-overlay" @click.self="closeVideoModal">
      <div class="video-modal-content">
        <button class="close-modal-button" @click="closeVideoModal">&times;</button>
        <iframe 
          :src="`https://www.youtube.com/embed/${selectedVideoId}?autoplay=1`" 
          frameborder="0" 
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen>
        </iframe>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: 'EconomicNewsView'
}
</script>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
// import { useAuthStore } from '@/stores/authStore'
import AOS from 'aos'
import 'aos/dist/aos.css'
import { useRouter } from 'vue-router'

// const authStore = useAuthStore()
const searchQuery = ref('')
const youtubeVideos = ref([])
const isLoading = ref(false)
const error = ref(null)

const nextPageToken = ref(null)
const prevPageTokens = ref([])
const totalResults = ref(0)
const resultsPerPage = ref(6)
const currentPage = ref(1)

const initialSearchPerformed = ref(false)
const selectedVideoId = ref(null)

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/recommendations/youtube/economic-news/'
const FIXED_KEYWORDS = '금융 경제 뉴스'

const totalPages = computed(() => {
  if (totalResults.value === 0) return 0
  return Math.ceil(totalResults.value / resultsPerPage.value)
})

const fetchVideos = async (pageNavigationToken = null, isNewSearch = false) => {
  if (isNewSearch) {
    youtubeVideos.value = []
    nextPageToken.value = null
    prevPageTokens.value = []
    currentPage.value = 1
    initialSearchPerformed.value = true
    selectedVideoId.value = null
  }

  if (!searchQuery.value.trim()) {
    if (isNewSearch) {
      error.value = '검색어를 입력해주세요.'
      youtubeVideos.value = []
      initialSearchPerformed.value = false
    }
    return
  }
  
  isLoading.value = true
  if(isNewSearch) error.value = null;

  const effectiveQuery = `${searchQuery.value.trim()} ${FIXED_KEYWORDS}`.trim()

  try {
    const params = {
      query: effectiveQuery,
      max_results: resultsPerPage.value,
    }
    if (pageNavigationToken) {
      params.pageToken = pageNavigationToken
    }

    const response = await axios.get(API_BASE_URL, {
      params,
    })

    if (response.data && response.data.videos) {
      youtubeVideos.value = response.data.videos
      
      if (nextPageToken.value && pageNavigationToken === nextPageToken.value) {
          // prevPageTokens.value.push(currentPageTokenForPrev);
      }

      nextPageToken.value = response.data.nextPageToken || null
      totalResults.value = response.data.totalResults || youtubeVideos.value.length
      
      if (response.data.error) {
        error.value = response.data.error
      } else {
        if(response.data.videos.length === 0 && isNewSearch) {
          // 결과 없음 메시지 표시 (템플릿에서 처리)
        } else {
          error.value = null
        }
      }
    } else {
      error.value = response.data.error || '데이터 형식이 올바르지 않거나 영상을 불러오는데 실패했습니다.'
    }

  } catch (err) {
    console.error('영상 검색 중 오류:', err)
    if (err.response && err.response.data && err.response.data.error) {
        error.value = err.response.data.error
    } else if (err.message) {
        error.value = err.message
    } else {
        error.value = '영상 검색 중 오류가 발생했습니다.'
    }
  } finally {
    isLoading.value = false
  }
}

const handleSearch = () => {
  fetchVideos(null, true)
}

const goToNextPage = () => {
  if (nextPageToken.value && !isLoading.value) {
    currentPage.value++
    fetchVideos(nextPageToken.value, false)
  }
}

const goToPrevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchVideos(null, true);
  }
}

const router = useRouter()

const openVideoModal = (videoId) => {
  router.push({ name: 'videoDetail', params: { videoId: videoId } });
}

const closeVideoModal = () => {
  selectedVideoId.value = null
}

const formatPublishTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  AOS.init();
})

</script>

<style scoped>
.economic-news-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  color: #333;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px; /* 가이드 문구와의 간격 조정 */
  color: #4a90e2; /* 포인트 색상 */
}

.search-section {
  background-color: #f8f9fa; /* 배경색 변경 */
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08); /* 그림자 강화 */
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 15px; /* 간격 증가 */
}

.search-box input {
  flex: 1;
  padding: 12px 18px;
  border: 1px solid #ced4da; /* 테두리 색상 변경 */
  border-radius: 8px;
  font-size: 1rem;
  background-color: #fff; /* 입력 필드 배경 흰색 */
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.search-box input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2);
}

.search-box button {
  padding: 12px 25px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.search-box button:hover:not(:disabled) {
  background-color: #357abd;
  transform: translateY(-1px);
}

.search-box button:disabled {
  background-color: #adb5bd; /* 비활성 색상 변경 */
  cursor: not-allowed;
}

.loading-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  margin-top: 20px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3; /* Light grey */
  border-top: 5px solid #4a90e2; /* Blue */
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-indicator p {
  font-size: 1.1rem;
  color: #555;
}

.error-message {
  background-color: #ffebee; /* 붉은 계열 배경 */
  color: #c62828; /* 어두운 붉은색 텍스트 */
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #ef9a9a; /* 연한 붉은색 테두리 */
  display: flex;
  flex-direction: column; /* 버튼과 메시지 수직 정렬 */
  align-items: center;
  gap: 10px;
}

.retry-button {
  padding: 8px 15px;
  background-color: #c62828;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: #ad1414;
}

.youtube-results {
  margin-top: 30px;
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.youtube-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 한 줄에 2개씩 */
  gap: 25px; /* 간격 증가 */
}

.youtube-video-item {
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.youtube-video-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.12);
}

.video-thumbnail-wrapper {
  position: relative;
  width: 100%;
  aspect-ratio: 16/9;
  background-color: #000; /* 썸네일 로딩 중 배경 */
}

.video-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block; /* 불필요한 공백 제거 */
}

.play-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  border: none;
  border-radius: 50%;
  width: 60px;
  height: 60px;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease, transform 0.3s ease;
  opacity: 0.8;
}

.youtube-video-item:hover .play-button {
  transform: translate(-50%, -50%) scale(1.1);
  background-color: rgba(0, 0, 0, 0.8);
  opacity: 1;
}

.video-info {
  padding: 15px;
  flex-grow: 1; /* 제목, 채널 등이 공간을 채우도록 */
  display: flex;
  flex-direction: column;
}

.video-title {
  margin: 0 0 8px 0;
  padding: 0 15px; /* 패딩 조정 */
  font-size: 1rem;
  font-weight: 600; /* 제목 강조 */
  color: #222;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  flex-grow: 1; /* 제목이 가능한 많은 공간 차지 */
}

.youtube-video-item:hover .video-title {
  color: #4a90e2;
}

.video-channel, .video-publish-time {
  font-size: 0.85rem;
  color: #555;
  margin: 0 15px 5px 15px; /* 패딩 조정 */
  line-height: 1.3;
}

.video-publish-time {
  margin-bottom: 10px; /* 하단 패딩 역할 */
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  padding-bottom: 20px;
}

.prev-button, .next-button {
  padding: 10px 20px; /* 패딩 조정 */
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem; /* 폰트 크기 조정 */
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.prev-button:hover:not(:disabled),
.next-button:hover:not(:disabled) {
  background-color: #357abd;
  transform: translateY(-1px);
}

.prev-button:disabled,
.next-button:disabled {
  background-color: #adb5bd;
  cursor: not-allowed;
}

.page-info {
  margin: 0 15px; /* 간격 조정 */
  font-size: 0.95rem; /* 폰트 크기 조정 */
  color: #333;
  font-weight: 500;
}

.no-results {
  text-align: center;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  margin-top: 20px;
}

.no-results p {
  color: #555;
  font-size: 1.1rem;
  margin-bottom: 10px;
}

/* Video Modal Styles */
.video-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.75);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000; /* 다른 요소 위에 오도록 */
}

.video-modal-content {
  position: relative;
  background-color: #000;
  padding: 0; /* iframe이 꽉 차도록 패딩 제거 */
  border-radius: 8px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  width: 80%;
  max-width: 960px; 
  aspect-ratio: 16/9;
}

.video-modal-content iframe {
  display: block; /* 불필요한 공백 제거 */
  width: 100%;
  height: 100%;
  border-radius: 8px; /* iframe에도 radius 적용 */
}

.close-modal-button {
  position: absolute;
  top: -40px; /* 모달 바깥 위로 조금 이동 */
  right: -5px;
  background: none;
  border: none;
  color: white;
  font-size: 30px;
  font-weight: bold;
  cursor: pointer;
  padding: 5px;
  line-height: 1;
  transition: color 0.2s ease;
}
.close-modal-button:hover {
  color: #ccc;
}

.search-guide {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 15px;
  text-align: left; /* 가이드 문구 왼쪽 정렬 */
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }
  .search-box input, .search-box button {
    width: 100%;
  }
  .youtube-grid {
    grid-template-columns: 1fr;
  }
  .results-title {
    font-size: 1.3rem;
  }
  .video-modal-content {
    width: 95%;
  }
  .close-modal-button {
    top: -30px;
    right: 0px;
    font-size: 24px;
  }
}
</style> 