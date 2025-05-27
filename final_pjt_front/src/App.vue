<template>
  <div id="app">
    <RouterView />
    <CustomAlert 
      v-if="alertStore.isVisible"
      :title="alertStore.title"
      :message="alertStore.message"
      :type="alertStore.type"
      :show-confirm-button="!!alertStore.confirmCallback" 
      @confirm="handleConfirm"
      @close="handleClose"
    />
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router';
import CustomAlert from '@/components/CustomAlert.vue';
import { useAlertStore } from '@/stores/alertStore';
import { onMounted } from 'vue'
import AOS from 'aos'
import 'aos/dist/aos.css'
import { useAuthStore } from '@/stores/authStore'
import '@fortawesome/fontawesome-free/css/all.css'

const alertStore = useAlertStore()
const authStore = useAuthStore()

const handleConfirm = () => {
  alertStore.confirmAlert()
}

const handleClose = () => {
  alertStore.closeAlert()
}

onMounted(() => {
  // AOS 라이브러리 초기화, data-aos 속성을 사용하는 모든 컴포넌트에서 전역적 사용 가능
  AOS.init({
    duration: 1000, // 애니메이션 지속 시간 (ms)
    once: false,    // 애니메이션 한 번만 실행 여부 (스크롤 시)
    offset: 100     // 트리거 지점 오프셋 (px)
  })
  authStore.initializeAuth() // 앱 시작 시 인증 상태 초기화

  // 토큰 존재 시 사용자 정보 갱신
  if (authStore.isAuthenticated) {
    authStore.fetchUser()
  }
})
</script>

<style>
/* 전역 스타일 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}

*, *::before, *::after {
  box-sizing: inherit;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f4f6f8; /* 기본 배경색 */
}

#app {
  /* #app 관련 스타일 */
}
</style>