<template>
  <div class="callback-container">
    <p v-if="isLoading">소셜 로그인 정보를 처리 중입니다...</p>
    <p v-if="error" class="error-message">{{ error }}</p>
    <p v-if="!isLoading && !error">로그인 성공! 잠시 후 메인 페이지로 이동합니다.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import axios from 'axios'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()
const isLoading = ref(true)
const error = ref(null)

onMounted(async () => {
  // URL 쿼리에서 'ott' (One-Time Token) 파라미터 추출
  const ott = route.query.ott

  if (!ott) {
    error.value = '잘못된 접근입니다. OTT 파라미터가 없습니다.'
    isLoading.value = false
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 3000)
    return
  }

  try {
    // Django 백엔드의 새로운 API 엔드포인트 URL
    const apiUrl = `${import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000'}/api/v1/accounts/exchange-onetime-token/`
    
    // OTT를 쿼리 파라미터로 전달
    const response = await axios.get(apiUrl, {
      params: { ott },
      // withCredentials: true // OTT 방식에서는 세션 쿠키가 필수는 아님. 필요시 유지.
    })

    if (response.data && response.data.token && response.data.user_id) {
      const { token, user_id } = response.data
      
      // authStore의 액션 호출 (기존과 동일하거나, 필요시 social용으로 분리)
      const loginResult = await authStore.loginSuccessFromSocial({ token, userId: user_id })

      if (loginResult) {
        // 성공 시 mainPageDefault 또는 적절한 라우트로 이동
        router.push({ name: 'mainPageDefault' })
      } else {
        error.value = authStore.getLoginError || '소셜 로그인 후 토큰 저장에 실패했습니다.' 
        setTimeout(() => {
          router.push({ name: 'login' })
        }, 5000)
      }
    } else {
      throw new Error(response.data.error || 'OTT를 이용한 토큰 정보를 가져오지 못했습니다.')
    }
  } catch (err) {
    console.error('소셜 로그인 콜백 처리 중 오류 (OTT 방식):', err)
    error.value = err.response?.data?.error || err.message || '로그인 처리 중 문제가 발생했습니다. 다시 시도해주세요.'
    setTimeout(() => {
      router.push({ name: 'login' })
    }, 5000)
  } finally {
    isLoading.value = false
  }
})
</script>

<style scoped>
.callback-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
}
.error-message {
  color: red;
  margin-top: 20px;
}
</style> 