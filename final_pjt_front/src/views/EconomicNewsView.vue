<template>
  <div class="economic-news-container">
    <div class="search-section">
      <h2 class="section-title">금융 영상 검색</h2>
      <p class="search-guide">원하시는 검색어 입력 시 금융 관련 내용만 찾아서 보여드립니다.</p>
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="관심 있는 금융 키워드를 입력하세요 (예: 금리, 주식, 부동산, 환율 등)"
          @keyup.enter="handleSearch"
          :disabled="isLoadingAllData"
        />
        <button @click="handleSearch" :disabled="isLoadingAllData">
          {{ isLoadingAllData ? '검색 중...' : '검색' }}
        </button>
      </div>
    </div>

    <div v-if="isLoadingAllData && currentVideos.length === 0" class="loading-indicator">
      <div class="spinner"></div>
      <p>금융 영상을 검색 중입니다...</p>
    </div>

    <div v-if="error && currentVideos.length === 0" class="error-message">
      <p>{{ error }}</p>
      <button v-if="displayedSearchQuery.trim()" @click="handleSearch" class="retry-button">다시 검색</button>
    </div>

    <div v-if="currentVideos.length > 0" class="youtube-results">
      <h3 v-if="initialSearchPerformed && totalResults > 0" class="results-title">
        '{{ displayedSearchQuery }}' 관련 영상 (총 {{ totalResults }}개)
      </h3>
      <div class="youtube-grid">
        <div v-for="video in currentVideos" :key="video.video_id" class="youtube-video-item">
          <div class="video-thumbnail-wrapper">
            <img :src="video.thumbnail_url" :alt="video.title" class="video-thumbnail" @click="openVideoModal(video.video_id)"/>
            <button class="play-button" @click="openVideoModal(video.video_id)">&#9658;</button>
          </div>
          <h4 class="video-title" :title="video.title" @click="openVideoModal(video.video_id)">{{ video.title }}</h4>
          <p class="video-channel">{{ video.channel_title }}</p>
          <p class="video-publish-time">{{ formatPublishTime(video.publish_time) }}</p>
        </div>
      </div>
      
      <div v-if="totalPages > 1" class="pagination-controls">
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1" class="prev-button">
          이전
        </button>
        <span v-for="page in displayedPageNumbers" :key="page.text"
              @click="page.clickable ? goToPage(page.number) : null"
              :class="{ 'page-number': true, 'current-page': page.number === currentPage, 'disabled': !page.clickable }">
          {{ page.text }}
        </span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages" class="next-button">
          다음
        </button>
      </div>
    </div>

    <div v-if="!isLoadingAllData && initialSearchPerformed && currentVideos.length === 0 && !error" class="no-results">
      <p>'{{ displayedSearchQuery }}' 관련 검색 결과가 없습니다.</p>
      <p>다른 키워드로 검색해보세요.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'EconomicNewsView'
}
</script>

<script setup>
import { ref, computed, onMounted, onActivated, nextTick, watch } from 'vue'
import axios from 'axios'
// import { useAuthStore } from '@/stores/authStore'
// import AOS from 'aos'
// import 'aos/dist/aos.css'
import { useRouter } from 'vue-router'

// const authStore = useAuthStore()
const resultsPerPage = ref(6)
const searchQuery = ref('')
const displayedSearchQuery = ref('')
const currentVideos = ref([])
const isLoadingAllData = ref(false)
const error = ref(null)
const totalResults = ref(0)
const currentPage = ref(1)
const initialSearchPerformed = ref(false)

const nextPageToken = ref(null)
const prevPageToken = ref(null)
const VITE_API_BASE_URL = import.meta.env.VITE_API_URL

const API_BASE_URL = `${VITE_API_BASE_URL}/api/v1/recommendations/youtube/economic-news/`
const FIXED_KEYWORDS = '금융 경제 뉴스'

const totalPages = computed(() => {
  if (totalResults.value === 0) return 0;
  return Math.ceil(totalResults.value / resultsPerPage.value);
});

const displayedPageNumbers = computed(() => {
  if (totalPages.value === 0) return [];
  const pages = [];
  const maxPagesToShow = 7;

  if (totalPages.value <= maxPagesToShow) {
    for (let i = 1; i <= totalPages.value; i++) {
      pages.push({ number: i, text: i.toString(), clickable: true });
    }
  } else {
    pages.push({ number: 1, text: '1', clickable: true });
    
    let rangeStart = Math.max(2, currentPage.value - Math.floor((maxPagesToShow - 3) / 2));
    let rangeEnd = Math.min(totalPages.value - 1, currentPage.value + Math.floor((maxPagesToShow - 2) / 2));

    if (currentPage.value < Math.ceil(maxPagesToShow/2) ) {
        rangeEnd = maxPagesToShow - 2;
    }
    if (currentPage.value > totalPages.value - Math.ceil(maxPagesToShow/2)) {
        rangeStart = totalPages.value - (maxPagesToShow - 3) ;
    }
    
    if (rangeStart > 2) {
      pages.push({ text: '...', clickable: false });
    }

    for (let i = rangeStart; i <= rangeEnd; i++) {
      if (i > 1 && i < totalPages.value) {
         pages.push({ number: i, text: i.toString(), clickable: true });
      }
    }

    if (rangeEnd < totalPages.value - 1) {
      pages.push({ text: '...', clickable: false });
    }
    
    pages.push({ number: totalPages.value, text: totalPages.value.toString(), clickable: true });
  }

  const uniquePages = [];
  let lastPushedClickable = true;
  for(let i=0; i < pages.length; i++) {
    if (pages[i].text === '...') {
      if (lastPushedClickable) {
        uniquePages.push(pages[i]);
        lastPushedClickable = false;
      }
    } else {
      if (uniquePages.length > 0 && 
          uniquePages[uniquePages.length -1].text === '...' &&
          i > 0 && pages[i-1] && pages[i-1].text === '...' &&
          uniquePages[uniquePages.length -2] &&
          typeof uniquePages[uniquePages.length -2].number === 'number' &&
          uniquePages[uniquePages.length -2].number + 1 === pages[i].number
          ) {
            uniquePages.pop();
      }
      uniquePages.push(pages[i]);
      lastPushedClickable = true;
    }
  }
  return uniquePages;
});

const fetchVideosForPage = async (page, pToken = null) => {
  if (!displayedSearchQuery.value.trim()) {
    initialSearchPerformed.value = false;
    currentVideos.value = [];
    totalResults.value = 0;
    nextPageToken.value = null;
    prevPageToken.value = null;
    return;
  }

  isLoadingAllData.value = true;
  error.value = null;

  const effectiveQuery = `${displayedSearchQuery.value.trim()} ${FIXED_KEYWORDS}`.trim();
  const params = {
    query: effectiveQuery,
    max_results: resultsPerPage.value,
  };

  if (pToken) {
    params.pageToken = pToken;
  }

  try {
    console.log(`[EconomicNewsView] fetchVideosForPage - Requesting page ${page} with params:`, JSON.parse(JSON.stringify(params)));
    const response = await axios.get(API_BASE_URL, { params });
    console.log('[EconomicNewsView] fetchVideosForPage - API Response Data (raw):', JSON.parse(JSON.stringify(response.data)));

    if (response.data && response.data.videos) {
      currentVideos.value = response.data.videos;
      
      if (page === 1 || totalResults.value === 0) {
          totalResults.value = response.data.totalResults || 0;
      }
      
      nextPageToken.value = response.data.nextPageToken || null;
      prevPageToken.value = response.data.prevPageToken || null;

      currentPage.value = page;
      initialSearchPerformed.value = true;

      if (currentVideos.value.length === 0 && initialSearchPerformed.value) {
        console.log(`[EconomicNewsView] fetchVideosForPage - No videos found for query '${displayedSearchQuery.value}' on page ${page}.`);
      }
    } else {
      const errMsg = response.data.error || '영상을 불러오는데 실패했거나 데이터 형식이 올바르지 않습니다.';
      console.error('[EconomicNewsView] fetchVideosForPage - Error in response structure or explicit error:', errMsg);
      throw new Error(errMsg);
    }
  } catch (err) {
    console.error(`[EconomicNewsView] fetchVideosForPage - Error during fetching videos for page ${page}:`, err);
    error.value = err.response?.data?.error || err.message || `페이지 ${page}의 영상을 불러오는 중 오류가 발생했습니다.`;
    currentVideos.value = [];
    totalResults.value = 0;
    nextPageToken.value = null;
    prevPageToken.value = null;
  } finally {
    isLoadingAllData.value = false;
    console.log(`[EconomicNewsView] fetchVideosForPage - Finished. isLoadingAllData: ${isLoadingAllData.value}. CurrentPage: ${currentPage.value}`);
  }
};

const resetSearchStateAndFetchFirstPage = () => {
  currentVideos.value = [];
  currentPage.value = 1;
  totalResults.value = 0;
  error.value = null;
  initialSearchPerformed.value = true;
  displayedSearchQuery.value = searchQuery.value;
  nextPageToken.value = null;
  prevPageToken.value = null;

  fetchVideosForPage(1);
};

const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    error.value = '검색어를 입력해주세요.';
    initialSearchPerformed.value = false; 
    currentVideos.value = [];
    totalResults.value = 0;
    displayedSearchQuery.value = '';
    return;
  }
  resetSearchStateAndFetchFirstPage();
};

const goToPage = (pageNumber) => {
  if (isLoadingAllData.value || pageNumber < 1 || pageNumber > totalPages.value || pageNumber === currentPage.value) {
    return;
  }

  let targetToken = null;
  if (pageNumber > currentPage.value) {
    if (pageNumber === currentPage.value + 1 && nextPageToken.value) {
      targetToken = nextPageToken.value;
    } else if (pageNumber === currentPage.value - 1 && prevPageToken.value) {
      targetToken = prevPageToken.value;
    } else {
      console.warn(`[EconomicNewsView] goToPage - Direct page jump to ${pageNumber} without specific token. This might re-fetch from start or use stored tokens if available for prev/next.`);
    }
    fetchVideosForPage(pageNumber, targetToken);
  } else {
    if (pageNumber === currentPage.value -1 && prevPageToken.value) {
       targetToken = prevPageToken.value
    }
    fetchVideosForPage(pageNumber, targetToken);
  }
};

const router = useRouter()

const openVideoModal = (videoId) => {
  router.push({ name: 'videoDetail', params: { videoId: videoId } });
}

const formatPublishTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}

onMounted(() => {
  console.log('[EconomicNewsView] onMounted - Component mounted.');
})

onActivated(() => {
  console.log('[EconomicNewsView] onActivated - Component activated.');
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
  margin-bottom: 10px;
  color: #4a90e2;
}

.search-section {
  background-color: #f8f9fa;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 15px;
}

.search-box input {
  flex: 1;
  padding: 12px 18px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1rem;
  background-color: #fff;
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
  background-color: #adb5bd;
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
  border: 5px solid #f3f3f3;
  border-top: 5px solid #4a90e2;
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
  background-color: #ffebee;
  color: #c62828;
  padding: 15px 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #ef9a9a;
  display: flex;
  flex-direction: column;
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
  grid-template-columns: repeat(2, 1fr);
  gap: 25px;
}

.youtube-video-item {
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
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
  background-color: #e9ecef;
  cursor: pointer;
}

.video-thumbnail {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
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
  width: 50px;
  height: 50px;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s ease, transform 0.3s ease;
  opacity: 0;
}

.video-thumbnail-wrapper:hover .play-button {
  opacity: 0.9;
  transform: translate(-50%, -50%) scale(1.1);
}
.play-button:hover {
    background-color: rgba(0, 0, 0, 0.8);
}

.video-title {
  margin: 12px 15px 8px 15px;
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  cursor: pointer;
  transition: color 0.2s ease;
}

.youtube-video-item:hover .video-title {
  color: #4a90e2;
}

.video-channel, .video-publish-time {
  font-size: 0.85rem;
  color: #555;
  margin: 0 15px 5px 15px;
  line-height: 1.3;
}

.video-publish-time {
  margin-bottom: 12px;
}

.pagination-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 30px;
  padding-bottom: 20px;
  gap: 8px;
}

.prev-button, .next-button {
  padding: 8px 16px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
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

.page-number {
  padding: 8px 12px;
  color: #4a90e2;
  border: 1px solid #4a90e2;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.3s ease, color 0.3s ease;
  font-weight: 500;
  min-width: 36px;
  text-align: center;
}

.page-number:hover:not(.disabled):not(.current-page) {
  background-color: #e0eef9;
}

.page-number.current-page {
  background-color: #4a90e2;
  color: white;
  border-color: #4a90e2;
  font-weight: bold;
}

.page-number.disabled {
  color: #adb5bd;
  border-color: #ced4da;
  cursor: default;
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

.search-guide {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 15px;
  text-align: left;
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
  .pagination-controls {
    flex-wrap: wrap;
    gap: 6px;
  }
  .page-number {
    padding: 6px 10px;
    min-width: 30px;
  }
}
</style> 