<template>
  <div class="map-container">
    <h1>은행 및 ATM 찾기</h1>
    <div class="controls">
      <select v-model="selectedBank" @change="filterMarkers">
        <option value="">모든 은행</option>
        <option v-for="bank in uniqueBanks" :key="bank" :value="bank">{{ bank }}</option>
      </select>
      <select v-model="selectedCity" @change="filterMarkers">
        <option value="">모든 도시</option>
        <option v-for="city in uniqueCities" :key="city" :value="city">{{ city }}</option>
      </select>
    </div>
    <div id="map" class="map-view"></div>
    <div v-if="isLoading" class="loading-indicator">
      <p>지도 및 데이터를 불러오는 중입니다...</p>
    </div>
    <div v-if="error" class="error-message">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'

// axios 인스턴스 생성
const api = axios.create({
  baseURL: 'http://localhost:5173'  // Vite 개발 서버 주소
})

const KAKAO_MAP_API_KEY = ref(null)
const KAKAO_REST_API_KEY = ref(null) // REST API 키 저장용 변수
const map = ref(null)
const markers = ref([])
const allPlaces = ref([]) // API 검색 결과를 저장할 ref (지도에 표시될 장소들)
const cityInfoList = ref([]) // data.json의 mapInfo (도시 이름 및 지역 목록) 저장용
const bankNameList = ref([]) // data.json의 bankInfo (은행 이름 목록) 저장용
const filteredPlaces = ref([]) 
const selectedBank = ref('')
const selectedCity = ref('')
const isLoading = ref(true)
const error = ref(null)
let clusterer = null // 마커 클러스터러 객체를 저장할 변수
let searchDebounceTimer = null; // 검색 디바운싱을 위한 타이머 변수

// data.json에서 은행 위치 데이터 로드
async function loadBankData() {
  try {
    console.log('[loadBankData] Starting to load data.json...');
    // public 폴더에 있는 data.json을 직접 참조
    const response = await api.get('/data.json')
    console.log('[loadBankData] Response received:', response);
    console.log('[loadBankData] response.data type:', typeof response.data);
    console.log('[loadBankData] response.data content:', JSON.stringify(response.data, null, 2));

    if (response.data && Array.isArray(response.data.mapInfo)) {
      cityInfoList.value = response.data.mapInfo;
      console.log('[loadBankData] cityInfoList.value after assignment:', cityInfoList.value);
    } else {
      console.warn('[loadBankData] response.data.mapInfo is missing or not an array.');
      cityInfoList.value = [];
    }

    if (response.data && Array.isArray(response.data.bankInfo)) {
      bankNameList.value = response.data.bankInfo;
      console.log('[loadBankData] bankNameList.value after assignment:', bankNameList.value);
    } else {
      console.warn('[loadBankData] response.data.bankInfo is missing or not an array.');
      bankNameList.value = [];
    }
    
    // 현재 data.json은 드롭다운용 데이터만 제공합니다.
    // allPlaces.value = []; // 명시적으로 비워둠 -> API 검색 결과를 담을 것이므로 초기화는 여기서 하지 않음.
    console.log('[loadBankData] allPlaces.value (for map markers) will be populated by API search results.');

    // filterMarkers() // 데이터 로드 후 필터링 적용 -> 초기 로드 시에는 검색 전이므로 호출 불필요
    // 초기에는 아무것도 검색하지 않으므로 빈 지도를 보여주거나, 기본 검색 실행 가능
    // 여기서는 초기에는 빈 지도를 보여주고, 사용자 선택에 따라 검색 실행
    return response.data 
  } catch (err) {
    console.error('은행 데이터를 불러오는 데 실패했습니다:', err)
    console.error('Error stack:', err.stack); // Log the stack trace of the caught error
    cityInfoList.value = [];
    bankNameList.value = [];
    allPlaces.value = [] // 오류 발생 시 allPlaces가 배열인지 확인
    error.value = '드롭다운 및 지도 데이터를 불러오는 데 실패했습니다.'; // 에러 메시지 업데이트
    return null // 오류 발생 시 null 반환
  }
}

// 카카오맵 SDK 동적 로드
function loadKakaoMapSdk(apiKey) {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps) {
      console.log('카카오맵 SDK가 이미 로드되어 있습니다.')
      resolve()
      return
    }
    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services,clusterer&autoload=false`
    script.onload = () => {
      window.kakao.maps.load(() => {
        console.log('카카오맵 SDK 로드 완료')
        resolve()
      })
    }
    script.onerror = (err) => {
      console.error('카카오맵 SDK 로드 실패:', err)
      error.value = '카카오맵 SDK를 로드하는 데 실패했습니다. API 키 또는 네트워크 연결을 확인하세요.'
      reject(err)
    }
    document.head.appendChild(script)
  })
}

// 지도 초기화 및 마커 생성
async function initMap() { 
  if (!window.kakao || !window.kakao.maps) {
    console.error('카카오맵 SDK가 준비되지 않았습니다.')
    isLoading.value = false
    if (!error.value) { 
        error.value = '지도 초기화에 필요한 데이터가 준비되지 않았습니다.'
    }
    return
  }

  const mapContainer = document.getElementById('map')
  if (!mapContainer) {
    console.error('지도 컨테이너 요소를 찾을 수 없습니다.')
    error.value = '지도 컨테이너 요소를 찾을 수 없습니다.'
    isLoading.value = false
    return
  }

  const defaultCenter = new window.kakao.maps.LatLng(37.566826, 126.9786567)
  const options = {
    center: defaultCenter,
    level: 7 
  }

  map.value = new window.kakao.maps.Map(mapContainer, options)
  console.log('지도 객체 생성 완료:', map.value)
  // clusterer = null; // 클러스터러를 사용하지 않으므로 이 변수 자체가 필요 없음
  isLoading.value = false 
}

// 마커 및 인포윈도우 업데이트
function updateMarkers(places) { 
  if (!map.value || !window.kakao || !window.kakao.maps) {
    console.warn('[updateMarkers] Map object or Kakao Maps SDK not available. Skipping.');
    return;
  }

  // 기존 마커들을 지도에서 제거
  markers.value.forEach(marker => marker.setMap(null));
  markers.value = []; 

  if (!places || places.length === 0) {
    console.log('[updateMarkers] No places to display.');
    return;
  }

  console.log(`[updateMarkers] Updating markers for ${places.length} places.`);

  const newMarkers = places.map(place => {
    if (!place.y || !place.x) {
      console.warn('위치 정보(y, x)가 없는 데이터:', place.place_name);
      return null; 
    }
    const position = new window.kakao.maps.LatLng(parseFloat(place.y), parseFloat(place.x))
    const marker = new window.kakao.maps.Marker({
      position: position,
      clickable: true 
    })

    const infowindowContent = 
      `<div style="padding:5px;font-size:12px;">
        <strong>${place.place_name}</strong><br>
        ${place.road_address_name || place.address_name || '주소 정보 없음'}<br>
        ${place.phone ? `전화: ${place.phone}<br>` : ''}
        ${place.category_name ? `카테고리: ${place.category_name}` : ''}
       </div>`;

    const infowindow = new window.kakao.maps.InfoWindow({
      content: infowindowContent,
      removable: true 
    })

    window.kakao.maps.event.addListener(marker, 'click', function() {
      if (infowindow.getMap()) {
        infowindow.close();
      } else {
        infowindow.open(map.value, marker);
      }
    });
    return marker;
  }).filter(marker => marker !== null); 

  markers.value = newMarkers;

  if (map.value && newMarkers.length > 0) {
    console.log('[updateMarkers] Adding markers directly to map.');
    newMarkers.forEach(marker => marker.setMap(map.value));
    console.log(`${newMarkers.length}개의 마커가 지도에 직접 추가되었습니다.`);
  } else if (newMarkers.length === 0) {
    console.log('[updateMarkers] No new markers to add.');
  }

  if (places.length > 0 && places[0].y && places[0].x) {
    const firstPlacePosition = new window.kakao.maps.LatLng(parseFloat(places[0].y), parseFloat(places[0].x))
    map.value.panTo(firstPlacePosition)
  } else if (places.length === 0 && (selectedBank.value || selectedCity.value)) {
    console.log('선택한 조건에 맞는 장소가 없습니다.')
  }
}

// 필터링된 은행 목록 가져오기 (중복 제거)
const uniqueBanks = computed(() => {
  // bankNameList에서 직접 은행 목록을 가져옵니다.
  if (!Array.isArray(bankNameList.value)) return []
  console.log('[uniqueBanks] bankNameList.value:', bankNameList.value);
  return [...new Set(bankNameList.value)].sort()
})

// 필터링된 도시 목록 가져오기 (중복 제거)
const uniqueCities = computed(() => {
  // cityInfoList에서 도시 이름 목록을 가져옵니다.
  if (!Array.isArray(cityInfoList.value)) return []
  const cities = cityInfoList.value.map(place => place.name).filter(Boolean) // 'name' 속성 사용
  console.log('[uniqueCities] Extracted cities:', cities);
  return [...new Set(cities)].sort()
})

// filterMarkers 함수는 더 이상 사용되지 않으므로 삭제 또는 주석 처리
/*
function filterMarkers() {
  console.log('[filterMarkers] This function is no longer used.');
}
*/

// selectedBank 또는 selectedCity 변경 시 장소 검색 (디바운싱 적용됨)
watch([selectedBank, selectedCity], () => {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer);
  }
  searchDebounceTimer = setTimeout(() => {
    searchPlaces(); // 은행 또는 도시 선택 변경 시 장소 검색
  }, 500); // 500ms 디바운스
});

// 카카오맵 장소 검색 API 호출 함수
async function searchPlaces() {
  if (!selectedBank.value && !selectedCity.value) {
    allPlaces.value = [];
    updateMarkers(allPlaces.value); // 선택된 값이 없으면 마커 클리어
    return;
  }

  isLoading.value = true;
  error.value = null;

  let searchQuery = selectedBank.value; // 기본 검색어는 은행 이름
  if (selectedCity.value) {
    searchQuery += ' ' + selectedCity.value; // 도시 이름이 있으면 추가
  }

  console.log(`[searchPlaces] Searching for: ${searchQuery}`);

  try {
    const response = await axios.get(
      'https://dapi.kakao.com/v2/local/search/keyword.json',
      {
        params: {
          query: searchQuery,
          size: 15 // 한 번에 가져올 검색 결과 수 (최대 15)
        },
        headers: {
          Authorization: `KakaoAK ${KAKAO_REST_API_KEY.value}`,
        },
      }
    );

    if (response.data && response.data.documents) {
      console.log('[searchPlaces] API Response:', response.data.documents);
      allPlaces.value = response.data.documents; 
    } else {
      console.warn('[searchPlaces] No documents found or unexpected API response.');
      allPlaces.value = [];
    }
  } catch (err) {
    console.error('[searchPlaces] Error searching places:', err);
    error.value = '장소 검색 중 오류가 발생했습니다.';
    allPlaces.value = [];
  } finally {
    isLoading.value = false;
    updateMarkers(allPlaces.value); // 검색 완료 후 마커 업데이트 (성공/실패/결과없음 모두 포함)
  }
}

// 컴포넌트 마운트 시 실행
onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    // 백엔드에서 API 키 가져오기
    const response = await api.get('http://127.0.0.1:8000/api/v1/kakaomap/get_kakao_map_api_key/')
    KAKAO_MAP_API_KEY.value = response.data.kakaomap_api_key // JavaScript SDK용 키
    KAKAO_REST_API_KEY.value = response.data.kakaomap_rest_api_key // REST API용 키

    if (!KAKAO_MAP_API_KEY.value) {
      throw new Error('카카오맵 API 키를 가져오지 못했습니다.')
    }
    // 개발자 도구 콘솔에서 두 키가 정상적으로 수신되었는지 확인할 수 있습니다.
    console.log('Kakao JS API Key:', KAKAO_MAP_API_KEY.value)
    console.log('Kakao REST API Key:', KAKAO_REST_API_KEY.value)

    await loadKakaoMapSdk(KAKAO_MAP_API_KEY.value) // 지도 SDK 로드
    await loadBankData() // 드롭다운용 데이터 로드 (data.json)
    // bankData는 이제 드롭다운용 데이터만 포함하므로, initMap은 placesData 없이 호출
    await initMap() // 지도만 초기화 (마커 표시는 searchPlaces가 담당)
    
    // 초기 로드 시 기본 검색을 원한다면 여기서 searchPlaces() 호출 가능
    // 예: searchPlaces(); // 기본값(아마도 빈 값)으로 검색 시도 또는 특정 기본값 설정
    // 또는 사용자가 명시적으로 선택할 때까지는 검색 안 함

  } catch (err) {
    console.error('페이지 초기화 중 오류 발생:', err)
    if (!error.value) { // 기존 에러 메시지가 없다면 설정
        error.value = err.message || '페이지를 로드하는 중 문제가 발생했습니다. 다시 시도해주세요.'
    }
  } finally {
    isLoading.value = false
  }
})

</script>

<style scoped>
.map-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 1200px; /* 최대 너비 설정 */
  margin: 20px auto; /* 페이지 중앙 정렬 */
  padding: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* 부드러운 그림자 효과 */
  border-radius: 8px; /* 모서리 둥글게 */
  background-color: #f9f9f9; /* 약간의 배경색 */
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.controls {
  display: flex;
  gap: 15px; /* 컨트롤 사이 간격 */
  margin-bottom: 20px;
  padding: 10px;
  background-color: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.controls select {
  padding: 10px 15px;
  border-radius: 4px;
  border: 1px solid #ccc;
  font-size: 1rem;
  cursor: pointer;
  background-color: #fff;
  transition: border-color 0.3s ease;
}

.controls select:hover {
  border-color: #007bff; /* 호버 시 테두리 색상 변경 */
}

.map-view {
  width: 100%;
  height: 600px; /* 지도 높이 조정 */
  border-radius: 6px; /* 지도 모서리 */
  border: 1px solid #ddd; /* 지도 테두리 */
}

.loading-indicator,
.error-message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
  width: 100%;
  text-align: center;
}

.loading-indicator p {
  color: #007bff;
  font-size: 1.1rem;
}

.error-message {
  background-color: #ffebee; /* 연한 빨간색 배경 */
  border: 1px solid #ef5350; /* 빨간색 테두리 */
}

.error-message p {
  color: #c62828; /* 어두운 빨간색 텍스트 */
  font-size: 1.1rem;
}

/* 인포윈도우 내부 스타일은 전역으로 적용될 수 있으므로, 필요시 더 구체적인 셀렉터 사용 */
/* #map div[style*="padding:5px"] { ... } */
</style>