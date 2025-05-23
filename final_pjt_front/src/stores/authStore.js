import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue' // watch는 필요시 사용
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  // --- State --- (ref 사용)
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const user = ref(JSON.parse(localStorage.getItem('userInfo')) || null)
  const isLoggedIn = ref(!!accessToken.value) // 토큰 유무로 초기 로그인 상태 결정
  const loginError = ref(null)

  // --- Getters --- (computed 사용)
  const isAuthenticated = computed(() => !!accessToken.value && isLoggedIn.value)
  const currentUser = computed(() => user.value)
  const getLoginError = computed(() => loginError.value)

  // --- Actions --- (함수로 정의)
  const initializeAuth = () => {
    const tokenFromStorage = localStorage.getItem('accessToken')
    const userInfoFromStorage = localStorage.getItem('userInfo')

    if (tokenFromStorage) {
      accessToken.value = tokenFromStorage
      isLoggedIn.value = true
      if (userInfoFromStorage) {
        user.value = JSON.parse(userInfoFromStorage)
      }
      axios.defaults.headers.common['Authorization'] = `Token ${accessToken.value}`
    } else {
      // 토큰이 없으면 로그아웃 상태로 확실히 처리
      _resetAuthSate()
    }
  }

  const login = async (credentials) => {
    loginError.value = null
    try {
      console.log('Pinia setup store login action. Credentials:', credentials)
      const response = await axios.post(
        'http://127.0.0.1:8000/dj-rest-auth/login/', 
        credentials
      )
      console.log('Login API response:', response.data)

      const tokenData = response.data.key
      const userData = response.data.user

      if (tokenData) {
        accessToken.value = tokenData
        isLoggedIn.value = true
        localStorage.setItem('accessToken', tokenData)

        if (userData) {
          user.value = userData
          localStorage.setItem('userInfo', JSON.stringify(userData))
        } else {
          user.value = null
          localStorage.removeItem('userInfo')
        }
        axios.defaults.headers.common['Authorization'] = `Token ${tokenData}`
        console.log('로그인 성공 (Pinia Setup Store), 토큰 및 사용자 정보 저장.')
        return true
      } else {
        loginError.value = '로그인에 성공했으나, 인증 토큰을 받지 못했습니다.'
        console.error('Login success, but no token received.', response.data)
        return false
      }
    } catch (error) {
      console.error('로그인 API 요청 실패 (Pinia Setup Store):', error)
      _resetAuthSate()

      if (error.response) {
        let errorMessage = '아이디 또는 비밀번호가 올바르지 않습니다.'
        if (error.response.data) {
          if (error.response.data.non_field_errors && error.response.data.non_field_errors.length > 0) {
            errorMessage = error.response.data.non_field_errors.join(' ')
          } else if (Array.isArray(error.response.data) && error.response.data.length > 0 && typeof error.response.data[0] === 'string') {
            errorMessage = error.response.data.join(' ')
          } else if (typeof error.response.data === 'object' && Object.keys(error.response.data).length > 0) {
            const fieldErrors = Object.values(error.response.data).flat().join(' ')
            if (fieldErrors) errorMessage = fieldErrors
          }
        }
        loginError.value = errorMessage
      } else if (error.request) {
        loginError.value = '서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.'
      } else {
        loginError.value = '로그인 요청 중 오류가 발생했습니다.'
      }
      return false
    }
  }
  
  // 내부 상태 초기화 헬퍼 함수
  const _resetAuthSate = () => {
    isLoggedIn.value = false
    accessToken.value = null
    user.value = null
    loginError.value = null
    localStorage.removeItem('accessToken')
    localStorage.removeItem('userInfo')
    delete axios.defaults.headers.common['Authorization']
  }

  const logoutAction = async () => { // async로 변경 (향후 로그아웃 API 호출 대비)
    console.log('Pinia setup store logout action.')
    _resetAuthSate()
    
    // 필요하다면 로그아웃 API 호출 (주석 처리된 부분 참고)
    // try {
    //   await axios.post('http://127.0.0.1:8000/dj-rest-auth/logout/');
    //   console.log('Successfully called logout API');
    // } catch (error) {
    //   console.error('Logout API call failed:', error);
    // }

    // 컴포넌트에서 라우팅 처리하는 것이 일반적이므로 스토어에서 직접 호출은 최소화
    // const router = useRouter() // Composition API 함수는 setup 함수 범위 내에서 호출
    // router.push('/login')
  }

  const fetchUser = async () => {
    if (!accessToken.value) return
    try {
      const response = await axios.get('http://127.0.0.1:8000/dj-rest-auth/user/')
      user.value = response.data
      localStorage.setItem('userInfo', JSON.stringify(response.data))
      console.log('User info fetched (Pinia Setup Store):', response.data)
    } catch (error) {
      console.error('Failed to fetch user info (Pinia Setup Store):', error)
      // this.logoutAction() // 토큰 유효하지 않으면 로그아웃 처리 가능
    }
  }
  
  // localStorage 변경 감지하여 다른 탭/창 간 상태 동기화 (선택적 고급 기능)
  // watch(accessToken, (newToken) => {
  //   if (!newToken) {
  //     _resetAuthSate();
  //   }
  // });

  // 스토어가 반환해야 하는 모든 상태, 게터, 액션을 객체로 반환
  return {
    accessToken,
    user,
    isLoggedIn,
    loginError,
    isAuthenticated,
    currentUser,
    getLoginError,
    initializeAuth,
    login,
    logoutAction,
    fetchUser
  }
}) 