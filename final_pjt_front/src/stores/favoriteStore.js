import axios from 'axios';
import { useAlertStore } from './alertStore'; // alertStore 임포트

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

export const addFavoriteChannel = async (channelData) => {
  const alertStore = useAlertStore();
  try {
    const response = await apiClient.post('/favorite-channels/', channelData);
    alertStore.openAlert({ title: '성공', message: '채널이 즐겨찾기에 추가되었습니다.', type: 'success' });
    return response; // API 응답 반환
  } catch (error) {
    alertStore.openAlert({ title: '오류', message: error.response?.data?.detail || '채널 즐겨찾기 추가 실패', type: 'error' });
    throw error; // 에러를 다시 throw하여 호출한 쪽에서 처리
  }
};

export const removeFavoriteChannel = async (favoriteChannelId) => {
  const alertStore = useAlertStore();
  try {
    const response = await apiClient.delete(`/favorite-channels/${favoriteChannelId}/`);
    alertStore.openAlert({ title: '성공', message: '채널이 즐겨찾기에서 삭제되었습니다.', type: 'info' });
    return response;
  } catch (error) {
    alertStore.openAlert({ title: '오류', message: error.response?.data?.detail || '채널 즐겨찾기 해제 실패', type: 'error' });
    throw error;
  }
};

export const isChannelFavorite = (channelId) => {
  return apiClient.get(`/favorite-channels/is_favorite/?channel_id=${channelId}`);
};

// --- 즐겨찾는 영상 API ---
export const getFavoriteVideos = () => {
  return apiClient.get('/favorite-videos/');
};

export const addFavoriteVideo = async (videoData) => {
  const alertStore = useAlertStore();
  try {
    const response = await apiClient.post('/favorite-videos/', videoData);
    alertStore.openAlert({ title: '성공', message: '영상이 즐겨찾기에 추가되었습니다.', type: 'success' });
    return response;
  } catch (error) {
    alertStore.openAlert({ title: '오류', message: error.response?.data?.detail || '영상 즐겨찾기 추가 실패', type: 'error' });
    throw error;
  }
};

export const removeFavoriteVideo = async (favoriteVideoId) => {
  const alertStore = useAlertStore();
  try {
    const response = await apiClient.delete(`/favorite-videos/${favoriteVideoId}/`);
    alertStore.openAlert({ title: '성공', message: '영상이 즐겨찾기에서 삭제되었습니다.', type: 'info' });
    return response;
  } catch (error) {
    alertStore.openAlert({ title: '오류', message: error.response?.data?.detail || '영상 즐겨찾기 해제 실패', type: 'error' });
    throw error;
  }
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