<template>
  <div class="signup-container">
    <div class="signup-card">
      <h2 class="signup-title">회원가입</h2>
      <form @submit.prevent="handleSignup" class="signup-form">
        <div class="form-group">
          <label for="username">아이디</label>
          <input type="text" id="username" v-model="username" required placeholder="아이디를 입력하세요">
          <span v-if="fieldErrors && fieldErrors.username" class="field-error-message">{{ fieldErrors.username }}</span>
        </div>
        <div class="form-group">
          <label for="email">이메일</label>
          <input type="email" id="email" v-model="email" required placeholder="이메일 주소를 입력하세요">
          <span v-if="fieldErrors && fieldErrors.email" class="field-error-message">{{ fieldErrors.email }}</span>
        </div>
        <div class="form-group">
          <label for="password">비밀번호</label>
          <input type="password" id="password" v-model="password" required placeholder="비밀번호를 입력하세요">
          <span v-if="fieldErrors && fieldErrors.password1" class="field-error-message">{{ fieldErrors.password1 }}</span>
        </div>
        <div class="form-group">
          <label for="password2">비밀번호 확인</label>
          <input type="password" id="password2" v-model="password2" required placeholder="비밀번호를 다시 입력하세요">
          <span v-if="fieldErrors && fieldErrors.password2" class="field-error-message">{{ fieldErrors.password2 }}</span>
        </div>

        <!-- 일반 에러 메시지 (non_field_errors 또는 detail) -->
        <div v-if="generalErrorMessage" class="error-message">
          <pre>{{ generalErrorMessage }}</pre>
        </div>
        
        <div v-if="passwordMismatchError" class="error-message">
          <p>비밀번호가 일치하지 않습니다.</p>
        </div>

        <button type="submit" class="signup-button">가입하기</button>
      </form>
      <div class="login-link">
        이미 계정이 있으신가요? <router-link to="/login">로그인</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const password = ref('')
const password2 = ref('')
const passwordMismatchError = ref(false)

// 스토어의 signupError 상태를 가져옴
const signupError = computed(() => authStore.getSignupError)

// 필드별 에러 객체를 위한 computed 속성
const fieldErrors = computed(() => {
  const error = signupError.value;
  return (typeof error === 'object' && error !== null) ? error : null;
})

// 일반 에러 메시지 (문자열)를 위한 computed 속성
const generalErrorMessage = computed(() => {
  const error = signupError.value;
  return (typeof error === 'string') ? error : null;
})

const handleSignup = async () => {
  // authStore.signupAction 시작 시 에러가 초기화되므로, 여기서 별도 초기화는 생략 가능
  // authStore.signupError = null 
  passwordMismatchError.value = false

  if (password.value !== password2.value) {
    passwordMismatchError.value = true
    // 비밀번호 불일치 시 필드별 에러가 있다면 함께 표시될 수 있으므로, 
    // signupError를 여기서 초기화하지 않는 것이 좋을 수 있음.
    // 또는 특정 필드 에러로 통합 관리도 고려.
    return
  }

  const credentials = {
    username: username.value,
    email: email.value,
    password1: password.value,
    password2: password2.value
  }

  const success = await authStore.signupAction(credentials)

  if (success) {
    alert('회원가입이 완료되었습니다. 로그인 페이지로 이동합니다.')
    router.push({ name: 'login' })
  }
  // 실패 시 에러 메시지는 fieldErrors 또는 generalErrorMessage를 통해 template에서 자동으로 표시됨
}
</script>

<style scoped>
/* Noto Sans KR 폰트 import (LoginView와 동일하게) */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

.signup-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #121212; /* 어두운 배경 (LoginView 참고) */
  font-family: 'Noto Sans KR', sans-serif; /* 폰트 적용 */
  padding: 20px;
}

.signup-card {
  background-color: #1e1e1e; /* 살짝 밝은 어두운 배경 (LoginView 참고) */
  padding: 40px 50px;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
  width: 100%;
  max-width: 450px; /* LoginView와 유사한 너비 */
  text-align: center;
  border: 1px solid #282828; /* LoginView 참고 */
}

.signup-title {
  color: #007bff; /* 파란색 강조 (LoginView 참고) */
  margin-bottom: 30px; /* LoginView 참고 */
  font-size: 1.8rem; /* LoginView 참고 */
  font-weight: 700;
}

.signup-form .form-group {
  margin-bottom: 15px; /* 필드 에러 메시지 공간 확보를 위해 약간 줄임 */
  text-align: left;
  position: relative; /* 필드 에러 메시지 위치 기준 */
}

.signup-form label {
  display: block;
  color: #cccccc; /* 밝은 회색 텍스트 (LoginView 참고) */
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.signup-form input[type="text"],
.signup-form input[type="email"],
.signup-form input[type="password"] {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #333;
  border-radius: 8px;
  background-color: #252525; /* 입력 필드 배경 (LoginView 참고) */
  color: #e0e0e0; /* 입력 텍스트 색상 (LoginView 참고) */
  font-size: 1rem;
  box-sizing: border-box;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.signup-form input[type="text"]:focus,
.signup-form input[type="email"]:focus,
.signup-form input[type="password"]:focus {
  border-color: #007bff; /* LoginView 참고 */
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25); /* LoginView 참고 */
  outline: none;
}

.field-error-message {
  display: block;
  color: #ff4d4d; /* 에러 색상 */
  font-size: 0.8rem;
  margin-top: 4px;
  /* position: absolute; */ /* 필요에 따라 절대 위치로 조정 */
  /* bottom: -18px; */
}

.error-message {
  background-color: rgba(255, 0, 0, 0.1);
  color: #ff4d4d;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 15px; /* 간격 조정 */
  font-size: 0.9rem;
  border: 1px solid #ff4d4d;
  text-align: left;
}
.error-message pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: inherit;
}

.signup-button {
  width: 100%;
  padding: 15px; /* LoginView 참고 */
  background-color: #0064FF; /* 메인 파란색 (LoginView 참고) */
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem; /* LoginView 참고 */
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin-top: 10px; 
}

.signup-button:hover {
  background-color: #0052cc; /* LoginView 참고 */
  transform: translateY(-2px);
}

.login-link {
  margin-top: 25px; /* LoginView 참고 */
  font-size: 0.9rem;
}

.login-link a {
  color: #0095ff; /* 밝은 파란색 링크 (LoginView 참고) */
  text-decoration: none;
  margin: 0 8px;
  transition: color 0.3s ease;
}

.login-link a:hover {
  color: #007bff;
  text-decoration: underline;
}
</style> 