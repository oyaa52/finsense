import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import AOS from 'aos'
import 'aos/dist/aos.css'
import { useAuthStore } from '@/stores/authStore'

// Axios 기본 URL 설정
axios.defaults.baseURL = 'http://127.0.0.1:8000'

// 인증 토큰이 있다면 모든 요청에 포함
const token = localStorage.getItem('accessToken')
if (token) {
  axios.defaults.headers.common['Authorization'] = `Token ${token}`
}

// Axios 인터셉터 설정
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      authStore._resetAuthSate()
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(AOS.init())

app.mount('#app')
