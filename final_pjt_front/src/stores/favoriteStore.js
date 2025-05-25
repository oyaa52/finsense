import axios from 'axios';

// API 기본 URL (환경에 따라 설정 필요)
const API_BASE_URL = 'http://localhost:8000/api/v1/accounts'; // accounts 앱의 기본 URL

// 인증 토큰을 포함한 axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터를 사용하여 모든 요청에 인증 토큰 추가
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken'); // 'authToken'에서 'accessToken'으로 수정
    if (token) {
      config.headers.Authorization = `Token ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// --- 즐겨찾는 채널 API ---
export const getFavoriteChannels = () => {
  return apiClient.get('/favorite-channels/');
};

export const addFavoriteChannel = (channelData) => {
  // channelData 예시: { channel_id: 'UC...', channel_title: '채널 제목' }
  return apiClient.post('/favorite-channels/', channelData);
};

export const removeFavoriteChannel = (favoriteChannelId) => {
  // 여기서 favoriteChannelId는 DB에 저장된 FavoriteChannel 객체의 pk 입니다.
  return apiClient.delete(`/favorite-channels/${favoriteChannelId}/`);
};


export const isChannelFavorite = (channelId) => {
  return apiClient.get(`/favorite-channels/is_favorite/?channel_id=${channelId}`);
};


// --- 즐겨찾는 영상 API ---
export const getFavoriteVideos = () => {
  return apiClient.get('/favorite-videos/');
};

export const addFavoriteVideo = (videoData) => {
  // videoData 예시: { video_id: '...', video_title: '...', thumbnail_url: '...', ... }
  return apiClient.post('/favorite-videos/', videoData);
};

export const removeFavoriteVideo = (favoriteVideoId) => {
  // 여기서 favoriteVideoId는 DB에 저장된 FavoriteVideo 객체의 pk 입니다.
  return apiClient.delete(`/favorite-videos/${favoriteVideoId}/`);
};


export const isVideoFavorite = (videoId) => {
  return apiClient.get(`/favorite-videos/is_favorite/?video_id=${videoId}`);
};

export default {
  getFavoriteChannels,
  addFavoriteChannel,
  removeFavoriteChannel,
  isChannelFavorite,
  getFavoriteVideos,
  addFavoriteVideo,
  removeFavoriteVideo,
  isVideoFavorite,
}; 