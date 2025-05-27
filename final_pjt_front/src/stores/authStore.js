import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue' // watch는 필요시 사용
import axios from 'axios'
import { useRouter } from 'vue-router'

export const useAuthStore = defineStore('auth', () => {
  // --- State --- (ref 사용)
  const API_URL = ref(import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'); // VITE_API_URL 환경 변수 사용, 실패하면 하드코딩
  const accessToken = ref(localStorage.getItem('accessToken') || null)
  const user = ref(JSON.parse(localStorage.getItem('userInfo')) || null)
  const isLoggedIn = ref(!!accessToken.value) // 토큰 유무로 초기 로그인 상태 결정
  const loginError = ref(null)
  const signupError = ref(null) // 회원가입 에러 상태 추가
  const userProfile = ref(null) // 사용자 프로필 정보 상태 추가
  const profileError = ref(null) // 프로필 관련 에러 상태 추가

  // --- Getters --- (computed 사용)
  const isAuthenticated = computed(() => !!accessToken.value && isLoggedIn.value)
  const currentUser = computed(() => user.value)
  const getLoginError = computed(() => loginError.value)
  const getSignupError = computed(() => signupError.value) // 회원가입 에러 게터 추가
  const getUserProfile = computed(() => userProfile.value) // 프로필 정보 게터 추가
  const getProfileError = computed(() => profileError.value) // 프로필 에러 게터 추가

  // --- Actions --- (함수로 정의)
  // 스토어 초기화 시 로컬 스토리지에서 사용자 프로필 정보도 로드하는 헬퍼 함수
  const _loadProfileFromStorage = () => {
    const storedProfile = localStorage.getItem('userProfile');
    if (storedProfile) {
      userProfile.value = JSON.parse(storedProfile);
    }
  };

  // 기존 initializeAuth 함수 수정
  const originalInitializeAuth = () => {
    const tokenFromStorage = localStorage.getItem('accessToken');
    const userInfoFromStorage = localStorage.getItem('userInfo');

    if (tokenFromStorage) {
      accessToken.value = tokenFromStorage;
      isLoggedIn.value = true;
      if (userInfoFromStorage) {
        user.value = JSON.parse(userInfoFromStorage);
      }
      axios.defaults.headers.common['Authorization'] = `Token ${accessToken.value}`;
    } else {
      _resetAuthSate();
    }
  };

  const initializeAuth = () => { // 새 initializeAuth 함수
    originalInitializeAuth(); // 기존 인증 로직 실행
    if (isLoggedIn.value) { // 로그인 상태일 때만 프로필 로드
      _loadProfileFromStorage();
    }
  };

  const login = async (credentials) => {
    loginError.value = null
    try {
      const response = await axios.post(
        `${API_URL.value}/dj-rest-auth/login/`, // API_URL 사용
        credentials
      )

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
        return true
      } else {
        loginError.value = '로그인에 성공했으나, 인증 토큰을 받지 못했습니다.'
        return false
      }
    } catch (error) {
      _resetAuthSate()

      if (error.response && error.response.data) {
        const errors = error.response.data;
        if (typeof errors === 'object' && errors !== null) {
          if (errors.non_field_errors && Array.isArray(errors.non_field_errors)) {
            loginError.value = errors.non_field_errors.join(' ');
          } else if (errors.detail && typeof errors.detail === 'string') {
            loginError.value = errors.detail;
          } else { // 필드 에러로 간주 또는 예상치 못한 객체 형태
            const fieldMessages = {};
            let hasFieldErrors = false;
            for (const key in errors) {
              if (Array.isArray(errors[key]) && errors[key].length > 0) {
                fieldMessages[key] = errors[key].join(' ');
                hasFieldErrors = true;
              } else if (typeof errors[key] === 'string') {
                fieldMessages[key] = errors[key];
                hasFieldErrors = true;
              }
            }
            if (hasFieldErrors) {
              loginError.value = fieldMessages; // 객체 형태로 저장
            } else {
              loginError.value = '아이디 또는 비밀번호가 올바르지 않습니다.'; // 기본 메시지
            }
          }
        } else if (typeof errors === 'string') {
          loginError.value = errors;
        } else {
          loginError.value = '아이디 또는 비밀번호가 올바르지 않습니다.';
        }
      } else if (error.request) {
        loginError.value = '서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.'
      } else {
        loginError.value = '로그인 요청 중 오류가 발생했습니다.'
      }
      return false
    }
  }
  
  const signupAction = async (credentials) => {
    signupError.value = null // 이전 에러 메시지 초기화
    try {
      const response = await axios.post(
        `${API_URL.value}/dj-rest-auth/registration/`, // API_URL 사용
        credentials
      )

      // 회원가입 성공 시 (보통 201 Created)
      // dj-rest-auth는 기본적으로 회원가입 후 바로 로그인시키지 않음.
      // 성공 메시지를 반환하거나, 로그인 페이지로 유도할 수 있음.
      // 여기서는 성공 여부만 반환하고, UI 단에서 후속 처리
      return true 
    } catch (error) {
      if (error.response) {
        console.error('Backend validation error details:', error.response.data);
      }

      if (error.response && error.response.data) {
        const errors = error.response.data;
        if (typeof errors === 'object' && errors !== null) {
           // dj-rest-auth는 필드 에러를 {username: ["error"], email: ["error"]} 형태로 반환
           // non_field_errors나 detail이 올 수도 있음
          if (errors.non_field_errors && Array.isArray(errors.non_field_errors)) {
            signupError.value = errors.non_field_errors.join(' ');
          } else if (errors.detail && typeof errors.detail === 'string') {
            signupError.value = errors.detail;
          } else { // 필드 에러 객체로 처리
            const fieldMessages = {};
            let hasFieldErrors = false;
            for (const key in errors) {
              if (Array.isArray(errors[key]) && errors[key].length > 0) {
                fieldMessages[key] = errors[key].join(' '); // 배열 내 메시지들을 합침
                hasFieldErrors = true;
              } else if (typeof errors[key] === 'string') { // 간혹 문자열로 올 경우
                fieldMessages[key] = errors[key];
                hasFieldErrors = true;
              }
            }
            if (hasFieldErrors) {
              signupError.value = fieldMessages; // 객체 형태로 저장
            } else {
              signupError.value = '회원가입 중 오류가 발생했습니다. 입력 정보를 확인해주세요.';
            }
          }
        } else if (typeof errors === 'string') {
          signupError.value = errors;
        } else {
          signupError.value = '회원가입 중 오류가 발생했습니다. 입력 정보를 확인해주세요.';
        }
      } else if (error.request) {
        signupError.value = '서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.'
      } else {
        signupError.value = '회원가입 요청 중 알 수 없는 오류가 발생했습니다.'
      }
      return false
    }
  }

  // 내부 상태 초기화 헬퍼 함수
  const _resetAuthSate = () => {
    isLoggedIn.value = false
    accessToken.value = null
    user.value = null
    userProfile.value = null // 프로필 정보도 초기화
    loginError.value = null
    signupError.value = null
    profileError.value = null // 프로필 에러도 초기화
    localStorage.removeItem('accessToken')
    localStorage.removeItem('userInfo')
    localStorage.removeItem('userProfile') // 로컬 스토리지에서도 프로필 제거 (선택적)
    delete axios.defaults.headers.common['Authorization']
  }

  const logoutAction = async () => { // async로 변경 (향후 로그아웃 API 호출 대비)
    try {
      // 실제 로그아웃 API 호출 (백엔드에서 토큰 무효화 등 처리)
      await axios.post(`${API_URL.value}/dj-rest-auth/logout/`)
    } catch (error) {
      // 로그아웃 API 호출 실패 시에도 프론트엔드에서는 로그아웃 처리를 진행할 수 있음
      // (예: 로컬 토큰 삭제 등)
      // 다만, 서버 측 토큰이 계속 유효할 수 있다는 점은 인지해야 함.
    }
    
    _resetAuthSate() // API 호출 성공 여부와 관계없이 로컬 상태는 초기화

    // 컴포넌트에서 라우팅 처리하는 것이 일반적이므로 스토어에서 직접 호출은 최소화
    // const router = useRouter() // Composition API 함수는 setup 함수 범위 내에서 호출
    // router.push('/login')
  }

  const fetchUser = async () => {
    if (!accessToken.value) return
    try {
      const response = await axios.get(`${API_URL.value}/dj-rest-auth/user/`)
      user.value = response.data
      localStorage.setItem('userInfo', JSON.stringify(response.data))
    } catch (error) {
      // this.logoutAction() // 토큰 유효하지 않으면 로그아웃 처리 가능
    }
  }
  
  const fetchProfile = async () => {
    if (!accessToken.value) {
      profileError.value = '프로필 정보를 가져오려면 로그인이 필요합니다.'
      return false
    }
    profileError.value = null // 이전 에러 초기화

    const headers = {
      'Authorization': `Token ${accessToken.value}`
    };

    try {
      const response = await axios.get(`${API_URL.value}/api/v1/accounts/profile/`, {
        headers: headers // 수정된 헤더 사용
      })
      userProfile.value = response.data
      localStorage.setItem('userProfile', JSON.stringify(response.data)) // 선택적: 로컬 스토리지에 저장
      return true
    } catch (error) {
      if (error.response) {
        if (error.response.status === 404) {
          profileError.value = '프로필 정보가 아직 등록되지 않았습니다.' 
          // 404의 경우, userProfile.value를 null 또는 빈 객체로 유지하여 UI에서 새 프로필 작성을 유도
        } else if (error.response.status === 403) {
          profileError.value = '프로필 정보에 접근할 권한이 없습니다. 세션이 만료되었거나 유효하지 않은 접근일 수 있습니다. 다시 로그인 해주세요.' // 403 메시지 구체화
        } else if (error.response.data && (error.response.data.detail || error.response.data.error || typeof error.response.data === 'string')) {
          profileError.value = error.response.data.detail || error.response.data.error || error.response.data;
        } else {
          profileError.value = '프로필 정보를 불러오는 중 알 수 없는 오류가 발생했습니다.'
        }
      } else if (error.request) {
        profileError.value = '서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.';
      } else {
        profileError.value = '프로필 정보를 불러오는 중 알 수 없는 오류가 발생했습니다.';
      }
      return false
    }
  }

  const updateProfile = async (profileDataToUpdate) => {
    if (!accessToken.value) {
      profileError.value = '프로필을 수정하려면 로그인이 필요합니다.';
      return false;
    }
    profileError.value = null;

    const headers = {
      'Authorization': `Token ${accessToken.value}`,
      // FormData 사용 시 'Content-Type': 'multipart/form-data'는 axios가 자동으로 설정
    };

    let formData;
    if (profileDataToUpdate instanceof FormData) {
      formData = profileDataToUpdate;
    } else {
      formData = new FormData();
      for (const key in profileDataToUpdate) {
        if (profileDataToUpdate[key] !== null && profileDataToUpdate[key] !== undefined) {
          formData.append(key, profileDataToUpdate[key]);
        }
      }
    }

    try {
      const response = await axios.put(
        `${API_URL.value}/api/v1/accounts/profile/`,
        formData, // FormData 사용
        { headers: headers }
      );
      userProfile.value = response.data; // 업데이트된 프로필 정보로 상태 업데이트
      localStorage.setItem('userProfile', JSON.stringify(response.data)); // 로컬 스토리지도 업데이트
      return true;
    } catch (error) {
      if (error.response && error.response.data) {
        const errors = error.response.data;
        if (typeof errors === 'object' && errors !== null) {
          if (errors.non_field_errors && Array.isArray(errors.non_field_errors)) {
            profileError.value = errors.non_field_errors.join(' ');
          } else if (errors.detail && typeof errors.detail === 'string') {
            profileError.value = errors.detail;
          } else {
            const fieldMessages = {};
            let hasFieldErrors = false;
            for (const key in errors) {
              if (Array.isArray(errors[key]) && errors[key].length > 0) {
                fieldMessages[key] = errors[key].join(' ');
                hasFieldErrors = true;
              } else if (typeof errors[key] === 'string') {
                fieldMessages[key] = errors[key];
                hasFieldErrors = true;
              }
            }
            if (hasFieldErrors) {
              profileError.value = fieldMessages;
            } else {
              profileError.value = '프로필 업데이트 중 오류가 발생했습니다. 입력 정보를 확인해주세요.';
            }
          }
        } else if (typeof errors === 'string') {
          profileError.value = errors;
        } else {
          profileError.value = '프로필 업데이트 중 오류가 발생했습니다. 입력 정보를 확인해주세요.';
        }
      } else if (error.request) {
        profileError.value = '서버에 연결할 수 없습니다. 네트워크 상태를 확인해주세요.';
      } else {
        profileError.value = '프로필 업데이트 요청 중 알 수 없는 오류가 발생했습니다.';
      }
      return false;
    }
  };
  
  // localStorage 변경 감지하여 다른 탭/창 간 상태 동기화 (선택적 고급 기능)
  // watch(accessToken, (newToken) => {
  //   if (!newToken) {
  //     _resetAuthSate();
  //   }
  // });

  // 스토어가 반환해야 하는 모든 상태, 게터, 액션을 객체로 반환
  return {
    API_URL,
    accessToken,
    user,
    isLoggedIn,
    loginError,
    signupError,
    userProfile,
    profileError,
    isAuthenticated,
    currentUser,
    getLoginError,
    getSignupError,
    getUserProfile,
    getProfileError,
    initializeAuth,
    login,
    signupAction,
    logoutAction,
    fetchUser,
    fetchProfile,
    updateProfile,
    _resetAuthSate,
  }
}, {
  persist: true, // persist 옵션이 있다면 유지
}) 