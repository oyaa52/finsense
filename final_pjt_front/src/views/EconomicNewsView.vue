<template>
  <div class="economic-news-container" data-aos="fade-up">
    <div class="search-section">
      <h2 class="section-title">경제 뉴스 검색</h2>
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="관심 있는 경제 키워드를 입력하세요 (예: 금리, 주식, 부동산, 환율 등)"
          @keyup.enter="handleSearch"
        />
        <button @click="handleSearch" :disabled="isLoading">
          {{ isLoading ? '검색 중...' : '검색' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>

    <div v-if="youtubeVideos.length > 0" class="youtube-results">
      <h3 class="results-title">관련 경제 뉴스 영상</h3>
      <div class="youtube-grid">
        <div v-for="video in youtubeVideos" :key="video.video_id" class="youtube-video-item">
          <iframe 
            :src="`https://www.youtube.com/embed/${video.video_id}`" 
            frameborder="0" 
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
            allowfullscreen>
          </iframe>
          <h4 class="video-title" :title="video.title">{{ video.title }}</h4>
        </div>
      </div>
    </div>

    <div v-else-if="!isLoading && searchQuery" class="no-results">
      <p>검색 결과가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const searchQuery = ref('')
const youtubeVideos = ref([])
const isLoading = ref(false)
const error = ref(null)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    error.value = '검색어를 입력해주세요.'
    return
  }

  isLoading.value = true
  error.value = null
  youtubeVideos.value = []

  try {
    const response = await axios.get(
      `http://127.0.0.1:8000/api/v1/recommendations/youtube-search/?query=${encodeURIComponent(searchQuery.value)}`,
      {
        headers: {
          'Authorization': `Token ${authStore.accessToken}`
        }
      }
    )
    youtubeVideos.value = response.data
  } catch (err) {
    error.value = err.response?.data?.error || '검색 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.economic-news-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #333333;
  margin-bottom: 25px;
}

.search-section {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-box input {
  flex: 1;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  color: #333333;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
}

.search-box input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
  background-color: #ffffff;
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
  transition: all 0.3s ease;
}

.search-box button:hover:not(:disabled) {
  background-color: #357abd;
  transform: translateY(-2px);
}

.search-box button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #e74c3c;
}

.youtube-results {
  margin-top: 30px;
}

.results-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333333;
  margin-bottom: 20px;
}

.youtube-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.youtube-video-item {
  background-color: #ffffff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: transform 0.3s ease;
}

.youtube-video-item:hover {
  transform: translateY(-5px);
}

.youtube-video-item iframe {
  width: 100%;
  aspect-ratio: 16/9;
  border: none;
}

.video-title {
  padding: 15px;
  margin: 0;
  font-size: 1rem;
  font-weight: 500;
  color: #333333;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.no-results {
  text-align: center;
  padding: 40px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.no-results p {
  color: #666666;
  font-size: 1.1rem;
  margin: 0;
}

@media (max-width: 768px) {
  .search-box {
    flex-direction: column;
  }

  .search-box button {
    width: 100%;
  }

  .youtube-grid {
    grid-template-columns: 1fr;
  }
}
</style> 