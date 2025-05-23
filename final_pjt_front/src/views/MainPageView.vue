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
        <!-- 여기에 각 메뉴에 해당하는 컴포넌트가 보여집니다. -->
        <!-- 기본적으로 보여줄 내용이나, 선택되지 않았을 때의 UI를 추가할 수 있습니다. -->
        <div v-if="isMainPageDefaultView" class="default-content">
          <h2>Fin Sense에 오신 것을 환영합니다!</h2>
          <p>상단 메뉴를 선택하여 다양한 금융 서비스를 이용해보세요.</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router' // useRoute import
import AOS from 'aos'
import 'aos/dist/aos.css'
import { useAuthStore } from '@/stores/authStore' // authStore 임포트

const authStore = useAuthStore() // authStore 인스턴스 생성
const router = useRouter()
const route = useRoute() // 현재 라우트 정보를 가져오기 위해 추가

// authStore의 상태를 computed 속성으로 사용
const isLoggedIn = computed(() => authStore.isAuthenticated)
const currentUser = computed(() => authStore.currentUser) // dj-rest-auth/user/의 응답을 기반으로 함

// 로그아웃 함수
const logout = async () => {
  await authStore.logoutAction() // 스토어의 로그아웃 액션 호출
  router.push('/') // 로그아웃 후 랜딩 페이지 등으로 이동
}

onMounted(() => {
  AOS.init()
  // authStore.initializeAuth()가 App.vue에서 이미 호출되므로 여기서 별도 호출 필요 없을 수 있음
  // 만약 사용자가 직접 /main으로 접근했을 때 사용자 정보를 가져오고 싶다면 다음을 고려:
  // if (isLoggedIn.value && !currentUser.value) {
  //   authStore.fetchUser(); 
  // }
})

// 현재 라우트가 MainPageView의 기본 경로인지 확인하는 computed 속성
// $route.name을 직접 사용하는 대신, $route.matched를 사용하여 nested routes에서도 정확히 작동하도록 수정
const isMainPageDefaultView = computed(() => {
  // 현재 활성화된 라우트 중 mainServiceView라는 이름을 가진 자식 라우트가 있는지 확인
  return !route.matched.some(record => record.components && record.components.mainServiceView)
})

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

/* AOS Animations */
[data-aos] {
  transition-property: transform, opacity;
}
</style> 