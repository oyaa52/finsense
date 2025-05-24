<template>
  <div class="default-content">
    <!-- 상단 이미지 슬라이더 섹션 -->
    <section class="main-image-slider-section">
      <swiper
        :modules="swiperModules"
        :slides-per-view="1"
        :space-between="0"
        effect="fade"
        :fade-effect="{ crossFade: true }"
        :loop="true"
        :autoplay="{ delay: 3000, disableOnInteraction: false }"
        :speed="1500"
        :navigation="{
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev'
        }"
        :pagination="{ el: '.swiper-pagination', clickable: true }"
        class="main-promo-slider"
      >
        <swiper-slide v-for="(slide, index) in promoSlides" :key="index">
          <img :src="slide.src" :alt="slide.alt" class="promo-slide-image"/>
        </swiper-slide>
        <!-- 네비게이션 버튼 -->
        <div class="swiper-button-prev"></div>
        <div class="swiper-button-next"></div>
        <!-- 페이지네이션 -->
        <div class="swiper-pagination"></div>
      </swiper>
    </section>

    <!-- 하단 금융 뉴스 섹션 -->
    <section class="news-section">
      <h2>오늘 주목할 금융 뉴스</h2>
      <div v-if="videosLoading" class="loading-message">
        <div class="loading-spinner"></div>
        <p>영상을 불러오는 중입니다...</p>
      </div>
      <div v-else-if="videosError" class="error-message">
        <p>{{ videosError }}</p>
        <button @click="fetchYoutubeVideos" class="retry-button">다시 시도</button>
      </div>
      <div v-else-if="youtubeVideos.length > 0" class="youtube-videos-container">
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
      <div v-else class="no-videos-message">
        <p>현재 표시할 영상이 없습니다.</p>
        <button @click="fetchYoutubeVideos" class="retry-button">새로고침</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, Navigation, Pagination, EffectFade } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/effect-fade'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

const swiperModules = [Autoplay, Navigation, Pagination, EffectFade]

const promoSlides = ref([
  { src: new URL('@/assets/Main_Image.png', import.meta.url).href, alt: '프로모션 이미지 1' },
  { src: new URL('@/assets/Main_Image1.png', import.meta.url).href, alt: '프로모션 이미지 2' },
  { src: new URL('@/assets/Main_Image2.png', import.meta.url).href, alt: '프로모션 이미지 3' },
  { src: new URL('@/assets/Main_Image3.png', import.meta.url).href, alt: '프로모션 이미지 4' },
])

const youtubeVideos = ref([])
const videosLoading = ref(false)
const videosError = ref(null)

const fetchYoutubeVideos = async () => {
  videosLoading.value = true
  videosError.value = null
  
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/v1/recommendations/youtube-search/', {
      params: {
        query: '금융 뉴스',
        max_results: 2
      }
    })
    youtubeVideos.value = response.data
  } catch (error) {
    console.error('YouTube 영상 로딩 중 에러:', error)
    if (error.response) {
      switch (error.response.status) {
        case 503:
          videosError.value = 'YouTube 서비스가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.'
          break
        case 429:
          videosError.value = 'YouTube API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.'
          break
        default:
          videosError.value = '영상을 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
      }
    } else if (error.request) {
      videosError.value = '서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.'
    } else {
      videosError.value = '영상을 불러오는 중 오류가 발생했습니다.'
    }
  } finally {
    videosLoading.value = false
  }
}

onMounted(() => {
  fetchYoutubeVideos()
})
</script>

<style scoped>
.default-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  min-height: 100%;
  height: auto;
  text-align: center;
  color: #191919;
}

.main-image-slider-section {
  width: 80%;
  max-width: 80%;
  margin: 0 auto 40px auto;
}

.main-promo-slider {
  width: 100%;
  height: 65vh;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.promo-slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.swiper-button-prev,
.swiper-button-next {
  color: rgba(255, 255, 255, 0.7);
  background-color: rgba(0, 0, 0, 0.3);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.swiper-button-prev:hover,
.swiper-button-next:hover {
  background-color: rgba(0, 0, 0, 0.5);
  color: #ffffff;
}

.swiper-button-prev::after,
.swiper-button-next::after {
  font-size: 18px;
  font-weight: bold;
}

.swiper-pagination {
  bottom: 20px !important;
}

.swiper-pagination .swiper-pagination-bullet {
  background-color: rgba(255, 255, 255, 0.5);
  opacity: 1;
  width: 8px;
  height: 8px;
  margin: 0 5px !important;
  transition: background-color 0.3s ease, width 0.3s ease;
}

.swiper-pagination .swiper-pagination-bullet-active {
  background-color: #ffffff;
  width: 24px;
  border-radius: 4px;
}

.news-section {
  width: 100%;
  text-align: center;
}

.news-section h2 {
  font-size: 1.8rem;
  color: #3F72AF;
  margin-bottom: 25px;
}

.loading-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 8px;
  min-height: 200px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0064FF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message, .no-videos-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px;
  background-color: #fff;
  border-radius: 8px;
  min-height: 200px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.error-message p, .no-videos-message p {
  color: #666;
  margin-bottom: 15px;
  text-align: center;
}

.retry-button {
  padding: 10px 20px;
  background-color: #0064FF;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.retry-button:hover {
  background-color: #0052cc;
}

.youtube-videos-container {
  display: flex;
  justify-content: space-around;
  gap: 20px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.youtube-video-item {
  flex-basis: calc(50% - 10px);
  max-width: calc(50% - 10px);
  background-color: #ffffff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.youtube-video-item iframe {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 6px;
  margin-bottom: 10px;
}

.video-title {
  font-size: 0.9rem;
  color: #191919;
  margin-top: auto;
  text-align: left;
  line-height: 1.4;
  max-height: 3.9em;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}
</style> 