<template>
  <div class="profile-management-container" data-aos="fade-up">
    <h2 class="view-title">회원 정보 관리</h2>
    <div v-if="isLoading" class="loading-indicator">
      <p>프로필 정보를 불러오는 중입니다...</p>
    </div>
    <div v-else-if="initialLoadingError && !profileDataFromStore" class="error-message">
      <p>{{ initialLoadingError }}</p>
    </div>
    <form v-else @submit.prevent="handleProfileUpdate" class="profile-form">
      <!-- 프로필 이미지 섹션 -->
      <div class="form-section profile-image-section">
        <h3 class="section-title">프로필 이미지</h3>
        <div class="profile-image-controls">
          <img :src="profileImageUrl" alt="Profile Image" class="profile-image-preview" @click="triggerFileInput">
          <input type="file" ref="fileInput" @change="handleFileChange" accept="image/*" style="display: none;">
          <button type="button" @click="triggerFileInput" class="change-image-button">이미지 변경</button>
          <p v-if="selectedFileName" class="selected-file-name">선택된 파일: {{ selectedFileName }}</p>
        </div>
        <span v-if="fieldErrors && fieldErrors.profile_image" class="field-error-message">{{ fieldErrors.profile_image }}</span>
      </div>

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

      <div class="form-section">
        <h3 class="section-title">구독 정보</h3>
        <div class="subscriptions-section">
          <!-- 예금 상품 구독 -->
          <div class="subscription-list">
            <div class="subscription-header">
              <h4>예금 상품</h4>
              <span class="subscription-count">{{ depositSubscriptions.length }}개</span>
            </div>
            <div v-if="depositSubscriptions.length === 0" class="no-subscriptions">
              <i class="fas fa-piggy-bank"></i>
              <p>가입한 예금 상품이 없습니다.</p>
            </div>
            <div v-else class="subscription-grid">
              <div v-for="sub in depositSubscriptions" :key="sub.id" class="subscription-card">
                <div class="card-header">
                  <h6>{{ sub.product_name }}</h6>
                  <span class="bank-badge">{{ sub.bank_name }}</span>
                </div>
                <div class="card-body">
                  <div class="rate-info">
                    <span class="rate-label">금리</span>
                    <span class="rate-value">{{ sub.interest_rate }}%</span>
                  </div>
                  <div class="period-info">
                    <span class="period-label">기간</span>
                    <span class="period-value">{{ sub.period }}개월</span>
                  </div>
                  <div class="date-info">
                    <span class="date-label">가입일</span>
                    <span class="date-value">{{ formatDate(sub.subscribed_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 적금 상품 구독 -->
          <div class="subscription-list">
            <div class="subscription-header">
              <h4>적금 상품</h4>
              <span class="subscription-count">{{ savingSubscriptions.length }}개</span>
            </div>
            <div v-if="savingSubscriptions.length === 0" class="no-subscriptions">
              <i class="fas fa-coins"></i>
              <p>가입한 적금 상품이 없습니다.</p>
            </div>
            <div v-else class="subscription-grid">
              <div v-for="sub in savingSubscriptions" :key="sub.id" class="subscription-card">
                <div class="card-header">
                  <h6>{{ sub.product_name }}</h6>
                  <span class="bank-badge">{{ sub.bank_name }}</span>
                </div>
                <div class="card-body">
                  <div class="rate-info">
                    <span class="rate-label">금리</span>
                    <span class="rate-value">{{ sub.interest_rate }}%</span>
                  </div>
                  <div class="period-info">
                    <span class="period-label">기간</span>
                    <span class="period-value">{{ sub.period }}개월</span>
                  </div>
                  <div class="date-info">
                    <span class="date-label">가입일</span>
                    <span class="date-value">{{ formatDate(sub.subscribed_at) }}</span>
                  </div>
                </div>
              </div>
            </div>
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
import defaultProfileImage from '@/assets/default_profile.png' // 기본 이미지 import
import axios from 'axios'

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
  investment_tendency: '',
  profile_image: null,
})

const isLoading = ref(true)
const isUpdating = ref(false)
const updateSuccessMessage = ref('')
const initialLoadingError = ref(null)

const fileInput = ref(null) // 파일 input 엘리먼트에 대한 ref
const profileImageFile = ref(null) // 선택된 파일 객체
const selectedFileName = ref('') // 선택된 파일명 표시용
const profileImagePreviewUrl = ref(defaultProfileImage) // 이미지 미리보기 URL

const profileDataFromStore = computed(() => authStore.getUserProfile)

const profileImageUrl = computed(() => {
  if (profileImagePreviewUrl.value !== defaultProfileImage && profileImagePreviewUrl.value) { // 새 이미지 선택 시 미리보기
    return profileImagePreviewUrl.value
  }
  if (profileDataFromStore.value && profileDataFromStore.value.profile_image) {
    return profileDataFromStore.value.profile_image
  }
  return defaultProfileImage
})

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

const depositSubscriptions = ref([])
const savingSubscriptions = ref([])

const loadProfile = async () => {
  isLoading.value = true;
  initialLoadingError.value = null;
  updateSuccessMessage.value = ''; // 이전 성공 메시지 초기화
  profileImagePreviewUrl.value = defaultProfileImage; // 미리보기 초기화
  selectedFileName.value = ''; // 파일명 초기화
  profileImageFile.value = null; // 파일 객체 초기화

  const success = await authStore.fetchProfile();
  if (success && profileDataFromStore.value) {
    const { profile_image, ...dataToAssign } = profileDataFromStore.value;
    Object.assign(profileData, dataToAssign);

    for (const key of Object.keys(profileData)) {
      if (profileDataFromStore.value[key] === null) {
        const numericKeys = ['age', 'monthly_income', 'amount_available', 'investment_term'];
        if (numericKeys.includes(key)) {
          profileData[key] = null; 
        } else if (key !== 'profile_image') { 
          profileData[key] = ''; 
        }
      }
    }

  } else if (!success) {
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
    const { profile_image, ...dataToAssign } = newProfile;
    Object.assign(profileData, dataToAssign);

    for (const key of Object.keys(profileData)) {
      if (profileData[key] === null) {
        const numericKeys = ['age', 'monthly_income', 'amount_available', 'investment_term'];
        if (numericKeys.includes(key)) {
          profileData[key] = null;
        } else if (key !== 'profile_image') {
          profileData[key] = '';
        }
      }
    }
  } else {
    Object.keys(profileData).forEach(key => {
      const numericKeys = ['age', 'monthly_income', 'amount_available', 'investment_term'];
      if (numericKeys.includes(key)) {
        profileData[key] = null;
      } else if (key !== 'profile_image') {
        profileData[key] = '';
      }
    });
    profileData.profile_image = null;
    profileImagePreviewUrl.value = defaultProfileImage; 
  }
}, { immediate: true, deep: true });

const triggerFileInput = () => {
  if (fileInput.value) {
    fileInput.value.click();
  }
};

const handleProfileUpdate = async () => {
  isUpdating.value = true;
  updateSuccessMessage.value = '';
  generalErrorMessage.value = '';
  fieldErrors.value = {};

  try {
    // profileData에서 profile_image 제외하고 나머지 데이터 복사
    const { profile_image, ...otherProfileData } = profileData;

    console.log("원본 profileData:", profileData);
    console.log("profile_image 제외한 데이터:", otherProfileData);
    console.log("선택된 파일:", profileImageFile.value);
    console.log("기존 사용자 프로필 이미지:", authStore.userProfile?.profile_image);

    // 이미지 업로드 처리
    if (profileImageFile.value) {
      console.log("이미지 업로드 시작:", profileImageFile.value);
      const publicImageUrl = await authStore.uploadImageToSupabase(profileImageFile.value);
      console.log("이미지 업로드 완료:", publicImageUrl);

      // 업로드된 URL을 추가
      otherProfileData.profile_image = publicImageUrl;
    } else if (authStore.userProfile?.profile_image) {
      // 기존 이미지 유지 (기존 사용자의 profile_image URL)
      otherProfileData.profile_image = authStore.userProfile.profile_image;
      console.log("기존 이미지 URL 사용:", authStore.userProfile.profile_image);
    }
    // 새 이미지도 없고 기존 이미지도 없으면 profile_image 필드 자체를 보내지 않음

    console.log("Django로 전송할 최종 데이터:", otherProfileData);
    console.log("데이터 타입 확인:", typeof otherProfileData, otherProfileData instanceof FormData);

    // ⚠️ 중요: JSON 객체로 전달 (FormData 아님)
    await authStore.updateProfile(otherProfileData);

    updateSuccessMessage.value = '프로필 정보가 성공적으로 업데이트되었습니다.';

    // 성공 후 초기화
    profileImageFile.value = null;
    selectedFileName.value = '';
    profileImagePreviewUrl.value = '';

    // 프로필 다시 가져오기
    await authStore.fetchProfile();

  } catch (error) {
    console.error("프로필 업데이트 오류:", error.response?.data || error);
    if (error.response && error.response.data && typeof error.response.data === 'object') {
      fieldErrors.value = error.response.data;
      generalErrorMessage.value = "입력 내용을 다시 확인해주세요.";
    } else {
      generalErrorMessage.value = error.response?.data?.detail || error.message || '프로필 업데이트에 실패했습니다.';
    }
  } finally {
    isUpdating.value = false;
  }
};


const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await loadProfile()
  } else {
    initialLoadingError.value = '로그인이 필요합니다. 로그인 후 다시 시도해주세요.';
    isLoading.value = false;
  }
});

</script>

<style scoped>
/* MainPageView의 content-area와 유사한 스타일 또는 Login/Signup 폼 스타일 적용 */
.profile-management-container {
  padding: 20px;
  background-color: #ffffff;
  color: #333333;
  border-radius: 8px;
  height: 100%;
  overflow-y: auto;
}

.view-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #4a90e2;
  margin-bottom: 25px;
  border-bottom: 1px solid #e0e0e0;
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
  color: #666666;
}

.error-message {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  border: 1px solid #e74c3c;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
  text-align: left;
}

.error-message pre {
  white-space: pre-wrap; /* 공백과 줄바꿈 유지 */
  word-wrap: break-word; /* 긴 단어 자동 줄바꿈 */
  margin: 0; /* pre 태그 기본 마진 제거 */
  font-family: inherit; /* 부모 폰트 상속 */
}

.success-message {
  background-color: rgba(46, 204, 113, 0.1);
  color: #2ecc71;
  border: 1px solid #2ecc71;
  padding: 10px;
  border-radius: 6px;
  margin-bottom: 20px;
}

.profile-form {
  max-width: 800px; /* 폼 최대 너비 */
  margin: 0 auto; /* 가운데 정렬 */
}

.form-section {
  background-color: #ffffff;
  padding: 25px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #e0e0e0;
}

.section-title {
  font-size: 1.3rem;
  font-weight: 500;
  color: #4a90e2;
  margin-top: 0;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
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
  color: #666666;
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
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background-color: #f8f9fa;
  color: #333333;
  font-size: 0.95rem;
  box-sizing: border-box;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
  outline: none;
  background-color: #ffffff;
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
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  margin: 30px auto 0;
}

.submit-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.submit-button:not(:disabled):hover {
  background-color: #357abd;
  transform: translateY(-2px);
}

.field-error-message {
  display: block;
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 4px;
}

.profile-management {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  background-color: #ffffff;
  border-radius: 15px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.profile-header {
  text-align: center;
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.profile-header h1 {
  color: #333333;
  font-size: 2.2rem;
  margin-bottom: 15px;
  font-weight: 600;
}

.profile-header p {
  color: #666666;
  font-size: 1.1rem;
  line-height: 1.6;
}

.profile-form {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #f0f0f0;
}

.form-group {
  margin-bottom: 25px;
}

.form-group label {
  display: block;
  color: #666666;
  font-size: 1rem;
  margin-bottom: 10px;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  color: #333333;
  transition: all 0.3s ease;
  background-color: #f8f9fa;
}

.form-group input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.1);
  background-color: #ffffff;
}

.form-group input::placeholder {
  color: #999999;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
  justify-content: center;
}

.form-actions button {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.save-button {
  background-color: #4a90e2;
  color: white;
}

.save-button:hover {
  background-color: #357abd;
  transform: translateY(-2px);
}

.cancel-button {
  background-color: #f0f0f0;
  color: #666666;
}

.cancel-button:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
}

.error-message {
  color: #e74c3c;
  font-size: 0.9rem;
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.success-message {
  color: #2ecc71;
  font-size: 0.9rem;
  margin-top: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .profile-management {
    padding: 20px;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions button {
    width: 100%;
  }
}

/* 프로필 이미지 섹션 관련 스타일 */
.profile-image-section {
  /* 기존 form-section 스타일 유지 */
}

.profile-image-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px; /* 요소 간 간격 */
  margin-bottom: 15px; /* 아래쪽 필드 에러 메시지와의 간격 */
}

.profile-image-preview {
  width: 120px; /* 크기 조정 */
  height: 120px; /* 크기 조정 */
  border-radius: 50%; /* 원형으로 */
  object-fit: cover; /* 이미지 비율 유지하며 채우기 */
  cursor: pointer;
  border: 2px solid #e0e0e0; /* 기본 테두리 */
  transition: border-color 0.3s ease;
}

.profile-image-preview:hover {
  border-color: #4a90e2; /* 호버 시 테두리 색상 변경 */
}

.change-image-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s ease, transform 0.2s ease;
  /* margin-top: 0; 제거 또는 필요시 조정 */
}

.change-image-button:hover {
  background-color: #4a90e2;
  transform: translateY(-1px);
}

.selected-file-name {
  font-size: 0.85rem;
  color: #666666;
  margin-top: 5px;
}

.follow-stats {
  display: flex;
  gap: 2rem;
  margin-bottom: 1rem;
}

.follow-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.follow-stat .count {
  font-size: 1.5rem;
  font-weight: bold;
  color: #333;
}

.follow-stat .label {
  font-size: 0.9rem;
  color: #666;
}

.follow-lists {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 1rem;
}

.follow-list {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
}

.follow-list h4 {
  margin-bottom: 1rem;
  color: #333;
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.user-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
}

.username {
  font-weight: 500;
}

.follow-button,
.unfollow-button {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}

.follow-button {
  background: #007bff;
  color: white;
  border: none;
}

.follow-button:hover {
  background: #0056b3;
}

.unfollow-button {
  background: #dc3545;
  color: white;
  border: none;
}

.unfollow-button:hover {
  background: #c82333;
}

.empty-list {
  text-align: center;
  color: #666;
  padding: 1rem;
}

.subscriptions-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}

.subscription-list {
  margin-bottom: 32px;
}

.subscription-list:last-child {
  margin-bottom: 0;
}

.subscription-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f0f0;
}

.subscription-header h4 {
  color: #333;
  font-size: 1.2rem;
  margin: 0;
}

.subscription-count {
  background: #4a90e2;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.9rem;
}

.subscription-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.subscription-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #e0e0e0;
  transition: all 0.3s ease;
}

.subscription-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-header h6 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
  flex: 1;
  margin-right: 12px;
}

.bank-badge {
  background: #f0f0f0;
  color: #666;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 0.8rem;
  white-space: nowrap;
}

.card-body {
  display: grid;
  gap: 12px;
}

.rate-info, .period-info, .date-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rate-info:last-child, .period-info:last-child, .date-info:last-child {
  border-bottom: none;
}

.rate-label, .period-label, .date-label {
  color: #666;
  font-size: 0.9rem;
}

.rate-value {
  color: #4a90e2;
  font-weight: 600;
  font-size: 1.1rem;
}

.period-value, .date-value {
  color: #333;
  font-weight: 500;
}

.no-subscriptions {
  text-align: center;
  padding: 40px 20px;
  background: #f8f9fa;
  border-radius: 12px;
  color: #666;
}

.no-subscriptions i {
  font-size: 2rem;
  color: #4a90e2;
  margin-bottom: 12px;
}

.no-subscriptions p {
  margin: 0;
  font-size: 1rem;
}

@media (max-width: 768px) {
  .subscription-grid {
    grid-template-columns: 1fr;
  }
  
  .subscription-card {
    margin-bottom: 16px;
  }
}
</style> 