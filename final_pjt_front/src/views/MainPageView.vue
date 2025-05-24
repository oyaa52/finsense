<template>
  <div class="main-page-container">
    <!-- 좌측 사이드바 -->
    <aside class="sidebar" data-aos="fade-right">
      <div class="logo-container">
        <router-link to="/main">
          <img src="@/assets/FS_logo.png" alt="Fin Sense Logo" class="sidebar-logo"/>
        </router-link>
        <!-- 로고 이미지가 어두운 배경에 잘 보이도록 흰색 버전이나 대비가 높은 로고로 교체하는 것이 좋습니다. -->
        <!-- 없다면 일단 기존 로고를 사용합니다. -->
      </div>
      
      <div v-if="!isLoggedIn" class="auth-links">
        <router-link to="/login" class="auth-button login-button">로그인</router-link>
        <router-link to="/signup" class="auth-button signup-button">회원가입</router-link>
      </div>
      <div v-else class="user-info">
        <!-- currentUser가 null이 아닐 때만 프로필 이미지와 사용자 이름 표시 -->
        <template v-if="currentUser">
          <img :src="currentUser.profile_image || '@/assets/default_profile.png'" alt="User Profile" class="profile-image"/>
          <p>{{ currentUser.username || '사용자' }}님, 환영합니다!</p>
        </template>
        <button @click="logout" class="auth-button logout-button">로그아웃</button>
      </div>
      
      <nav class="sidebar-nav">
        <ul>
          <li><router-link to="/main/profile-management">회원정보관리</router-link></li>
          <li><router-link to="/main/settings">설정</router-link></li>
        </ul>
      </nav>
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
          <!-- 상단 이미지 섹션 -->
          <section class="main-image-section">
            <img src="@/assets/Main_Image.png" alt="Main Promotional Image" class="promo-image"/>
          </section>

          <!-- 하단 금융 뉴스 섹션 -->
          <section class="news-section">
            <h2>오늘 주목할 금융 뉴스</h2>
            <div v-if="videosLoading" class="loading-message">영상을 불러오는 중입니다...</div>
            <div v-else-if="videosError" class="error-message">{{ videosError }}</div>
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
              현재 표시할 영상이 없습니다.
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

const authStore = useAuthStore() // authStore 인스턴스 생성
const router = useRouter()
const route = useRoute() // 현재 라우트 정보를 가져오기 위해 추가

// authStore의 상태를 computed 속성으로 사용
const isLoggedIn = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => authStore.currentUser) // dj-rest-auth/user/의 응답을 기반으로 함

// YouTube 영상 관련 상태
const youtubeVideos = ref([])
const videosLoading = ref(false)
const videosError = ref(null)

// YouTube 영상 가져오는 함수
const fetchYoutubeVideos = async () => {
  if (!isMainPageDefaultView.value) return; // 기본 화면일 때만 실행

  videosLoading.value = true
  videosError.value = null
  youtubeVideos.value = []
  try {
    // 백엔드 API 엔드포인트 (검색어와 결과 개수 지정)
    const response = await axios.get('http://127.0.0.1:8000/api/v1/recommendations/youtube-search/', {
      params: {
        query: '금융 주식', // 기본 검색어
        max_results: 2     // MainPageView에서는 2개만 요청
      }
    })
    if (response.data && Array.isArray(response.data)) {
      youtubeVideos.value = response.data
    } else {
      // 백엔드에서 에러 객체를 반환하는 경우 (예: {error: "메시지"} 또는 {message: "메시지"})
      if (response.data && (response.data.error || response.data.message)) {
        videosError.value = response.data.error || response.data.message;
      } else {
        videosError.value = '영상을 불러오는 데 실패했습니다.'
      }
    }
  } catch (error) {
    console.error('YouTube 영상 로딩 중 에러:', error)
    if (error.response && error.response.data && (error.response.data.error || error.response.data.message)) {
      videosError.value = error.response.data.error || error.response.data.message;
    } else {
      videosError.value = '서버와 통신 중 오류가 발생했습니다.'
    }
  } finally {
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
  if (isMainPageDefaultView.value) { // 기본 화면일 때만 영상 로드
    fetchYoutubeVideos()
  }
})

// 현재 라우트가 MainPageView의 기본 경로인지 확인하는 computed 속성
// $route.name을 직접 사용하는 대신, $route.matched를 사용하여 nested routes에서도 정확히 작동하도록 수정
const isMainPageDefaultView = computed(() => {
  // 현재 활성화된 라우트 중 mainServiceView라는 이름을 가진 자식 라우트가 있는지 확인
  const isDefault = !route.matched.some(record => record.components && record.components.mainServiceView)
  // isMainPageDefaultView 값이 변경될 때, true가 되면 영상 다시 로드 시도 (라우트 변경으로 메인 돌아왔을때)
  if (isDefault && youtubeVideos.value.length === 0 && !videosLoading.value) {
     // fetchYoutubeVideos(); // 이 부분은 watch나 다른 방식으로 처리하는 것이 더 적합할 수 있음
  }
  return isDefault;
})

// 라우트 변경 시 isMainPageDefaultView가 true로 바뀌면 영상 로드 (watch 사용)
watch(() => route.path, (newPath, oldPath) => {
  // /main으로 돌아왔고, 자식 라우트가 없는 경우 (즉 isMainPageDefaultView가 true가 되는 시점)
  if (newPath === '/main' && isMainPageDefaultView.value) {
    // 영상이 없거나, 이전에 에러가 나서 로드되지 않았을 경우 다시 시도
    if (youtubeVideos.value.length === 0 || videosError.value) {
      fetchYoutubeVideos()
    }
  }
}, { immediate: false }) // immediate: false로 초기 마운트 시 중복 호출 방지

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
  height: 100vh; /* 전체 화면 높이 */
  background-color: #121212; /* 매우 어두운 배경 (검정 계열) */
  color: #ffffff; /* 기본 텍스트 색상 흰색 */
  overflow: hidden; /* 스크롤은 각 영역에서 관리 */
}

/* Sidebar Styles */
.sidebar {
  width: 280px;
  background-color: #000000; /* 사이드바 배경 (검정) */
  padding: 30px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.5);
  overflow-y: auto;
}

.logo-container {
  margin-bottom: 40px;
}

.sidebar-logo {
  max-width: 150px;
  height: auto;
}

.auth-links, .user-info {
  width: 100%;
  text-align: center;
  margin-bottom: 30px;
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
  text-decoration: none; /* router-link 스타일 초기화 */
  color: #ffffff; /* 버튼 텍스트 색상 */
}

.login-button {
  background-color: #0064FF; /* 파란색 */
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
  background-color: rgba(0, 100, 255, 0.1);
  color: #007bff;
  transform: translateY(-1px);
}

.user-info .profile-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  margin-bottom: 15px;
  border: 3px solid #0064FF;
}

.user-info p {
  font-size: 1.1rem;
  margin-bottom: 20px;
}

.logout-button {
  background-color: #333;
}
.logout-button:hover {
  background-color: #444;
}

.sidebar-nav {
  width: 100%;
}

.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-nav li a {
  display: block;
  padding: 12px 15px;
  color: #adb5bd; /* 약간 밝은 회색 */
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.95rem;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.sidebar-nav li a:hover,
.sidebar-nav li a.router-link-exact-active {
  background-color: #0064FF; /* 파란색 */
  color: #ffffff;
}

/* Main Content Styles */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto; /* 메인 컨텐츠 영역만 스크롤 */
}

/* Top Navbar Styles */
.top-navbar {
  background-color: #1a1a1a; /* 상단바 배경 (검정보다 약간 밝게) */
  padding: 0 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  z-index: 10;
  height: 70px;
  display: flex;
  align-items: center;
}

.top-navbar nav { /* ul 대신 nav에 적용 */
  display: flex;
  flex-grow: 1; /* 네비게이션 바 내에서 가능한 많은 공간 차지 */
  justify-content: center; /* 내부 아이템들(ul)을 가운데 정렬 */
}

.top-navbar nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  gap: 25px; /* 메뉴 아이템 간 간격 */
}

.top-navbar nav ul li a {
  color: #e0e0e0; /* 기본 링크 색상 */
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  padding: 10px 15px;
  border-radius: 6px;
  transition: color 0.3s ease, background-color 0.3s ease;
  position: relative;
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
  color: #ffffff;
  background-color: rgba(0, 100, 255, 0.1); /* 호버/활성 시 약간의 배경 */
}

.top-navbar nav ul li a:hover::after,
.top-navbar nav ul li a.router-link-exact-active::after {
  width: calc(100% - 20px); /* 양쪽에 10px씩 여백을 둔 너비 */
}


/* Content Area Styles */
.content-area {
  flex-grow: 1;
  padding: 40px;
  background-color: #1f1f1f; /* 컨텐츠 영역 배경 (상단바보다 약간 밝게) */
  overflow-y: auto;
}

.default-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  color: #cccccc;
}

.default-content h2 {
  font-size: 2.5rem;
  color: #007bff; /* 파란색 강조 */
  margin-bottom: 20px;
}

.default-content p {
  font-size: 1.2rem;
  max-width: 600px;
}

/* 메인 이미지 섹션 스타일 */
.main-image-section {
  width: 100%;
  margin-bottom: 40px; /* 뉴스 섹션과의 간격 */
  text-align: center; /* 이미지 가운데 정렬 */
}

.promo-image {
  max-width: 100%;
  max-height: 400px; /* 이미지 최대 높이 제한 */
  border-radius: 12px;
  object-fit: cover; /* 이미지 비율 유지하며 채우기 */
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

/* 뉴스 섹션 스타일 */
.news-section {
  width: 100%;
  text-align: center;
}

.news-section h2 {
  font-size: 1.8rem; /* 기존 h2보다 약간 작게 */
  color: #0099ff; /* 다른 파란색 계열 */
  margin-bottom: 25px;
}

.youtube-placeholder {
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a0a0a0;
}

/* YouTube 영상 관련 스타일 */
.loading-message,
.error-message,
.no-videos-message {
  padding: 20px;
  background-color: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  min-height: 100px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a0a0a0;
  margin-top: 20px;
}

.error-message {
  color: #ff6b6b; /* 에러 메시지 색상 */
  border: 1px solid #ff6b6b;
}

.youtube-videos-container {
  display: flex;
  justify-content: space-around; /* 영상들을 가로로 균등 간격 배치 */
  gap: 20px; /* 영상 간의 간격 */
  margin-top: 20px;
  flex-wrap: wrap; /* 공간 부족 시 다음 줄로 */
}

.youtube-video-item {
  flex-basis: calc(50% - 10px); /* 기본적으로 2개씩, 간격 고려 */
  max-width: calc(50% - 10px);
  background-color: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
}

.youtube-video-item iframe {
  width: 100%;
  aspect-ratio: 16 / 9; /* 16:9 비율 유지 */
  border-radius: 6px;
  margin-bottom: 10px;
}

.video-title {
  font-size: 0.9rem;
  color: #e0e0e0;
  margin-top: auto; /* 제목을 카드 하단에 위치시키도록 */
  text-align: left;
  line-height: 1.4;
  max-height: 3.9em; /* 대략 3줄까지 보이도록 (1.3em * 3) */
  overflow: hidden;
  text-overflow: ellipsis;
  /* white-space: nowrap; */ /* 한 줄로 하고 싶을 때 */
  display: -webkit-box;
  -webkit-line-clamp: 3; /* Safari, Chrome 등 WebKit 기반 브라우저 */
  -webkit-box-orient: vertical;
}

/* AOS Animations */
[data-aos] {
  transition-property: transform, opacity;
}
</style> 