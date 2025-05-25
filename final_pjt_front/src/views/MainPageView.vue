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
          <img :src="profileImageUrl" alt="User Profile" class="profile-image"/>
          <p class="welcome-message">{{ currentUser.username || '사용자' }}님, 환영합니다!</p>
        </template>
        <div class="user-actions">
          <router-link to="/main/profile-management" class="action-link profile-link">내 프로필</router-link>
          <span class="separator">|</span>
          <button @click="logout" class="action-link logout-link">로그아웃</button>
        </div>
        <!-- 즐겨찾기 메뉴 추가 -->
        <nav class="sidebar-nav favorite-nav" v-if="isLoggedIn">
          <h3 class="nav-title">즐겨찾기</h3>
          <ul>
            <li><router-link to="/main/favorite-channels" class="action-link">즐겨찾는 채널</router-link></li>
            <li><router-link to="/main/favorite-videos" class="action-link">즐겨찾는 영상</router-link></li>
          </ul>
        </nav>
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
            <li><router-link to="/main/economic-news">경제 뉴스 검색</router-link></li>
            <li><router-link to="/main/nearby-banks">은행 찾기</router-link></li>
            <li><router-link to="/main/community">커뮤니티</router-link></li>
          </ul>
        </nav>
      </header>

      <!-- 컨텐츠 표시 영역 -->
      <div class="content-area" data-aos="fade-up" data-aos-delay="200">
        <router-view v-slot="{ Component, route }" name="mainServiceView">
          <keep-alive include="EconomicNewsView">
            <component :is="Component" :key="route.name" />
          </keep-alive>
        </router-view>
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
import defaultProfileImageSrc from '@/assets/default_profile.png'; // 기본 이미지 경로 import

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
const currentUser = computed(() => authStore.currentUser)
const userProfile = computed(() => authStore.getUserProfile)

const profileImageUrl = computed(() => {
  if (userProfile.value && userProfile.value.profile_image) {
    return userProfile.value.profile_image;
  }
  return defaultProfileImageSrc;
})

// 로그아웃 함수
const logout = async () => {
  await authStore.logoutAction() // 스토어의 로그아웃 액션 호출
  router.push('/') // 로그아웃 후 랜딩 페이지 등으로 이동
}

onMounted(() => {
  AOS.init()
  console.log('[MainPageView] onMounted: 시작')
  console.log('[MainPageView] onMounted: currentUser:', currentUser.value)
  // 로그인 상태이고, 스토어에 프로필 정보가 아직 없다면 가져오기
  if (isLoggedIn.value && !userProfile.value) {
    authStore.fetchProfile();
  }
  console.log('[MainPageView] onMounted: 종료')
})

// 현재 라우트가 MainPageView의 기본 경로인지 확인하는 computed 속성
const isMainPageDefaultView = computed(() => {
  return route.path === '/main' && route.name === 'mainPageDefault'
})

// 로그인 상태 변경 감시: 로그인 되었는데 프로필 정보가 없다면 가져오기
watch(isLoggedIn, (newIsLoggedIn) => {
  if (newIsLoggedIn && !userProfile.value) {
    authStore.fetchProfile();
  }
});

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

/* 즐겨찾기 네비게이션 스타일 추가 */
.favorite-nav {
  margin-top: 20px;
  width: 100%;
}

.favorite-nav .nav-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #555;
  margin-bottom: 10px;
  text-align: left;
  padding-left: 5px; /* 약간의 왼쪽 여백 */
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 5px;
}

.favorite-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.favorite-nav li {
  margin-bottom: 8px;
}

.favorite-nav .action-link {
  display: block;
  padding: 8px 10px;
  color: #333;
  text-decoration: none;
  border-radius: 4px;
  font-size: 0.95rem;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.favorite-nav .action-link:hover,
.favorite-nav .action-link.router-link-active {
  background-color: #e0e0e0; /* 호버 및 활성 링크 배경색 */
  color: #0064FF;
  font-weight: 500;
}
</style> 