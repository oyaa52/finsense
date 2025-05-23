import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'

import App from './App.vue'
import router from './router'
import AOS from 'aos'
import 'aos/dist/aos.css'

// Axios 기본 URL 설정
axios.defaults.baseURL = 'http://127.0.0.1:8000'
// 인증 토큰이 있다면 모든 요청에 포함 (authStore의 initializeAuth에서도 처리하지만, 여기서도 명시 가능)
// const token = localStorage.getItem('accessToken')
// if (token) {
//   axios.defaults.headers.common['Authorization'] = `Token ${token}`
// }

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.AOS = AOS;

app.mount('#app')
