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
  // 메인 App 컴포넌트가 마운트될 때 AOS 라이브러리를 초기화
  // => data-aos 속성을 사용하는 모든 컴포넌트에서 AOS 효과를 전역적으로 사용할 수 있음
  AOS.init({
    duration: 1000, // 애니메이션 지속 시간 (단위 : ms)
    once: false,    // 애니메이션이 한 번만 실행되어야 하는지 여부 (스크롤 내릴 때)
    offset: 100     // 원래 트리거 지점에서의 오프셋 (픽셀 단위)
  })
  authStore.initializeAuth() // 앱 시작 시 인증 상태 초기화
  
  // 토큰이 있으면 사용자 정보 갱신
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
  background-color: #f4f6f8; /* 기본 배경색 변경 가능 */
}

#app {
  /* 필요한 경우 #app에 대한 스타일 */
}
</style>