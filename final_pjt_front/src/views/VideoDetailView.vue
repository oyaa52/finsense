<template>
  <div class="video-detail-container" v-if="videoData">
    <div class="video-player-wrapper">
      <iframe 
        :src="`https://www.youtube.com/embed/${videoId}?autoplay=1`" 
        frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
        class="video-iframe">
      </iframe>
    </div>
    <div class="video-info-wrapper">
      <h2 class="video-title">{{ videoData.title }}</h2>
      <div class="video-meta">
        <p class="channel-title">{{ videoData.channel_title }}</p>
        <p class="publish-time">게시일: {{ formatPublishTime(videoData.publish_time) }}</p>
      </div>
      <p class="video-description">{{ videoData.description }}</p>
      
      <!-- 즐겨찾기 버튼 위치 (추후 구현) -->
      <div class="favorite-buttons">
        <button class="favorite-channel-button" @click="toggleChannelFavorite">
          {{ isChannelFavorited ? '채널 즐겨찾기 해제' : '채널 즐겨찾기' }}
        </button>
        <button class="favorite-video-button" @click="toggleVideoFavorite">
          {{ isVideoFavorited ? '영상 즐겨찾기 해제' : '영상 즐겨찾기' }}
        </button>
      </div>
    </div>
    <button @click="goBack" class="back-button">목록으로 돌아가기</button>
  </div>
  <div v-else-if="loading" class="loading-indicator">
    <div class="spinner"></div>
    <p>영상 정보를 불러오는 중입니다...</p>
  </div>
  <div v-else-if="error" class="error-message">
    <p>{{ error }}</p>
    <button @click="goBack" class="back-button">목록으로 돌아가기</button>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import favoriteStore from '@/stores/favoriteStore'
import { useAlertStore } from '@/stores/alertStore'

const props = defineProps({
  videoId: String
})

const route = useRoute()
const router = useRouter()
const alertStore = useAlertStore()

const videoData = ref(null)
const loading = ref(true)
const error = ref(null)

const isChannelFavorited = ref(false)
const currentFavoriteChannelDBId = ref(null)
const isVideoFavorited = ref(false)
const currentFavoriteVideoDBId = ref(null)

const fetchVideoDetails = async () => {
  if (!props.videoId) {
    error.value = '잘못된 영상 ID입니다.'
    loading.value = false
    return
  }
  loading.value = true
  error.value = null
  try {
    const response = await axios.get(`http://127.0.0.1:8000/api/v1/recommendations/youtube/economic-news/`, {
      params: {
        query: props.videoId,
        max_results: 1
      }
    })

    if (response.data && response.data.videos && response.data.videos.length > 0) {
      const foundVideo = response.data.videos.find(v => v.video_id === props.videoId);
      if (foundVideo) {
        videoData.value = foundVideo;
        checkChannelFavoriteStatus(foundVideo.channel_id);
        checkVideoFavoriteStatus(props.videoId);
      } else {
        videoData.value = {
          title: '제목 로딩 중...',
          channel_title: '채널 로딩 중...',
          publish_time: new Date().toISOString(),
          description: '설명 로딩 중...',
          video_id: props.videoId
        };
      }
    } else {
      error.value = '영상 정보를 불러오는 데 실패했습니다.'
    }
  } catch (err) {
    console.error('영상 정보 로딩 중 에러:', err)
    error.value = '영상 정보 로딩 중 오류가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

const checkChannelFavoriteStatus = async (channelId) => {
  if (!channelId) return;
  try {
    const response = await favoriteStore.isChannelFavorite(channelId);
    isChannelFavorited.value = response.data.is_favorite;
    if (response.data.is_favorite && response.data.id) {
      currentFavoriteChannelDBId.value = response.data.id;
    } else {
      currentFavoriteChannelDBId.value = null;
    }
  } catch (err) {
    console.error('채널 즐겨찾기 상태 확인 중 오류:', err);
    currentFavoriteChannelDBId.value = null;
  }
};

const checkVideoFavoriteStatus = async (videoId) => {
  if (!videoId) return;
  try {
    const response = await favoriteStore.isVideoFavorite(videoId);
    isVideoFavorited.value = response.data.is_favorite;
    if (response.data.is_favorite && response.data.id) {
      currentFavoriteVideoDBId.value = response.data.id;
    } else {
      currentFavoriteVideoDBId.value = null;
    }
  } catch (err) {
    console.error('영상 즐겨찾기 상태 확인 중 오류:', err);
    currentFavoriteVideoDBId.value = null;
  }
};

const formatPublishTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  const date = new Date(dateTimeString)
  return date.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long', day: 'numeric' })
}

const goBack = () => {
  if (router.options.history.state.back) {
    router.back()
  } else {
    router.push({ name: 'economicNews' })
  }
}

const toggleChannelFavorite = async () => {
  if (!videoData.value || !videoData.value.channel_id || !videoData.value.channel_title) {
    alertStore.openAlert({ title: '오류', message: '채널 정보를 가져올 수 없어 즐겨찾기를 할 수 없습니다.', type: 'error' });
    return;
  }

  loading.value = true;
  try {
    if (isChannelFavorited.value) {
      if (currentFavoriteChannelDBId.value) {
        alertStore.openAlert({
          title: '채널 즐겨찾기 해제 확인',
          message: '정말로 이 채널을 즐겨찾기에서 해제하시겠습니까?',
          type: 'warning',
          showConfirmButton: true,
          onConfirm: async () => {
            try {
              await favoriteStore.removeFavoriteChannel(currentFavoriteChannelDBId.value);
              isChannelFavorited.value = false;
              currentFavoriteChannelDBId.value = null;
            } catch (err) {
              console.error('채널 즐겨찾기 해제 중 오류 (onConfirm):', err);
            } finally {
              loading.value = false;
            }
          },
          onCancel: () => {
            loading.value = false;
          }
        });
        return;
      } else {
        alertStore.openAlert({ title: '오류', message: '즐겨찾기 ID를 찾지 못해 해제할 수 없습니다. 페이지를 새로고침 후 다시 시도해주세요.', type: 'error' });
        loading.value = false;
      }
    } else {
      const response = await favoriteStore.addFavoriteChannel({
        channel_id: videoData.value.channel_id,
        channel_title: videoData.value.channel_title,
      });
      isChannelFavorited.value = true;
      currentFavoriteChannelDBId.value = response.data.id;
      loading.value = false;
    }
  } catch (err) {
    console.error('채널 즐겨찾기 처리 중 오류 (메인 try-catch):', err);
    loading.value = false;
  }
};

const toggleVideoFavorite = async () => {
  if (!props.videoId || !videoData.value || !videoData.value.title) {
    alertStore.openAlert({ title: '오류', message: '영상 정보를 가져올 수 없어 즐겨찾기를 할 수 없습니다.', type: 'error' });
    return;
  }
  loading.value = true;
  try {
    if (isVideoFavorited.value) {
      if (currentFavoriteVideoDBId.value) {
        alertStore.openAlert({
          title: '영상 즐겨찾기 해제 확인',
          message: '정말로 이 영상을 즐겨찾기에서 해제하시겠습니까?',
          type: 'warning',
          showConfirmButton: true,
          onConfirm: async () => {
            try {
              await favoriteStore.removeFavoriteVideo(currentFavoriteVideoDBId.value);
              isVideoFavorited.value = false;
              currentFavoriteVideoDBId.value = null;
            } catch (err) {
              console.error('영상 즐겨찾기 해제 중 오류 (onConfirm):', err);
            } finally {
              loading.value = false;
            }
          },
          onCancel: () => {
            loading.value = false;
          }
        });
        return;
      } else {
        alertStore.openAlert({ title: '오류', message: '즐겨찾기 ID를 찾지 못해 해제할 수 없습니다. 페이지를 새로고침 후 다시 시도해주세요.', type: 'error' });
        loading.value = false;
      }
    } else {
      const response = await favoriteStore.addFavoriteVideo({
        video_id: props.videoId,
        video_title: videoData.value.title,
        thumbnail_url: videoData.value.thumbnail_url || '',
        channel_title: videoData.value.channel_title || '',
        publish_time: videoData.value.publish_time || new Date().toISOString(),
      });
      isVideoFavorited.value = true;
      currentFavoriteVideoDBId.value = response.data.id;
      loading.value = false;
    }
  } catch (err) {
    console.error('영상 즐겨찾기 처리 중 오류 (메인 try-catch):', err);
    loading.value = false;
  }
};

onMounted(() => {
  fetchVideoDetails();
});

</script>

<style scoped>
.video-detail-container {
  padding: 20px;
  max-width: 900px;
  margin: 20px auto;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.video-player-wrapper {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 Aspect Ratio */
  height: 0;
  overflow: hidden;
  margin-bottom: 20px;
  border-radius: 8px;
}

.video-iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: none;
}

.video-info-wrapper {
  text-align: left;
  padding: 0 10px;
}

.video-title {
  font-size: 1.8rem;
  font-weight: 600;
  margin-bottom: 10px;
  color: #333;
}

.video-meta {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 15px;
}

.channel-title {
  margin-right: 15px;
  font-weight: 500;
}

.publish-time {
  display: inline-block; /* 채널명과 같은 줄에 배치될 수 있도록 */
}

.video-description {
  font-size: 1rem;
  line-height: 1.6;
  color: #444;
  margin-bottom: 25px;
  white-space: pre-wrap; /* 줄바꿈 및 공백 유지 */
}

.favorite-buttons {
  margin-bottom: 20px;
}

.favorite-buttons button {
  padding: 10px 15px;
  margin-right: 10px;
  border: none;
  border-radius: 6px;
  background-color: #4a90e2;
  color: white;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s ease;
}

.favorite-buttons button:hover {
  background-color: #357abd;
}

.back-button {
  display: inline-block;
  padding: 10px 20px;
  background-color: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  text-decoration: none;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 10px;
}

.back-button:hover {
  background-color: #5a6268;
}

.loading-indicator, .error-message {
  text-align: center;
  padding: 40px;
  margin-top: 30px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #f3f3f3; /* Light grey */
  border-top: 5px solid #4a90e2; /* Blue */
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style> 