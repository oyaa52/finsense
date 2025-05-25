<template>
  <div class="favorite-videos-container" data-aos="fade-up">
    <h2 class="view-title">즐겨찾는 영상 목록</h2>
    <div v-if="loading" class="loading-indicator">
      <div class="spinner"></div>
      <p>영상 목록을 불러오는 중입니다...</p>
    </div>
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
    <div v-else-if="favoriteVideos.length === 0" class="empty-message">
      <p>즐겨찾는 영상이 아직 없습니다.</p>
      <p>영상 상세 페이지나 경제 뉴스 페이지에서 영상을 즐겨찾기에 추가해보세요!</p>
    </div>
    <div v-else class="videos-grid">
      <div v-for="video in favoriteVideos" :key="video.id" class="video-card">
        <img 
          :src="video.thumbnail_url || defaultThumbnail" 
          alt="Video thumbnail"
          class="video-thumbnail"
          @click="goToVideoDetail(video.video_id)"
          @error="handleImageError"
        />
        <div class="video-info">
          <h3 class="video-title" @click="goToVideoDetail(video.video_id)">{{ video.video_title }}</h3>
          <p class="channel-title">{{ video.channel_title }}</p>
          <p class="publish-time">게시일: {{ formatPublishTime(video.publish_time) }}</p>
          <p class="added-date">추가된 날짜: {{ formatAddedDate(video.added_at) }}</p>
        </div>
        <div class="card-actions">
          <button @click="removeFavorite(video.id)" class="action-button remove-button">즐겨찾기 해제</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import favoriteStore from '@/stores/favoriteStore';
import AOS from 'aos';
import 'aos/dist/aos.css';
import defaultThumbnailSrc from '@/assets/default_thumbnail.png'; // 기본 썸네일 이미지

const favoriteVideos = ref([]);
const loading = ref(true);
const error = ref(null);
const router = useRouter();
const defaultThumbnail = defaultThumbnailSrc;

const fetchFavoriteVideos = async () => {
  loading.value = true;
  error.value = null;
  try {
    const response = await favoriteStore.getFavoriteVideos();
    favoriteVideos.value = response.data;
  } catch (err) {
    console.error('즐겨찾는 영상 로딩 중 오류:', err);
    error.value = '즐겨찾는 영상을 불러오는 데 실패했습니다. 잠시 후 다시 시도해주세요.';
  } finally {
    loading.value = false;
  }
};

const removeFavorite = async (favoriteVideoDbId) => {
  if (!confirm('정말로 이 영상을 즐겨찾기에서 삭제하시겠습니까?')) {
    return;
  }
  try {
    await favoriteStore.removeFavoriteVideo(favoriteVideoDbId);
    favoriteVideos.value = favoriteVideos.value.filter(video => video.id !== favoriteVideoDbId);
    alert('영상이 즐겨찾기에서 삭제되었습니다.');
  } catch (err) {
    console.error('즐겨찾는 영상 삭제 중 오류:', err);
    alert('즐겨찾기 삭제 중 오류가 발생했습니다.');
  }
};

const goToVideoDetail = (videoId) => {
  router.push({ name: 'videoDetail', params: { videoId: videoId } });
};

const formatPublishTime = (dateTimeString) => {
  if (!dateTimeString) return '-';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
};

const formatAddedDate = (dateTimeString) => {
  if (!dateTimeString) return '-';
  const date = new Date(dateTimeString);
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' });
};

const handleImageError = (event) => {
  event.target.src = defaultThumbnail; // 이미지 로드 실패 시 기본 썸네일로 대체
};

onMounted(() => {
  AOS.init();
  fetchFavoriteVideos();
});
</script>

<style scoped>
.favorite-videos-container {
  padding: 20px;
  max-width: 1200px;
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

.videos-grid {
  display: grid;
  /* 화면 크기에 따라 1, 2, 3, 4개의 컬럼으로 유동적으로 변경 */
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px; /* 간격 살짝 늘림 */
}

.video-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.video-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.12);
}

.video-thumbnail {
  width: 100%;
  aspect-ratio: 16 / 9; /* 16:9 비율 유지 */
  object-fit: cover;
  cursor: pointer;
  border-bottom: 1px solid #eee;
}

.video-info {
  padding: 15px;
  flex-grow: 1; /* 내용이 적어도 카드 높이를 채우도록 */
}

.video-title {
  font-size: 1.1rem; /* 제목 크기 살짝 줄임 */
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 6px;
  cursor: pointer;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 두 줄 제한 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  min-height: calc(1.1rem * 1.4 * 2); /* 두 줄 높이 확보 */
}
.video-title:hover {
  color: #007bff;
}

.channel-title,
.publish-time,
.added-date {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 4px;
  line-height: 1.3;
}

.card-actions {
  padding: 10px 15px;
  text-align: right;
  background-color: #f9f9f9;
  border-top: 1px solid #eee;
}

.action-button {
  padding: 8px 12px;
  border: none;
  border-radius: 5px;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, opacity 0.2s ease;
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