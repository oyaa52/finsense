<template>
  <div class="favorite-channels-container" data-aos="fade-up">
    <h2 class="view-title">즐겨찾는 채널 목록</h2>
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>채널 목록을 불러오는 중입니다...</p>
    </div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="favoriteChannels.length === 0" class="empty-message">
      <p>즐겨찾는 채널이 아직 없습니다.</p>
      <p>영상 상세 페이지에서 채널을 즐겨찾기에 추가해보세요!</p>
    </div>
    <div v-else class="channels-grid">
      <div v-for="channel in favoriteChannels" :key="channel.id" class="channel-card">
        <div class="card-content">
          <h3 class="channel-title">{{ channel.channel_title }}</h3>
          <p class="channel-id">채널 ID: {{ channel.channel_id }}</p>
          <p class="added-date">추가된 날짜: {{ formatAddedDate(channel.added_at) }}</p>
        </div>
        <div class="card-actions">
          <button @click="goToChannel(channel.channel_id)" class="action-button view-button">채널 보기</button>
          <button @click="removeFavorite(channel.id)" class="action-button remove-button">즐겨찾기 해제</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import favoriteStore from '@/stores/favoriteStore';
import { useAlertStore } from '@/stores/alertStore';
import AOS from 'aos';
import 'aos/dist/aos.css';

const favoriteChannels = ref([]);
const loading = ref(true);
const error = ref(null);
const alertStore = useAlertStore();

const fetchFavoriteChannels = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await favoriteStore.getFavoriteChannels();
    favoriteChannels.value = response.data;
  } catch (err) {
    console.error('즐겨찾는 채널 로딩 중 오류:', err);
    error.value = '즐겨찾는 채널을 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.';
    alertStore.openAlert({ 
      title: '오류',
      message: error.value,
      type: 'error' 
    });
  } finally {
    loading.value = false;
  }
};

const removeFavorite = async (favoriteChannelDbId) => {
  alertStore.openAlert({
    title: '확인',
    message: '정말로 이 채널을 즐겨찾기에서 삭제하시겠습니까?',
    type: 'warning',
    showConfirmButton: true,
    onConfirm: async () => {
      try {
        await favoriteStore.removeFavoriteChannel(favoriteChannelDbId);
        favoriteChannels.value = favoriteChannels.value.filter(channel => channel.id !== favoriteChannelDbId);
      } catch (err) {
        console.error('[View] 즐겨찾는 채널 삭제 중 최종 오류:', err);
      }
    },
  });
};

const goToChannel = (channelId) => {
  window.open(`https://www.youtube.com/channel/${channelId}`, '_blank');
};

const formatAddedDate = (dateTimeString) => {
  if (!dateTimeString) return '';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
};

onMounted(() => {
  AOS.init();
  fetchFavoriteChannels();
});
</script>

<style scoped>
.favorite-channels-container {
  padding: 20px;
  max-width: 1000px;
  margin: 20px auto;
}

.view-title {
  font-size: 2rem;
  font-weight: 600;
  color: #333;
  margin-bottom: 25px;
  text-align: center;
}

.loading-indicator, .error-message, .empty-message {
  text-align: center;
  margin-top: 50px;
  font-size: 1.1rem;
  color: #555;
}

.spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #007bff;
  animation: spin 1s ease infinite;
  margin: 0 auto 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.channels-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.channel-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.channel-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

.card-content {
  padding: 15px;
}

.channel-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

.channel-id {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 5px;
  word-break: break-all;
}

.added-date {
  font-size: 0.8rem;
  color: #95a5a6;
}

.card-actions {
  display: flex;
  justify-content: flex-end;
  padding: 10px 15px;
  background-color: #f9f9f9; /* 카드 액션 영역 배경색 */
  border-top: 1px solid #eee;
}

.action-button {
  padding: 8px 12px;
  margin-left: 8px;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, opacity 0.2s ease;
}

.view-button {
  background-color: #3498db;
  color: white;
}
.view-button:hover {
  background-color: #2980b9;
}

.remove-button {
  background-color: #e74c3c;
  color: white;
}
.remove-button:hover {
  background-color: #c0392b;
}

.empty-message p:first-child {
  font-size: 1.2rem;
  font-weight: 500;
  margin-bottom: 10px;
}
</style> 