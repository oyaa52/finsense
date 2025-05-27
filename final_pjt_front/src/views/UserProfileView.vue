<template>
  <div class="user-profile-container" v-if="userProfile">
    <div class="profile-header">
      <div class="profile-info">
        <img :src="userProfile.profile_image || defaultProfileImageUrl" alt="User Profile Image" class="profile-image-large" @click="isOwnProfile && triggerFileInput()" :class="{'editable-image': isOwnProfile}">
        <input type="file" ref="fileInputRef" @change="handleFileChange" accept="image/*" style="display: none;" v-if="isOwnProfile">
        <div class="profile-details">
          <h1>{{ userProfile.username }}</h1>
          <div class="profile-stats">
            <div class="stat-item">
              <span class="stat-count">{{ userProfile.posts ? userProfile.posts.length : 0 }}</span>
              <span class="stat-label">posts</span>
            </div>
            <div class="stat-item stat-clickable" @click="toggleFollowersModal">
              <span class="stat-count">{{ userProfile.followers_count }}</span>
              <span class="stat-label">followers</span>
            </div>
            <div class="stat-item stat-clickable" @click="toggleFollowingsModal">
              <span class="stat-count">{{ userProfile.following_count }}</span>
              <span class="stat-label">following</span>
            </div>
          </div>
          <div class="profile-actions">
            <button 
              v-if="!isOwnProfile && authStore.isAuthenticated"
              @click="toggleFollow"
              :class="{'following-btn': userProfile.is_following, 'follow-btn': !userProfile.is_following}">
              {{ userProfile.is_following ? '언팔로우' : '팔로우' }}
            </button>
            <button v-if="isOwnProfile" @click="toggleProfileEdit" class="edit-profile-toggle-btn">
              {{ showProfileEditForm ? '프로필 관리 닫기' : '프로필 관리 열기' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <FollowListModal v-if="showFollowersModal" :users="followersList" title="팔로워" @close="showFollowersModal = false" />
    <FollowListModal v-if="showFollowingsModal" :users="followingsList" title="팔로잉" @close="showFollowingsModal = false" />

    <div v-if="isOwnProfile && showProfileEditForm" class="profile-management-section" data-aos="fade-up">
      <h2 class="section-title-underline">나의 정보 수정</h2>
      <form @submit.prevent="handleProfileUpdateSubmit" class="profile-form">
        <p v-if="selectedFileNameForEdit" class="selected-file-name">선택된 이미지: {{ selectedFileNameForEdit }}</p>
        
        <div class="form-section">
          <h3 class="sub-section-title">기본 정보</h3>
          <div class="form-grid">
            <div class="form-group">
              <label for="age">나이</label>
              <input type="number" id="age" v-model.number="editableProfileData.age">
            </div>
            <div class="form-group">
              <label for="gender">성별</label>
              <select id="gender" v-model="editableProfileData.gender">
                <option value="">선택안함</option> <option value="male">남성</option> <option value="female">여성</option>
              </select>
            </div>
          </div>
        </div>
        <div class="form-section">
          <h3 class="sub-section-title">직업 및 소득 정보</h3>
           <div class="form-grid">
            <div class="form-group">
              <label for="occupation">직업</label>
              <input type="text" id="occupation" v-model="editableProfileData.occupation">
            </div>
            <div class="form-group">
              <label for="marital_status">결혼 상태</label>
              <select id="marital_status" v-model="editableProfileData.marital_status">
                <option value="">선택안함</option> <option value="single">미혼</option> <option value="married">기혼</option>
              </select>
            </div>
            <div class="form-group full-width">
              <label for="monthly_income">월 소득 (원)</label>
              <input type="number" id="monthly_income" v-model.number="editableProfileData.monthly_income">
            </div>
          </div>
        </div>
        <div class="form-section">
          <h3 class="sub-section-title">투자 정보</h3>
          <div class="form-grid">
            <div class="form-group">
              <label for="amount_available">사용 가능 금액 (원)</label>
              <input type="number" id="amount_available" v-model.number="editableProfileData.amount_available">
            </div>
            <div class="form-group">
              <label for="investment_term">투자기간 (개월)</label>
              <input type="number" id="investment_term" v-model.number="editableProfileData.investment_term">
            </div>
            <div class="form-group full-width">
              <label for="investment_purpose">투자 목적</label>
              <textarea id="investment_purpose" v-model="editableProfileData.investment_purpose" rows="3"></textarea>
            </div>
            <div class="form-group full-width">
              <label for="investment_tendency">투자 성향</label>
              <select id="investment_tendency" v-model="editableProfileData.investment_tendency">
                <option value="">선택안함</option> <option value="stable">안정형</option> <option value="stable_seeking">안정추구형</option> <option value="neutral">위험중립형</option> <option value="active_investment">적극투자형</option> <option value="aggressive">공격투자형</option>
              </select>
            </div>
          </div>
        </div>
        <div v-if="updateSuccessMessage" class="success-message"><p>{{ updateSuccessMessage }}</p></div>
        <div v-if="generalErrorMessage && !updateSuccessMessage" class="error-message"><pre>{{ generalErrorMessage }}</pre></div>
        <button type="submit" class="submit-button" :disabled="isUpdatingProfile">{{ isUpdatingProfile ? '저장 중...' : '프로필 저장' }}</button>
      </form>
    </div>

    <div class="user-posts-section">
      <h2 class="section-title-underline">{{ isOwnProfile ? '내가' : userProfile.username + '님이' }} 작성한 게시글</h2>
      <div v-if="userProfile.posts && userProfile.posts.length > 0" class="posts-grid">
        <div v-for="post in userProfile.posts" :key="post.id" class="post-card-profile">
          <div v-if="post.image" class="post-image-container-profile">
            <img :src="post.image" alt="Post image" class="post-image-profile">
          </div>
          <div class="post-content-profile">
            <p>{{ post.content }}</p>
            <small>{{ formatDate(post.created_at) }}</small>
          </div>
        </div>
      </div>
      <div v-else>
        <p>아직 작성한 게시글이 없습니다.</p>
      </div>
    </div>
  </div>
  <div v-else-if="isLoading" class="loading-spinner-container">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
  <div v-else-if="error" class="error-message-container">
    <p>{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { useCommunityStore } from '@/stores/community'
import defaultProfileImage from '@/assets/default_profile.png'
import FollowListModal from '@/components/FollowListModal.vue'
import AOS from 'aos'
import 'aos/dist/aos.css'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const communityStore = useCommunityStore()

const userProfile = computed(() => communityStore.userProfileData)
const isLoading = ref(true)
const error = ref(null)
const defaultProfileImageUrl = defaultProfileImage

const showFollowersModal = ref(false)
const showFollowingsModal = ref(false)

const followersList = computed(() => communityStore.followers)
const followingsList = computed(() => communityStore.following)

const username = computed(() => route.params.username)
const isOwnProfile = computed(() => authStore.isAuthenticated && authStore.currentUser?.username === username.value)

const showProfileEditForm = ref(false)
const editableProfileData = reactive({
  age: null, gender: '', occupation: '', marital_status: '', monthly_income: null,
  amount_available: null, investment_term: null, investment_purpose: '', investment_tendency: '',
  profile_image_file: null
})
const fileInputRef = ref(null)
const selectedFileNameForEdit = ref('')
const isUpdatingProfile = ref(false)
const updateSuccessMessage = ref('')
const generalErrorMessage = ref('')

const fetchUserProfile = async () => {
  if (!username.value) return
  isLoading.value = true
  error.value = null
  try {
    await communityStore.fetchUserProfileByUsername(username.value)
  } catch (err) {
    console.error('Error fetching user profile:', err)
    error.value = '사용자 프로필을 불러오는 데 실패했습니다.'
    if (err.response && err.response.status === 404) {
      error.value = '해당 사용자를 찾을 수 없습니다.'
    }
  } finally {
    isLoading.value = false
  }
}

const toggleFollow = async () => {
  if (!authStore.isAuthenticated || !userProfile.value) return;
  try {
    await communityStore.toggleFollowUser(
      userProfile.value.id, 
      userProfile.value.follow_id_for_current_user
    );
  } catch (err) {
    console.error('Error toggling follow:', err);
    const storeError = communityStore.error;
    if (storeError) {
      alert(storeError);
    } else if (err.response && err.response.data && Array.isArray(err.response.data) && err.response.data.length > 0) {
      alert(err.response.data.join(', '));
    } else if (err.response && err.response.data && err.response.data.detail) {
      alert(err.response.data.detail);
    } else if (err.message) {
      alert(err.message);
    } else {
      alert('팔로우 상태 변경 중 오류가 발생했습니다.');
    }
  }
};

const formatDate = (dateString) => {
  const options = { year: 'numeric', month: 'long', day: 'numeric' }
  return new Date(dateString).toLocaleDateString(undefined, options)
}

const toggleFollowersModal = async () => {
  if (!userProfile.value) return;
  if (!showFollowersModal.value) {
    try {
      isLoading.value = true;
      await communityStore.fetchUserFollowers(userProfile.value.id);
    } catch (err) {
      console.error('Error fetching followers:', err);
      alert('팔로워 목록을 가져오는 데 실패했습니다.');
    } finally {
      isLoading.value = false;
    }
  }
  showFollowersModal.value = !showFollowersModal.value;
};

const toggleFollowingsModal = async () => {
  if (!userProfile.value) return;
  if (!showFollowingsModal.value) {
    try {
      isLoading.value = true;
      await communityStore.fetchUserFollowing(userProfile.value.id);
    } catch (err) {
      console.error('Error fetching followings:', err);
      alert('팔로잉 목록을 가져오는 데 실패했습니다.');
    } finally {
      isLoading.value = false;
    }
  }
  showFollowingsModal.value = !showFollowingsModal.value;
};

const toggleProfileEdit = () => {
  showProfileEditForm.value = !showProfileEditForm.value
  if (showProfileEditForm.value && userProfile.value && isOwnProfile.value) {
    const storeProfile = authStore.getUserProfile;
    if (storeProfile) {
        Object.keys(editableProfileData).forEach(key => {
            if (key !== 'profile_image_file') {
                 editableProfileData[key] = storeProfile[key] ?? (key === 'age' || key === 'monthly_income' || key === 'amount_available' || key === 'investment_term' ? null : '');
            }
        });
        selectedFileNameForEdit.value = ''
        editableProfileData.profile_image_file = null
    } else {
        authStore.fetchProfile().then(() => {
            const fetchedProfile = authStore.getUserProfile;
            if(fetchedProfile) {
                 Object.keys(editableProfileData).forEach(key => {
                    if (key !== 'profile_image_file') {
                        editableProfileData[key] = fetchedProfile[key] ?? (key === 'age' || key === 'monthly_income' || key === 'amount_available' || key === 'investment_term' ? null : '');
                    }
                });
            }
        });
    }
  }
}

const triggerFileInput = () => { fileInputRef.value?.click() }

const handleFileChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    editableProfileData.profile_image_file = file
    if (userProfile.value) userProfile.value.profile_image = URL.createObjectURL(file) 
    selectedFileNameForEdit.value = file.name
  } else {
    editableProfileData.profile_image_file = null
    selectedFileNameForEdit.value = ''
    if (userProfile.value && authStore.getUserProfile?.profile_image) {
        userProfile.value.profile_image = authStore.getUserProfile.profile_image
    } else if (userProfile.value && userProfile.value.profile?.profile_image_url_from_db) {
        userProfile.value.profile_image = userProfile.value.profile.profile_image_url_from_db;
    } else {
        userProfile.value.profile_image = defaultProfileImageUrl;
    }
  }
}

const handleProfileUpdateSubmit = async () => {
  if (!isOwnProfile.value) return
  isUpdatingProfile.value = true
  updateSuccessMessage.value = ''
  generalErrorMessage.value = ''

  const formData = new FormData()
  for (const key in editableProfileData) {
    if (key === 'profile_image_file' && editableProfileData.profile_image_file instanceof File) {
      formData.append('profile_image', editableProfileData.profile_image_file)
    } else if (key !== 'profile_image_file' && editableProfileData[key] !== null && editableProfileData[key] !== undefined) {
      formData.append(key, editableProfileData[key])
    }
  }

  try {
    await authStore.updateProfile(formData)
    updateSuccessMessage.value = '프로필이 성공적으로 업데이트되었습니다.'
    selectedFileNameForEdit.value = ''
    editableProfileData.profile_image_file = null
    await authStore.fetchProfile()
    await fetchUserProfile()
  } catch (error) {
    console.error("프로필 업데이트 오류:", error.response?.data || error)
    generalErrorMessage.value = error.response?.data?.detail || error.message || '프로필 업데이트 실패'
  } finally {
    isUpdatingProfile.value = false
  }
}

onMounted(() => {
  AOS.init();
  fetchUserProfile()
})
watch(username, fetchUserProfile)

</script>

<style scoped>
.user-profile-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
}

.profile-info {
  display: flex;
  align-items: center;
}

.profile-image-large {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 2rem;
  border: 3px solid #fff;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.profile-details h1 {
  font-size: 2rem;
  font-weight: bold;
  margin-top: 0;
  margin-bottom: 0.5rem;
}

.profile-stats {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1rem;
  align-items: center;
  justify-content: space-around;
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1.2;
}

.stat-count {
  font-size: 1.2rem;
  font-weight: bold;
  color: #333;
}

.stat-label {
  font-size: 0.85rem;
  color: #555;
  text-transform: lowercase;
}

.stat-clickable {
  cursor: pointer;
}

.stat-clickable:hover .stat-count,
.stat-clickable:hover .stat-label {
  color: #007bff;
}

.profile-actions {
  margin-top: 1rem;
}

.edit-profile-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 5px;
  text-decoration: none;
  font-weight: bold;
  transition: background-color 0.2s ease;
}

.edit-profile-btn:hover {
  background-color: #218838;
}

.follow-btn,
.following-btn {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s ease;
}

.follow-btn {
  background-color: #007bff;
  color: white;
}

.follow-btn:hover {
  background-color: #0056b3;
}

.following-btn {
  background-color: #6c757d;
  color: white;
}

.following-btn:hover {
  background-color: #545b62;
}

.user-posts-section h2 {
  font-size: 1.5rem;
  margin-bottom: 1.5rem;
  color: #333;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
  display: inline-block;
}

.posts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.post-card-profile {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.08);
  overflow: hidden;
  transition: transform 0.2s ease-in-out;
}

.post-card-profile:hover {
    transform: translateY(-5px);
}

.post-image-container-profile {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.post-image-profile {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.post-content-profile {
  padding: 1rem;
}

.post-content-profile p {
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: #333;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;  
  overflow: hidden;
  text-overflow: ellipsis;
  height: 54px;
}

.post-content-profile small {
  font-size: 0.8rem;
  color: #777;
}

.loading-spinner-container, .error-message-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
  font-size: 1.2rem;
  color: #555;
}

.profile-management-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 5px rgba(0,0,0,0.07);
}
.section-title-underline {
  font-size: 1.6rem;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #007bff;
  display: inline-block;
}
.sub-section-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
  margin-top: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.3rem;
}

.profile-form .form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1rem;
}
.profile-form .form-group {
  display: flex;
  flex-direction: column;
}
.profile-form .form-group.full-width {
  grid-column: 1 / -1;
}
.profile-form label {
  margin-bottom: 0.5rem;
  font-weight: 500;
  font-size: 0.9rem;
}
.profile-form input[type="text"],
.profile-form input[type="number"],
.profile-form input[type="email"],
.profile-form select,
.profile-form textarea {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 0.95rem;
}
.profile-form textarea {
  min-height: 80px;
  resize: vertical;
}
.profile-form .submit-button {
  padding: 0.75rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s ease;
  margin-top: 1rem;
}
.profile-form .submit-button:disabled {
  background-color: #6c757d;
}
.profile-form .submit-button:hover:not(:disabled) {
  background-color: #0056b3;
}
.selected-file-name {
  font-size: 0.85rem; color: #555; margin-top: 0.5rem;
}
.success-message { color: green; margin-top: 1rem; }
.error-message { color: red; margin-top: 1rem; }

.editable-image {
  cursor: pointer;
  border: 2px dashed #007bff;
}
.edit-profile-toggle-btn {
   padding: 0.5rem 1rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.2s ease;
  margin-left: 0.5rem;
}
.edit-profile-toggle-btn:hover {
  background-color: #0056b3;
}
</style> 