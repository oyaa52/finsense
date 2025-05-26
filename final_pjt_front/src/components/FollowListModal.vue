<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <div class="modal-content" data-aos="zoom-in-up">
      <div class="modal-header">
        <h3>{{ title }}</h3>
        <button @click="closeModal" class="close-button">&times;</button>
      </div>
      <div class="modal-body">
        <div v-if="users && users.length > 0" class="user-list">
          <div v-for="user in users" :key="user.id" class="user-item">
            <router-link :to="{ name: 'userProfile', params: { username: user.username } }" @click="closeModal">
              <img :src="user.profile_image || defaultProfileImageUrl" alt="Profile Pic" class="user-avatar">
              <span class="username">{{ user.username }}</span>
            </router-link>
            <!-- 현재 로그인한 유저가 아니고, 팔로우/언팔로우 버튼을 여기에 추가할 수도 있음 (선택적) -->
          </div>
        </div>
        <div v-else class="empty-list-message">
          <p>{{ title === '팔로워' ? '아직 팔로워가 없습니다.' : '아직 팔로잉하는 사용자가 없습니다.' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, onMounted } from 'vue'
import defaultProfileImage from '@/assets/default_profile.png'
import AOS from 'aos'

const props = defineProps({
  users: {
    type: Array,
    required: true
  },
  title: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['close'])

const defaultProfileImageUrl = defaultProfileImage

const closeModal = () => {
  emit('close')
}

// 모달이 열릴 때 body 스크롤 방지, 닫힐 때 복원
onMounted(() => {
  document.body.style.overflow = 'hidden';
  AOS.refresh(); // 모달 내 AOS 요소들을 위해
})

// 컴포넌트 unmount 시 body 스크롤 복원 (Modal을 v-if로 제어하므로 unmounted가 호출됨)
import { onUnmounted } from 'vue'
onUnmounted(() => {
  document.body.style.overflow = 'auto';
})

</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1050; /* 부트스트랩 모달 z-index 보다 높거나 비슷하게 */
}

.modal-content {
  background-color: white;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
  width: 90%;
  max-width: 450px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
  margin-bottom: 15px;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 2rem;
  font-weight: bold;
  color: #aaa;
  cursor: pointer;
  padding: 0 0.5rem;
}
.close-button:hover {
  color: #777;
}

.modal-body {
  overflow-y: auto; /* 목록이 길어질 경우 스크롤 */
}

.user-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-item {
  padding: 10px;
  border-radius: 6px;
  transition: background-color 0.2s ease;
}

.user-item a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: inherit;
}

.user-item:hover {
  background-color: #f8f9fa;
}

.user-avatar {
  width: 45px;
  height: 45px;
  border-radius: 50%;
  object-fit: cover;
  margin-right: 12px;
  border: 1px solid #ddd;
}

.username {
  font-size: 1rem;
  font-weight: 500;
  color: #212529;
}

.empty-list-message {
  text-align: center;
  padding: 20px;
  color: #6c757d;
}

.empty-list-message p {
  font-size: 1rem;
}

/* AOS 애니메이션을 위한 기본 스타일 (선택적) */
[data-aos] {
  opacity: 0;
  transition-property: transform, opacity;
}
</style> 