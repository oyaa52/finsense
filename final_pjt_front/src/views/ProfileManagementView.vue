<template>
  <div class="profile-management-container" data-aos="fade-up">
    <h2 class="view-title">회원 정보 관리</h2>
    <div v-if="isLoading" class="loading-indicator">
      <p>프로필 정보를 불러오는 중입니다...</p>
      <!-- 로딩 스피너 등을 추가할 수 있습니다 -->
    </div>
    <div v-else-if="initialLoadingError && !profileDataFromStore" class="error-message">
      <p>{{ initialLoadingError }}</p>
    </div>
    <form v-else @submit.prevent="handleProfileUpdate" class="profile-form">
      <div class="form-section">
        <h3 class="section-title">기본 정보</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="age">나이</label>
            <input type="number" id="age" v-model.number="profileData.age" placeholder="나이를 입력하세요">
            <span v-if="fieldErrors && fieldErrors.age" class="field-error-message">{{ fieldErrors.age }}</span>
          </div>
          <div class="form-group">
            <label for="gender">성별</label>
            <select id="gender" v-model="profileData.gender">
              <option value="">선택하세요</option>
              <option value="male">남성</option>
              <option value="female">여성</option>
            </select>
            <span v-if="fieldErrors && fieldErrors.gender" class="field-error-message">{{ fieldErrors.gender }}</span>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">직업 및 소득 정보</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="occupation">직업</label>
            <input type="text" id="occupation" v-model="profileData.occupation" placeholder="직업을 입력하세요">
            <span v-if="fieldErrors && fieldErrors.occupation" class="field-error-message">{{ fieldErrors.occupation }}</span>
          </div>
          <div class="form-group">
            <label for="marital_status">결혼 상태</label>
            <select id="marital_status" v-model="profileData.marital_status">
              <option value="">선택하세요</option>
              <option value="single">미혼</option>
              <option value="married">기혼</option>
            </select>
            <span v-if="fieldErrors && fieldErrors.marital_status" class="field-error-message">{{ fieldErrors.marital_status }}</span>
          </div>
          <div class="form-group full-width">
            <label for="monthly_income">월 소득 (원)</label>
            <input type="number" id="monthly_income" v-model.number="profileData.monthly_income" placeholder="월 소득을 입력하세요">
            <span v-if="fieldErrors && fieldErrors.monthly_income" class="field-error-message">{{ fieldErrors.monthly_income }}</span>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h3 class="section-title">투자 정보</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="amount_available">사용 가능 금액 (원)</label>
            <input type="number" id="amount_available" v-model.number="profileData.amount_available" placeholder="사용 가능 금액을 입력하세요">
            <span v-if="fieldErrors && fieldErrors.amount_available" class="field-error-message">{{ fieldErrors.amount_available }}</span>
          </div>
           <div class="form-group">
            <label for="investment_term">투자기간 (개월)</label>
            <input type="number" id="investment_term" v-model.number="profileData.investment_term" placeholder="투자기간(개월)을 입력하세요">
            <span v-if="fieldErrors && fieldErrors.investment_term" class="field-error-message">{{ fieldErrors.investment_term }}</span>
          </div>
          <div class="form-group full-width">
            <label for="investment_purpose">투자 목적</label>
            <textarea id="investment_purpose" v-model="profileData.investment_purpose" rows="3" placeholder="주요 투자 목적을 입력하세요 (예: 주택 구매, 노후 자금 마련 등)"></textarea>
            <span v-if="fieldErrors && fieldErrors.investment_purpose" class="field-error-message">{{ fieldErrors.investment_purpose }}</span>
          </div>
          <div class="form-group full-width">
            <label for="investment_tendency">투자 성향</label>
            <select id="investment_tendency" v-model="profileData.investment_tendency">
              <option value="">선택하세요</option>
              <option value="stable">안정형</option>
              <option value="stable_seeking">안정추구형</option>
              <option value="neutral">위험중립형</option>
              <option value="active_investment">적극투자형</option>
              <option value="aggressive">공격투자형</option>
            </select>
            <span v-if="fieldErrors && fieldErrors.investment_tendency" class="field-error-message">{{ fieldErrors.investment_tendency }}</span>
          </div>
        </div>
      </div>

      <div v-if="updateSuccessMessage" class="success-message">
        <p>{{ updateSuccessMessage }}</p>
      </div>
      <div v-if="generalErrorMessage && !updateSuccessMessage" class="error-message">
        <pre>{{ generalErrorMessage }}</pre>
      </div>

      <button type="submit" class="submit-button" :disabled="isUpdating">
        {{ isUpdating ? '저장 중...' : '프로필 저장' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()

const profileData = reactive({
  age: null,
  gender: '',
  occupation: '',
  marital_status: '',
  monthly_income: null,
  amount_available: null,
  investment_purpose: '',
  investment_term: null,
  investment_tendency: ''
})

const isLoading = ref(true)
const isUpdating = ref(false)
const updateSuccessMessage = ref('')
const initialLoadingError = ref(null)

const profileDataFromStore = computed(() => authStore.getUserProfile)

// 스토어의 profileError 상태를 가져옴
const profileError = computed(() => authStore.getProfileError)

// 필드별 에러 객체를 위한 computed 속성
const fieldErrors = computed(() => {
  const error = profileError.value;
  // 에러가 객체이고, 배열이 아니며, detail이나 non_field_errors 키를 직접 가지지 않을 때 필드 에러로 간주
  return (typeof error === 'object' && error !== null && !Array.isArray(error) && !error.detail && !error.non_field_errors) ? error : null;
})

// 일반 에러 메시지 (문자열 또는 detail, non_field_errors)를 위한 computed 속성
const generalErrorMessage = computed(() => {
  const error = profileError.value;
  if (typeof error === 'string') {
    return error;
  }
  if (error && error.detail) {
    return error.detail;
  }
  if (error && Array.isArray(error.non_field_errors)) {
    return error.non_field_errors.join('\\n');
  }
  return null;
})

const loadProfile = async () => {
  isLoading.value = true;
  initialLoadingError.value = null;
  updateSuccessMessage.value = ''; // 이전 성공 메시지 초기화

  // 스토어의 에러 상태를 프로필 로드 전에 초기화하는 것을 고려할 수 있습니다.
  // 예: authStore.clearProfileError(); 또는 authStore.profileError = null;

  const success = await authStore.fetchProfile();
  if (!success) {
    const errorValue = profileError.value;
    if (typeof errorValue === 'string') {
      initialLoadingError.value = errorValue;
    } else if (errorValue && errorValue.detail) {
      initialLoadingError.value = errorValue.detail;
    } else if (errorValue && Array.isArray(errorValue.non_field_errors)) {
      initialLoadingError.value = errorValue.non_field_errors.join('\\n');
    } else if (fieldErrors.value && Object.keys(fieldErrors.value).length > 0) {
      initialLoadingError.value = '프로필 정보를 불러오는 중 일부 항목에 오류가 있습니다.';
    } else {
      initialLoadingError.value = '프로필 정보를 불러오는 중 알 수 없는 오류가 발생했습니다. 다시 시도해주세요.';
    }
  }
  isLoading.value = false;
};

watch(profileDataFromStore, (newProfile) => {
  if (newProfile) {
    Object.assign(profileData, newProfile);
    // profileData의 각 키에 대해 null 값 처리
    for (const key of Object.keys(profileData)) {
      if (profileData[key] === null) {
        const numericKeys = ['age', 'monthly_income', 'amount_available', 'investment_term'];
        // 숫자 타입이 아닌 필드가 null일 경우 빈 문자열로 설정 (폼 바인딩 개선 목적)
        if (!numericKeys.includes(key)) {
          profileData[key] = '';
        }
        // 숫자 타입 필드가 null인 경우 그대로 null 유지
      }
    }
  } else {
    // 스토어 프로필이 null이 되면 (예: 로그아웃 시) 로컬 폼 데이터 초기화
    Object.keys(profileData).forEach(key => {
      const numericKeys = ['age', 'monthly_income', 'amount_available', 'investment_term'];
      if (numericKeys.includes(key)) {
        profileData[key] = null;
      } else {
        profileData[key] = '';
      }
    });
  }
}, { immediate: true, deep: true });

const handleProfileUpdate = async () => {
  isUpdating.value = true
  updateSuccessMessage.value = ''
  // 업데이트 시도 전에 스토어의 에러 상태 초기화 (선택적, 스토어 액션에서 처리 권장)
  // authStore.profileError = null 

  const success = await authStore.updateProfile({ ...profileData })

  if (success) {
    updateSuccessMessage.value = '프로필 정보가 성공적으로 업데이트되었습니다.'
  }
  isUpdating.value = false
}

onMounted(() => {
  if (authStore.isAuthenticated) {
    loadProfile()
  } else {
    initialLoadingError.value = '로그인이 필요합니다. 로그인 후 다시 시도해주세요.'
    isLoading.value = false
  }
})

</script>

<style scoped>
/* MainPageView의 content-area와 유사한 스타일 또는 Login/Signup 폼 스타일 적용 */
.profile-management-container {
  padding: 20px;
  background-color: #1f1f1f; /* MainPageView content-area 배경색 */
  color: #e0e0e0; /* 기본 텍스트 색상 */
  border-radius: 8px;
  height: 100%; /* 부모 요소(content-area)에 맞춰 채우기 */
  overflow-y: auto; /* 내용 많을 시 스크롤 */
}

.view-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #007bff; /* 파란색 강조 */
  margin-bottom: 25px;
  border-bottom: 1px solid #333;
  padding-bottom: 15px;
}

.loading-indicator p,
.error-message p,
.success-message p {
  text-align: center;
  padding: 15px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.loading-indicator p {
  color: #cccccc;
}

.error-message {
  background-color: rgba(255, 0, 0, 0.1);
  color: #ff4d4d;
  border: 1px solid #ff4d4d;
  padding: 10px; /* 패딩 일관성 */
  border-radius: 6px;
  margin-bottom: 20px;
  text-align: left; /* 텍스트 왼쪽 정렬 추가 */
}

.error-message pre {
  white-space: pre-wrap; /* 공백과 줄바꿈 유지 */
  word-wrap: break-word; /* 긴 단어 자동 줄바꿈 */
  margin: 0; /* pre 태그 기본 마진 제거 */
  font-family: inherit; /* 부모 폰트 상속 */
}

.success-message {
  background-color: rgba(0, 255, 0, 0.1);
  color: #4caf50;
  border: 1px solid #4caf50;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.profile-form {
  max-width: 800px; /* 폼 최대 너비 */
  margin: 0 auto; /* 가운데 정렬 */
}

.form-section {
  background-color: #252525; /* 섹션 배경색 */
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}

.section-title {
  font-size: 1.3rem;
  font-weight: 500;
  color: #0095ff; /* 밝은 파란색 */
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #444;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); /* 반응형 그리드 */
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1; /* 그리드 전체 너비 사용 */
}

.form-group label {
  display: block;
  color: #cccccc;
  margin-bottom: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input[type="email"], /* 필요 시 이메일 필드 */
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #333;
  border-radius: 6px;
  background-color: #1e1e1e; /* 입력 필드 배경 */
  color: #e0e0e0;
  font-size: 0.95rem;
  box-sizing: border-box;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.25);
  outline: none;
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.submit-button {
  display: block;
  width: auto;
  min-width: 150px;
  padding: 12px 30px;
  background-color: #0064FF;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin: 30px auto 0; /* 상단 여백 및 가운데 정렬 */
}

.submit-button:disabled {
  background-color: #555;
  cursor: not-allowed;
}

.submit-button:not(:disabled):hover {
  background-color: #0052cc;
  transform: translateY(-2px);
}

.field-error-message {
  display: block;
  color: #ff4d4d; /* 에러 색상 */
  font-size: 0.8rem;
  margin-top: 4px;
  /* position: absolute; 와 같은 스타일은 필요시 추가 */
}
</style> 