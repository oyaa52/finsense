<template>
  <div class="login-page-container" data-aos="fade-in">
    <div class="login-form-wrapper">
      <div class="logo-container">
        <router-link to="/main">
          <img src="@/assets/FS_logo.png" alt="Fin Sense Logo" class="login-logo"/>
        </router-link>
        <h2>Fin Sense 로그인</h2>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input type="text" id="username" v-model="username" placeholder="아이디를 입력하세요" required />
          <span v-if="fieldErrors && fieldErrors.username" class="field-error-message">{{ fieldErrors.username }}</span>
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input type="password" id="password" v-model="password" placeholder="비밀번호를 입력하세요" required />
          <span v-if="fieldErrors && fieldErrors.password" class="field-error-message">{{ fieldErrors.password }}</span>
        </div>
        
        <div v-if="generalErrorMessage" class="error-message">
          <pre>{{ generalErrorMessage }}</pre>
        </div>

        <button type="submit" class="login-button">로그인</button>
      </form>

      <div class="links">
        <router-link to="/signup">회원가입</router-link>
        <span>|</span>
        <router-link to="/find-credentials">아이디/비밀번호 찾기</router-link>
      </div>

      <!-- Social Login Buttons Start -->
      <div class="social-login-container">
        <div class="social-login-divider">
          <span>OR</span>
        </div>
        <a :href="`${djangoBaseUrl}/accounts/google/login/?process=login`" class="social-login-btn google-btn">
          <img src="@/assets/google-logo.png" alt="Google logo" class="social-logo"/> Google로 계속하기
        </a>
        <a :href="`${djangoBaseUrl}/accounts/kakao/login/?process=login`" class="social-login-btn kakao-btn">
          <img src="@/assets/kakao-logo.png" alt="Kakao logo" class="social-logo"/> Kakao로 계속하기
        </a>
      </div>
      <!-- Social Login Buttons End -->

       <div class="home-link-container">
        <router-link to="/main" class="home-button">홈으로 돌아가기</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import AOS from 'aos'
import 'aos/dist/aos.css'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

const username = ref('')
const password = ref('')

const router = useRouter()
const authStore = useAuthStore()

// Django 백엔드 기본 URL (소셜 로그인 링크용)
const djangoBaseUrl = import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000';

const loginError = computed(() => authStore.getLoginError)

const fieldErrors = computed(() => {
  const error = loginError.value;
  return (typeof error === 'object' && error !== null && !Array.isArray(error)) ? error : null;
})

const generalErrorMessage = computed(() => {
  const error = loginError.value;
  if (typeof error === 'string') {
    return error;
  }
  if (error && error.detail) {
    return error.detail;
  }
  if (error && Array.isArray(error.non_field_errors)) {
    return error.non_field_errors.join('\n');
  }
  if (Array.isArray(error)) {
    return error.join('\n');
  }
  return null;
})

const handleLogin = async () => {
  const success = await authStore.login({ 
    username: username.value, 
    password: password.value 
  })

  if (success) {
    console.log('LoginView: 로그인 성공, 사용자 정보를 가져옵니다.')
    await authStore.fetchUser()
    console.log('LoginView: 사용자 정보 로드 완료, 메인 페이지로 이동합니다.')
    router.push('/main')
  } else {
    console.log('LoginView: 로그인 실패.')
  }
}

onMounted(() => {
  AOS.init()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

.login-page-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #121212; /* 어두운 배경 */
  font-family: 'Noto Sans KR', sans-serif;
  padding: 20px;
}

.login-form-wrapper {
  background-color: #1e1e1e; /* 살짝 밝은 어두운 배경 */
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 450px;
  text-align: center;
  border: 1px solid #282828;
}

.logo-container {
  margin-bottom: 30px;
}

.login-logo {
  max-width: 120px; /* 메인 페이지 사이드바 로고보다 약간 작게 */
  margin-bottom: 10px;
}

.logo-container h2 {
  color: #007bff; /* 파란색 강조 */
  font-size: 1.8rem;
  font-weight: 700;
  margin: 0;
}

.login-form .form-group {
  margin-bottom: 20px;
  text-align: left;
}

.form-group label {
  display: block;
  color: #cccccc; /* 밝은 회색 텍스트 */
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="password"] {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #333;
  border-radius: 8px;
  background-color: #252525; /* 입력 필드 배경 */
  color: #e0e0e0; /* 입력 텍스트 색상 */
  font-size: 1rem;
  box-sizing: border-box; /* 패딩과 테두리가 너비에 포함되도록 */
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input[type="text"]:focus,
.form-group input[type="password"]:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}

.login-button {
  width: 100%;
  padding: 15px;
  background-color: #0064FF; /* 메인 파란색 */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin-top: 10px; /* 에러 메시지와의 간격 */
}

.login-button:hover {
  background-color: #0052cc;
  transform: translateY(-2px);
}

.field-error-message {
  display: block;
  color: #ff4d4d; /* 에러 색상 */
  font-size: 0.8rem;
  margin-top: 4px;
}

.error-message {
  background-color: rgba(255, 0, 0, 0.1);
  color: #ff4d4d;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px;
  font-size: 0.9rem;
  border: 1px solid #ff4d4d;
  text-align: left; /* 텍스트 왼쪽 정렬 추가 */
}

.error-message pre {
  white-space: pre-wrap; /* 공백과 줄바꿈 유지 */
  word-wrap: break-word; /* 긴 단어 자동 줄바꿈 */
  margin: 0; /* pre 태그 기본 마진 제거 */
  font-family: inherit; /* 부모 폰트 상속 */
}

.links {
  margin-top: 25px;
  font-size: 0.9rem;
}

.links a {
  color: #0095ff; /* 밝은 파란색 링크 */
  text-decoration: none;
  margin: 0 8px;
  transition: color 0.3s ease;
}

.links a:hover {
  color: #007bff;
  text-decoration: underline;
}

.links span {
  color: #555; /* 구분선 색상 */
}

.home-link-container {
  margin-top: 30px;
}

.home-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: transparent;
  color: #007bff;
  border: 1px solid #007bff;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.3s ease, color 0.3s ease;
}

.home-button:hover {
  background-color: #007bff;
  color: #ffffff;
}

/* Social Login Styles */
.social-login-container {
  margin-top: 25px;
  margin-bottom: 25px;
}

.social-login-divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #888;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.social-login-divider::before,
.social-login-divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #444;
}

.social-login-divider span {
  padding: 0 15px;
}

.social-login-btn {
  display: flex; /* 로고와 텍스트 정렬을 위해 flex 사용 */
  align-items: center; /* 세로 중앙 정렬 */
  justify-content: center; /* 가로 중앙 정렬 */
  width: 100%;
  padding: 12px 15px;
  margin-bottom: 12px;
  border-radius: 8px;
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease, box-shadow 0.2s ease;
  border: 1px solid transparent; /* 테두리 초기화 */
  box-sizing: border-box;
}

.social-logo {
  width: 20px; /* 로고 크기 */
  height: 20px; /* 로고 크기 */
  margin-right: 10px; /* 로고와 텍스트 간격 */
}

.google-btn {
  background-color: #fff;
  color: #444; /* 구글은 보통 검은색 또는 회색 텍스트 */
  border: 1px solid #ddd;
}

.google-btn:hover {
  background-color: #f8f8f8;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.kakao-btn {
  background-color: #FEE500;
  color: #3C1E1E; /* 카카오 텍스트 색상 */
  border: 1px solid #FEE500;
}

.kakao-btn:hover {
  background-color: #fada0a;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
</style> 