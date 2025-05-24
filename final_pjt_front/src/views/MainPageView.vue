<template>
  <div class="main-page-container">
    <!-- 좌측 사이드바 -->
    <aside class="sidebar" data-aos="fade-right">
      <div class="logo-container">
        <router-link to="/main">
          <img src="@/assets/FS_logo.png" alt="Fin Sense Logo" class="sidebar-logo"/>
        </router-link>
      </div>
      
      <div v-if="!isLoggedIn" class="auth-links">
        <router-link to="/login" class="auth-button login-button">로그인</router-link>
        <router-link to="/signup" class="auth-button signup-button">회원가입</router-link>
      </div>
      <div v-else class="user-info-box">
        <template v-if="currentUser">
          <img :src="currentUser.profile_image || '@/assets/default_profile.png'" alt="User Profile" class="profile-image"/>
          <p class="welcome-message">{{ currentUser.username || '사용자' }}님, 환영합니다!</p>
        </template>
        <div class="user-actions">
          <router-link to="/main/profile-management" class="action-link profile-link">내 프로필</router-link>
          <span class="separator">|</span>
          <button @click="logout" class="action-link logout-link">로그아웃</button>
        </div>
      </div>
      
      <!-- <nav class="sidebar-nav">
        <ul>
          <li><router-link to="/main/profile-management">회원정보관리</router-link></li>
          <li><router-link to="/main/settings">설정</router-link></li>
        </ul>
      </nav> -->
    </aside>

    <!-- 메인 컨텐츠 영역 -->
    <main class="main-content">
      <!-- 상단 네비게이션 바 -->
      <header class="top-navbar" data-aos="fade-down">
        <nav>
          <ul>
            <li><router-link to="/main/deposit-comparison">예적금 금리 비교</router-link></li>
            <li><router-link to="/main/commodity-comparison">현물 상품 비교</router-link></li>
            <li><router-link to="/main/product-recommendation">금융상품 추천</router-link></li>
            <li><router-link to="/main/stock-search">관심 종목 정보 검색</router-link></li>
            <li><router-link to="/main/nearby-banks">근처 은행 검색</router-link></li>
            <li><router-link to="/main/community">커뮤니티</router-link></li>
          </ul>
        </nav>
      </header>

      <!-- 컨텐츠 표시 영역 -->
      <div class="content-area" data-aos="fade-up" data-aos-delay="200">
        <router-view name="mainServiceView"></router-view>
        <!-- 기본 컨텐츠 영역 수정 -->
        <div v-if="isMainPageDefaultView" class="default-content">
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
                <!-- <div class="slide-caption">{{ slide.caption }}</div> -->
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
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router' // useRoute import
import AOS from 'aos'
import 'aos/dist/aos.css'
import { useAuthStore } from '@/stores/authStore' // authStore 임포트
import axios from 'axios' // axios 임포트

// Swiper Vue.js 로부터 컴포넌트 가져오기
import { Swiper, SwiperSlide } from 'swiper/vue'
// Swiper 모듈 가져오기
import { Autoplay, Navigation, Pagination, EffectFade } from 'swiper/modules'

// Swiper 스타일 가져오기
import 'swiper/css'
import 'swiper/css/effect-fade'
import 'swiper/css/navigation'
import 'swiper/css/pagination'

// 사용할 Swiper 모듈 배열
const swiperModules = [Autoplay, Navigation, Pagination, EffectFade]

// 슬라이드 이미지 데이터 (src 경로는 실제 파일 위치에 맞게 조정 필요)
const promoSlides = ref([
  { src: new URL('@/assets/Main_Image.png', import.meta.url).href, alt: '프로모션 이미지 1', caption: '첫번째 슬라이드' },
  { src: new URL('@/assets/Main_Image1.png', import.meta.url).href, alt: '프로모션 이미지 2', caption: '두번째 슬라이드' },
  { src: new URL('@/assets/Main_Image2.png', import.meta.url).href, alt: '프로모션 이미지 3', caption: '세번째 슬라이드' },
  { src: new URL('@/assets/Main_Image3.png', import.meta.url).href, alt: '프로모션 이미지 4', caption: '네번째 슬라이드' },
])

const authStore = useAuthStore() // authStore 인스턴스 생성
const router = useRouter()
const route = useRoute() // 현재 라우트 정보를 가져오기 위해 추가

// authStore의 상태를 computed 속성으로 사용
const isLoggedIn = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => {
  const user = authStore.currentUser
  console.log('[MainPageView] currentUser:', user)
  return user
}) // dj-rest-auth/user/의 응답을 기반으로 함
// YouTube 영상 관련 상태
const youtubeVideos = ref([])
const videosLoading = ref(false)
const videosError = ref(null)

// YouTube 영상 가져오는 함수
const fetchYoutubeVideos = async () => {
  console.log('[MainPageView] fetchYoutubeVideos: 시작, videosLoading:', videosLoading.value)
  videosLoading.value = true
  videosError.value = null
  
  try {
    console.log('[MainPageView] fetchYoutubeVideos: API 요청 전')
    const response = await axios.get('http://127.0.0.1:8000/api/v1/recommendations/youtube-search/', {
      params: {
        query: '금융 뉴스',
        max_results: 2
      }
    })
    console.log('[MainPageView] fetchYoutubeVideos: API 응답 받음')
    youtubeVideos.value = response.data
  } catch (error) {
    console.error('[MainPageView] YouTube 영상 로딩 중 에러:', error)
    if (error.response) {
      // 서버에서 응답이 왔지만 에러인 경우
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
      // 요청은 보냈지만 응답이 없는 경우
      videosError.value = '서버에 연결할 수 없습니다. 인터넷 연결을 확인해주세요.'
    } else {
      // 요청 설정 중 에러가 발생한 경우
      videosError.value = '영상을 불러오는 중 오류가 발생했습니다.'
    }
    youtubeVideos.value = []
  } finally {
    console.log('[MainPageView] fetchYoutubeVideos: 종료 (finally), videosLoading:', videosLoading.value)
    videosLoading.value = false
  }
}

// 로그아웃 함수
const logout = async () => {
  await authStore.logoutAction() // 스토어의 로그아웃 액션 호출
  router.push('/') // 로그아웃 후 랜딩 페이지 등으로 이동
}

onMounted(() => {
  AOS.init()
  console.log('[MainPageView] onMounted: 시작, isMainPageDefaultView:', isMainPageDefaultView.value)
  console.log('[MainPageView] onMounted: currentUser:', currentUser.value)
  if (isMainPageDefaultView.value) { // 기본 화면일 때만 영상 로드
    fetchYoutubeVideos()
  }
  console.log('[MainPageView] onMounted: 종료')
})

// 현재 라우트가 MainPageView의 기본 경로인지 확인하는 computed 속성
// $route.name을 직접 사용하는 대신, $route.matched를 사용하여 nested routes에서도 정확히 작동하도록 수정
const isMainPageDefaultView = computed(() => {
  // 현재 활성화된 라우트 중 mainServiceView라는 이름을 가진 자식 라우트가 있는지 확인
  const isDefault = !route.matched.some(record => record.components && record.components.mainServiceView)
  // isMainPageDefaultView 값이 변경될 때, true가 되면 영상 다시 로드 시도 (라우트 변경으로 메인 돌아왔을때)
  if (isDefault && youtubeVideos.value.length === 0 && !videosLoading.value) {
     // fetchYoutubeVideos(); // 이 부분은 watch나 다른 방식으로 처리하는 것이 더 적합할 수 있음
     console.log('[MainPageView] isMainPageDefaultView computed: 기본 뷰이고 영상 없음, 로드 필요 시 fetch 호출 (현재 주석 처리됨)')
  }
  return isDefault;
})

// 라우트 변경 시 isMainPageDefaultView가 true로 바뀌면 영상 로드 (watch 사용)
watch(() => route.path, (newPath, oldPath) => {
  console.log(`[MainPageView] watch route.path: 변경 감지 - newPath: ${newPath}, oldPath: ${oldPath}, isMainPageDefaultView: ${isMainPageDefaultView.value}`)
  // /main으로 돌아왔고, 자식 라우트가 없는 경우 (즉 isMainPageDefaultView가 true가 되는 시점)
  if (newPath === '/main' && isMainPageDefaultView.value) {
    console.log('[MainPageView] watch route.path: 메인 페이지로 돌아옴 & 기본 뷰 상태')
    // 영상이 없거나, 이전에 에러가 나서 로드되지 않았을 경우 다시 시도
    if (youtubeVideos.value.length === 0 || videosError.value) {
      console.log('[MainPageView] watch route.path: 영상이 없거나 에러 상태, fetchYoutubeVideos 호출')
      fetchYoutubeVideos()
    } else {
      console.log('[MainPageView] watch route.path: 이미 영상 데이터가 있거나 에러 없음, fetch 호출 안 함')
    }
  }
}, { immediate: false }) // immediate: false로 초기 마운트 시 중복 호출 방지

// authStore의 상태 변화 감시
watch(() => authStore.currentUser, (newUser, oldUser) => {
  console.log('[MainPageView] authStore.currentUser changed:', {
    old: oldUser,
    new: newUser
  })
}, { immediate: true })

</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

body, html {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: 'Noto Sans KR', sans-serif;
}

.main-page-container {
  display: flex;
  height: 100vh;
  background-color: #ffffff; /* 밝은 테마: 흰색 배경 */
  color: #191919; /* 밝은 테마: 기본 텍스트 색상 */
  overflow: hidden;
}

/* Sidebar Styles */
.sidebar {
  width: 320px; /* 고정 너비로 변경 */
  min-width: 320px; /* 최소 너비 설정 */
  max-width: 320px; /* 최대 너비 설정 */
  background-color: #f5f5f5;
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  position: fixed; /* 사이드바 고정 */
  height: 100vh; /* 전체 높이 */
  left: 0; /* 왼쪽에 고정 */
  top: 0; /* 상단에 고정 */
}

.logo-container {
  margin-bottom: 20px; /* user-info-box와의 간격을 살짝 줄임 */
}

.sidebar-logo {
  max-width: 150px;
  height: auto;
  align-items: center;
}

.auth-links, .user-info-box { /* user-info 에서 user-info-box로 클래스명 변경 */
  width: 100%;
  text-align: center;
  margin-bottom: 30px;
  padding: 20px; /* 박스 형태를 위한 패딩 추가 */
  background-color: #ffffff; /* 박스 배경색 */
  border-radius: 8px; /* 박스 모서리 둥글게 */
  box-shadow: 0 2px 4px rgba(0,0,0,0.05); /* 박스 그림자 */
}

.auth-button {
  display: block;
  width: 100%;
  padding: 12px 0;
  margin-bottom: 10px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  text-decoration: none;
}

.login-button {
  background-color: #0064FF;
  color: #ffffff;
}
.login-button:hover {
  background-color: #0052cc;
  transform: translateY(-1px);
}

.signup-button {
  background-color: transparent;
  border: 1px solid #0064FF;
  color: #0064FF;
}
.signup-button:hover {
  background-color: rgba(0, 100, 255, 0.05);
  transform: translateY(-1px);
}

.user-info-box .profile-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px; /* 환영 메시지와의 간격 늘림 */
  border: 2px solid #0064FF;
  flex-shrink: 0; /* 이미지 크기 고정 */
}

.user-info-box .welcome-message { /* user-info 에서 user-info-box로 클래스명 변경 및 새 클래스 */
  font-size: 1rem;
  margin: 15px 0;
  color: #191919;
  font-weight: 500;
  text-overflow: ellipsis; /* 내용이 넘칠 경우 말줄임표(...) 표시 */
  overflow: hidden;
  white-space: nowrap;
  max-width: 100%;
  padding: 0 10px;
}

.user-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 5px; /* 버튼과 구분자 사이 간격 */
  width: 100%; /* 너비를 100%로 설정하여 내부 요소들이 공간을 갖도록 함 */
}

.action-link {
  background: none;
  border: none;
  padding: 5px;
  font: inherit;
  cursor: pointer;
  outline: inherit;
  color: #0064FF; /* 링크 색상 */
  text-decoration: none;
  font-size: 0.9rem; /* 글자 크기 더 줄임 */
  font-weight: 500;
  transition: color 0.2s ease;
  white-space: nowrap; /* 내부 텍스트 줄바꿈 방지 */
}

.action-link:hover {
  color: #004cb3; /* 호버 시 색상 변경 */
  text-decoration: underline;
}

.separator {
  margin: 0 5px; /* 구분자 좌우 간격 5px로 수정 */
  color: #cccccc; /* 구분자 색상 연하게 */
  font-size: 0.9rem;
}

.logout-link {
  /* .action-link 스타일 상속 */
  color: #555555; /* 로그아웃 링크 기본 색상 */
  white-space: nowrap; /* 내부 텍스트 줄바꿈 방지 */
}

.logout-link:hover {
  color: #191919; /* 로그아웃 링크 호버 시 색상 */
  text-decoration: underline;
}

/* Main Content Styles */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  background-color: #ffffff;
  margin-left: 320px; /* 사이드바 너비만큼 여백 추가 */
  min-height: 100vh; /* 최소 높이 설정 */
}

/* Top Navbar Styles */
.top-navbar {
  background-color: #ffffff;
  padding: 0 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  z-index: 10;
  height: 70px; /* 고정 높이 */
  min-height: 70px; /* 최소 높이 설정 */
  max-height: 70px; /* 최대 높이 설정 */
  display: flex;
  align-items: center;
  position: sticky; /* 스크롤 시 상단에 고정 */
  top: 0; /* 상단에 고정 */
}

.top-navbar nav {
  display: flex;
  flex-grow: 1;
  justify-content: center;
  height: 100%; /* 네비게이션 높이 100% */
}

.top-navbar nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 25px;
  height: 100%; /* ul 높이 100% */
  align-items: center; /* 수직 중앙 정렬 */
}

.top-navbar nav ul li {
  height: 100%; /* li 높이 100% */
  display: flex;
  align-items: center; /* 수직 중앙 정렬 */
}

.top-navbar nav ul li a {
  color: #333333;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  padding: 10px 15px;
  border-radius: 6px;
  transition: color 0.3s ease, background-color 0.3s ease;
  position: relative;
  white-space: nowrap; /* 텍스트 줄바꿈 방지 */
  height: 100%; /* 링크 높이 100% */
  display: flex;
  align-items: center; /* 수직 중앙 정렬 */
}

.top-navbar nav ul li a::after {
  content: '';
  position: absolute;
  bottom: -5px;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background-color: #0064FF;
  transition: width 0.3s ease;
  border-radius: 2px;
}

.top-navbar nav ul li a:hover,
.top-navbar nav ul li a.router-link-exact-active {
  color: #0064FF;
  background-color: transparent;
}

.top-navbar nav ul li a:hover::after,
.top-navbar nav ul li a.router-link-exact-active::after {
  width: calc(100% - 20px);
}

/* Content Area Styles */
.content-area {
  flex-grow: 1;
  padding: 40px;
  background-color: #ffffff;
  overflow-y: auto;
  min-height: calc(100vh - 70px); /* 전체 높이에서 네비게이션 바 높이를 뺀 값 */
}

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

.default-content h2 {
  font-size: 2.5rem;
  color: #0064FF;
  margin-bottom: 20px;
}

.default-content p {
  font-size: 1.2rem;
  max-width: 600px;
  color: #333333;
}

/* 메인 이미지 슬라이더 섹션 스타일 */
.main-image-slider-section {
  width: 80%;
  max-width: 80%; /* 슬라이더 섹션 최대 가로폭 설정 */
  margin: 0 auto 40px auto; /* 위아래 마진 유지, 좌우 auto로 가운데 정렬, 아래쪽 마진 40px */
}

.main-promo-slider {
  width: 100%; /* 부모 요소인 .main-image-slider-section의 너비를 따름 */
  height: 65vh; /* 이전 값으로 복원 */
  border-radius: 12px;
  overflow: hidden; /* 중요: 슬라이드 내용이 넘치지 않도록 */
  position: relative; /* 네비게이션/페이지네이션 위치 기준 */
}

.promo-slide-image {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 이미지가 슬라이드 영역을 꽉 채우도록 */
  display: block;
}

/* Swiper 네비게이션 버튼 스타일 (토스뱅크 스타일 참고) */
.swiper-button-prev,
.swiper-button-next {
  color: rgba(255, 255, 255, 0.7); /* 반투명 흰색 */
  background-color: rgba(0, 0, 0, 0.3);
  width: 40px; /* 크기 조정 */
  height: 40px; /* 크기 조정 */
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
  font-size: 18px; /* 아이콘 크기 조정 */
  font-weight: bold;
}

/* Swiper 페이지네이션 스타일 (토스뱅크 스타일 참고) */
.swiper-pagination {
  bottom: 20px !important; /* 위치 조정 */
}

.swiper-pagination .swiper-pagination-bullet {
  background-color: rgba(255, 255, 255, 0.5); /* 비활성 점 색상 */
  opacity: 1;
  width: 8px;
  height: 8px;
  margin: 0 5px !important;
  transition: background-color 0.3s ease, width 0.3s ease;
}

.swiper-pagination .swiper-pagination-bullet-active {
  background-color: #ffffff; /* 활성 점 색상 */
  width: 24px; /* 토스뱅크처럼 활성 시 길어지는 효과 */
  border-radius: 4px;
}

/* 뉴스 섹션 스타일 */
.news-section {
  width: 100%;
  text-align: center;
}

.news-section h2 {
  font-size: 1.8rem;
  color: #3F72AF;
  margin-bottom: 25px;
}

/* YouTube 영상 관련 스타일 */
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

/* AOS Animations */
[data-aos] {
  transition-property: transform, opacity;
}
</style> 