<template>
  <div class="map-container">
    <div class="controls">
      <select v-model="selectedBank" @change="filterMarkers">
        <option value="">모든 은행</option>
        <option v-for="bank in uniqueBanks" :key="bank" :value="bank">{{ bank }}</option>
      </select>
      <select v-model="selectedCity" @change="filterMarkers">
        <option value="">모든 도시</option>
        <option v-for="city in uniqueCities" :key="city" :value="city">{{ city }}</option>
      </select>
      <button @click="searchPlaces" class="search-button">검색</button>
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
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import axios from 'axios'

// axios 인스턴스 생성
const api = axios.create({
  baseURL: 'http://localhost:5173'  // Vite 개발 서버 주소
})

// 전역 변수 선언 부분
const KAKAO_MAP_API_KEY = ref(null)
const KAKAO_REST_API_KEY = ref(null)
const map = ref(null)
const markers = ref([])
const allPlaces = ref([])
const cityInfoList = ref([])
const bankNameList = ref([])
const filteredPlaces = ref([])
const selectedBank = ref('')
const selectedCity = ref('')
const isLoading = ref(true)
const error = ref(null)
const directions = ref(null)
const startPosition = ref(null)
const currentInfoWindow = ref(null)
const currentRoute = ref(null)
const currentEndMarker = ref(null)
const currentEndInfoWindow = ref(null)
const currentRouteInfoWindow = ref(null)

let clusterer = null
let searchDebounceTimer = null

// 전역 변수로 SDK 로드 상태 관리
const isSDKLoaded = ref(false)
// 데이터 준비 완료 상태 플래그 추가
const isDataReady = ref(false)

// 카카오맵 SDK 동적 로드 (개선된 버전)
function loadKakaoMapSdk(apiKey) {
  console.log('[KakaoMap] SDK 로드 시도.');
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps && window.kakao.maps.LatLng) {
      console.log('[KakaoMap] SDK 이미 로드됨.');
      isSDKLoaded.value = true;
      resolve();
      return;
    }

    const existingScript = document.querySelector('script[src*="dapi.kakao.com/v2/maps/sdk.js"]');
    if (existingScript) {
      existingScript.remove();
    }

    const script = document.createElement('script');
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`;

    const timeoutId = setTimeout(() => {
      console.error('[KakaoMap] SDK 로드 시간 초과!');
      isLoading.value = false;
      reject(new Error('카카오맵 SDK 로드 시간이 초과되었습니다.'));
    }, 15000);

    script.onload = () => {
      clearTimeout(timeoutId);
      
      try {
        if (window.kakao && window.kakao.maps && window.kakao.maps.load) {
          window.kakao.maps.load(() => {
            try {
              console.log('[KakaoMap] SDK 로드 완료 (kakao.maps.load 콜백).');
              
              let checkCount = 0;
              const maxChecks = 50;
              
              const checkSDK = () => {
                try {
                  if (window.kakao && window.kakao.maps && window.kakao.maps.LatLng) {
                    isSDKLoaded.value = true;
                    resolve();
                    return;
                  }
                  
                  checkCount++;
                  if (checkCount >= maxChecks) {
                    console.error('[KakaoMap] SDK 초기화 시간 초과 (checkSDK 내부)');
                    reject(new Error('카카오맵 SDK 초기화 시간이 초과되었습니다. (checkSDK)'));
                    return;
                  }
                  
                  setTimeout(checkSDK, 100);
                } catch (sdkCheckError) {
                  console.error('[KakaoMap] checkSDK 내부 오류:', sdkCheckError);
                  reject(new Error('카카오맵 SDK checkSDK 중 오류 발생: ' + sdkCheckError.message));
                }
              };
              checkSDK();
            } catch (loadCallbackError) {
              console.error('[KakaoMap] kakao.maps.load 콜백 오류:', loadCallbackError);
              reject(new Error('카카오맵 SDK 로드 콜백 중 오류 발생: ' + loadCallbackError.message));
            }
          });
        } else {
          console.error('[KakaoMap] window.kakao.maps.load 사용 불가.');
          reject(new Error('카카오맵 SDK (window.kakao.maps.load)를 사용할 수 없습니다.'));
        }
      } catch (e) {
        console.error('[KakaoMap] window.kakao.maps.load() 호출 중 동기 오류:', e);
        reject(new Error('카카오맵 SDK 로드 중 동기적 오류 발생: ' + e.message));
      }
    };

    script.onerror = (err) => {
      clearTimeout(timeoutId);
      console.error('[KakaoMap] SDK 로드 실패 (onerror):', err);
      error.value = '카카오맵 SDK를 로드하는 데 실패했습니다. API 키 또는 네트워크 연결을 확인하세요.';
      isLoading.value = false;
      reject(err);
    };

    document.head.appendChild(script);
  });
}

// data.json에서 은행 위치 데이터 로드
async function loadBankData() {
  try {
    const response = await api.get('/data.json');
    
    if (!response.data) {
      throw new Error('data.json 데이터를 불러오지 못했습니다.');
    }

    if (Array.isArray(response.data.mapInfo)) {
      cityInfoList.value = response.data.mapInfo;
    } else {
      console.warn('[KakaoMap] response.data.mapInfo 누락 또는 배열 아님.');
      cityInfoList.value = [];
    }

    if (Array.isArray(response.data.bankInfo)) {
      bankNameList.value = response.data.bankInfo;
    } else {
      console.warn('[KakaoMap] response.data.bankInfo 누락 또는 배열 아님.');
      bankNameList.value = [];
    }
    
    isDataReady.value = true;
    console.log('[KakaoMap] 은행/도시 데이터 로드 완료.');
    return response.data;
  } catch (err) {
    console.error('[KakaoMap] 은행 데이터 로드 실패:', err);
    cityInfoList.value = [];
    bankNameList.value = [];
    allPlaces.value = [];
    error.value = '드롭다운 및 지도 데이터를 불러오는 데 실패했습니다.';
    throw err;
  }
}

// 지도 초기화 및 마커 생성 (개선된 버전)
async function initMap() {
  if (!window.kakao || !window.kakao.maps || !window.kakao.maps.LatLng) {
    console.error('[KakaoMap] SDK 준비 안됨 (initMap).');
    throw new Error('지도 초기화에 필요한 데이터가 준비되지 않았습니다.');
  }

  const mapContainer = document.getElementById('map');
  if (!mapContainer) {
    console.error('[KakaoMap] 지도 컨테이너 없음.');
    throw new Error('지도 컨테이너 요소를 찾을 수 없습니다.');
  }

  try {
    mapContainer.style.visibility = 'visible';
    mapContainer.style.height = '600px';
    await nextTick();

    const samsungPosition = new window.kakao.maps.LatLng(35.0993, 128.8581);
    const options = {
      center: samsungPosition,
      level: 3
    };

    map.value = new window.kakao.maps.Map(mapContainer, options);
    console.log('[KakaoMap] 지도 객체 생성 완료.');

    const startMarker = new window.kakao.maps.Marker({
      position: samsungPosition,
      map: map.value
    });

    const startInfoWindow = new window.kakao.maps.InfoWindow({
      content: `
        <div style="padding:15px;font-size:13px;width:250px;word-break:break-all;">
          <div style="font-size:15px;font-weight:bold;margin-bottom:8px;color:#333;line-height:1.4;">
            삼성전기 부산사업장
          </div>
          <div style="color:#666;margin-bottom:5px;line-height:1.4;">
            부산광역시 강서구 녹산산업중로 333
          </div>
        </div>
      `,
      removable: true,
      zIndex: 3
    });
    startInfoWindow.open(map.value, startMarker);

    if (map.value) {
        setTimeout(() => {
            if (map.value) {
                map.value.relayout();
                const samsungPositionForRelayout = new window.kakao.maps.LatLng(35.0993, 128.8581);
                map.value.setCenter(samsungPositionForRelayout);
            }
        }, 200);
    }
    isLoading.value = false;
  } catch (error) {
    console.error('[KakaoMap] 지도 초기화 중 에러:', error);
    throw error;
  }
}

// 필터링 함수 구현
function filterMarkers() {
  if (!allPlaces.value || allPlaces.value.length === 0) {
    filteredPlaces.value = [];
    updateMarkers([]);
    return;
  }

  const getCityKeyword = (cityName) => {
    if (!cityName) return '';
    
    const cityNameWithoutSuffix = cityName
      .replace('특별시', '')
      .replace('광역시', '')
      .replace('특별자치시', '')
      .replace('도', '')
      .trim();
    
    return cityNameWithoutSuffix;
  };

  const cityKeyword = getCityKeyword(selectedCity.value);

  filteredPlaces.value = allPlaces.value.filter(place => {
    const bankQuery = selectedBank.value || '';
    const matchesBank = !bankQuery || (place.place_name && place.place_name.includes(bankQuery));

    let matchesCity = !cityKeyword;
    if (cityKeyword) {
      const addressName = place.address_name || '';
      const roadAddressName = place.road_address_name || '';
      matchesCity = addressName.includes(cityKeyword) || roadAddressName.includes(cityKeyword);
      
      if (!matchesCity) {
        console.log(`[filterMarkers] City mismatch for place: ${place.place_name}`);
        console.log(`[filterMarkers] Address: ${addressName}`);
        console.log(`[filterMarkers] Road Address: ${roadAddressName}`);
      }
    }

    const matches = matchesBank && matchesCity;
    if (matches) {
      console.log(`[filterMarkers] Match found: ${place.place_name}`);
    }
    
    return matches;
  });
  
  if (filteredPlaces.value.length > 0) {
    console.log('[filterMarkers] First few matches:', filteredPlaces.value.slice(0, 3).map(p => p.place_name));
  }
  
  updateMarkers(filteredPlaces.value);
}

// 검색 디바운싱 함수
function debounceSearch() {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  searchDebounceTimer = setTimeout(() => {
    searchPlaces()
  }, 500)
}

// selectedBank 또는 selectedCity 변경 시 자동 필터링
watch([selectedBank, selectedCity], () => {
  debounceSearch()
})

// 카카오맵 장소 검색 API 호출 함수 개선
async function searchPlaces() {
  if (!selectedBank.value && !selectedCity.value) {
    allPlaces.value = [];
    filterMarkers();
    return;
  }

  isLoading.value = true;
  error.value = null;

  let searchQuery = selectedBank.value;
  if (selectedCity.value) {
    searchQuery = `${selectedCity.value} ${selectedBank.value}`;
  }

  try {
    const response = await axios.get(
      'https://dapi.kakao.com/v2/local/search/keyword.json',
      {
        params: {
          query: searchQuery,
          size: 15,
          page: 1
        },
        headers: {
          Authorization: `KakaoAK ${KAKAO_REST_API_KEY.value}`,
        },
      }
    );

    if (response.data && response.data.documents) {
      allPlaces.value = response.data.documents;
      filterMarkers();
    } else {
      allPlaces.value = [];
      filterMarkers();
    }
  } catch (err) {
    error.value = '장소 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    allPlaces.value = [];
    filterMarkers();
  } finally {
    isLoading.value = false;
  }
}

// 마커 업데이트 함수 개선
async function updateMarkers(places) {
  if (!map.value || !window.kakao || !window.kakao.maps) {
    console.warn('[updateMarkers] Map object or Kakao Maps SDK not available.')
    return
  }

  markers.value.forEach(marker => marker.setMap(null))
  markers.value = []

  if (!places || places.length === 0) {
    console.log('[updateMarkers] No places to display.')
    return
  }

  console.log(`[updateMarkers] Updating markers for ${places.length} places.`)

  const newMarkers = places.map(place => {
    if (!place.y || !place.x) {
      console.warn('[updateMarkers] Invalid coordinates for place:', place.place_name)
      return null
    }

    const position = new window.kakao.maps.LatLng(parseFloat(place.y), parseFloat(place.x))
    const marker = new window.kakao.maps.Marker({
      position: position,
      clickable: true
    })

    window.kakao.maps.event.addListener(marker, 'mouseover', () => showInfoWindow(place, marker))
    window.kakao.maps.event.addListener(marker, 'mouseout', closeInfoWindow)
    window.kakao.maps.event.addListener(marker, 'click', () => showRoute(place))

    return marker
  }).filter(marker => marker !== null)

  markers.value = newMarkers

  if (newMarkers.length > 0) {
    newMarkers.forEach(marker => marker.setMap(map.value))

    const bounds = new window.kakao.maps.LatLngBounds()
    
    const startPosition = new window.kakao.maps.LatLng(35.0993, 128.8581)
    bounds.extend(startPosition)
    
    newMarkers.forEach(marker => bounds.extend(marker.getPosition()))
    
    map.value.setBounds(bounds, 100)

    await nextTick()
    if (map.value) {
        map.value.relayout()
    }
  }
}

// 필터링된 은행 목록 가져오기 (중복 제거)
const uniqueBanks = computed(() => {
  if (!Array.isArray(bankNameList.value)) return []
  return [...new Set(bankNameList.value)].sort()
})

// 필터링된 도시 목록 가져오기 (중복 제거)
const uniqueCities = computed(() => {
  if (!Array.isArray(cityInfoList.value)) return []
  const cities = cityInfoList.value.map(place => place.name).filter(Boolean)
  return [...new Set(cities)].sort()
})

// 인포윈도우 표시 함수
function showInfoWindow(place, marker) {
  if (!window.kakao || !window.kakao.maps) {
    console.error('카카오맵 SDK가 준비되지 않았습니다.')
    return
  }

  if (currentInfoWindow.value) {
    currentInfoWindow.value.close()
  }

  const infowindowContent = `
    <div style="padding:15px;font-size:13px;width:250px;word-break:break-all;">
      <div style="font-size:15px;font-weight:bold;margin-bottom:8px;color:#333;line-height:1.4;">
        ${place.place_name}
      </div>
      <div style="color:#666;margin-bottom:5px;line-height:1.4;">
        ${place.road_address_name || place.address_name}
      </div>
      ${place.phone ? `<div style="color:#666;line-height:1.4;">전화: ${place.phone}</div>` : ''}
    </div>
  `

  currentInfoWindow.value = new window.kakao.maps.InfoWindow({
    content: infowindowContent,
    removable: true,
    zIndex: 3
  })

  currentInfoWindow.value.open(map.value, marker)
}

// 인포윈도우 닫기 함수
function closeInfoWindow() {
  if (currentInfoWindow.value) {
    currentInfoWindow.value.close()
    currentInfoWindow.value = null
  }
}

// 경로 안내 표시 함수 수정
async function showRoute(place) {
  if (!window.kakao || !window.kakao.maps) {
    console.error('카카오맵 SDK가 준비되지 않았습니다.')
    return
  }

  const startPosition = new window.kakao.maps.LatLng(35.0993, 128.8581)
  const endPosition = new window.kakao.maps.LatLng(place.y, place.x)
  
  if (currentRoute.value) {
    currentRoute.value.setMap(null)
    currentRoute.value = null
  }
  if (currentEndMarker.value) {
    currentEndMarker.value.setMap(null)
    currentEndMarker.value = null
  }
  if (currentEndInfoWindow.value) {
    currentEndInfoWindow.value.close()
    currentEndInfoWindow.value = null
  }
  if (currentRouteInfoWindow.value) {
    currentRouteInfoWindow.value.close()
    currentRouteInfoWindow.value = null
  }

  closeInfoWindow()

  try {
    currentEndMarker.value = new window.kakao.maps.Marker({
      position: endPosition,
      map: map.value
    })

    currentEndInfoWindow.value = new window.kakao.maps.InfoWindow({
      content: `<div style="padding:5px;font-size:12px;">${place.place_name}</div>`,
      removable: true
    })

    currentEndInfoWindow.value.open(map.value, currentEndMarker.value)

    const response = await axios.get(
      'https://apis-navi.kakaomobility.com/v1/directions',
      {
        params: {
          origin: `${startPosition.getLng()},${startPosition.getLat()},name=삼성전기 부산사업장`,
          destination: `${endPosition.getLng()},${endPosition.getLat()},name=${place.place_name}`,
          priority: 'RECOMMEND',
          car_fuel: 'GASOLINE',
          car_hipass: false,
          alternatives: false,
          road_details: false
        },
        headers: {
          'Authorization': `KakaoAK ${KAKAO_REST_API_KEY.value}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (response.data && response.data.routes && response.data.routes.length > 0) {
      const route = response.data.routes[0]
      console.log('Route data:', route)

      const path = []
      if (route.sections && route.sections[0] && route.sections[0].roads) {
        route.sections[0].roads.forEach(road => {
          if (road.vertexes && road.vertexes.length > 0) {
            for (let i = 0; i < road.vertexes.length; i += 2) {
              const x = road.vertexes[i]
              const y = road.vertexes[i + 1]
              if (typeof x === 'number' && typeof y === 'number') {
                path.push(new window.kakao.maps.LatLng(y, x))
              }
            }
          }
        })
      }

      if (path.length > 0) {
        currentRoute.value = new window.kakao.maps.Polyline({
          path: path,
          strokeColor: '#007bff',
          strokeWeight: 5,
          strokeOpacity: 0.8,
          strokeStyle: 'solid'
        })

        currentRoute.value.setMap(map.value)

        const bounds = new window.kakao.maps.LatLngBounds()
        bounds.extend(startPosition)
        bounds.extend(endPosition)
        
        path.forEach(point => bounds.extend(point))
        
        map.value.setBounds(bounds, 50)

        currentRouteInfoWindow.value = new window.kakao.maps.InfoWindow({
          content: `
            <div style="padding:15px;font-size:13px;width:250px;word-break:break-all;">
              <div style="font-size:15px;font-weight:bold;margin-bottom:8px;color:#333;line-height:1.4;">
                ${place.place_name}
              </div>
              <div style="color:#666;margin-bottom:5px;line-height:1.4;">
                ${place.road_address_name || place.address_name}
              </div>
              <div style="margin-top:10px;padding-top:10px;border-top:1px solid #eee;">
                <div style="color:#007bff;font-weight:bold;margin-bottom:5px;">경로 안내</div>
                <div style="color:#666;line-height:1.4;">
                  예상 거리: ${(route.summary.distance / 1000).toFixed(1)}km<br>
                  예상 소요시간: ${Math.ceil(route.summary.duration / 60)}분
                </div>
              </div>
            </div>
          `,
          removable: true,
          zIndex: 3
        })

        currentRouteInfoWindow.value.open(map.value, currentEndMarker.value)
      } else {
        console.error('유효한 경로 좌표가 없습니다.')
        error.value = '경로를 그릴 수 없습니다.'
      }
    }
  } catch (err) {
    console.error('경로 안내 실패:', err)
    error.value = '경로 안내를 불러오는데 실패했습니다.'
  }
}

// onMounted 훅 수정
onMounted(async () => {
  try {
    isLoading.value = true;
    error.value = null;
    isDataReady.value = false;

    const response = await axios.get('http://127.0.0.1:8000/api/v1/kakaomap/get_kakao_map_api_key/');
    KAKAO_MAP_API_KEY.value = response.data.kakaomap_api_key;
    KAKAO_REST_API_KEY.value = response.data.kakaomap_rest_api_key;

    await loadKakaoMapSdk(KAKAO_MAP_API_KEY.value);
    await loadBankData();
    await nextTick();

    if (isSDKLoaded.value && isDataReady.value) {
      await initMap();
    } else {
      let errorMessage = '지도 초기화 실패:';
      if (!isSDKLoaded.value) errorMessage += ' SDK 로드 안됨.';
      if (!isDataReady.value) errorMessage += ' 데이터 준비 안됨.';
      throw new Error(errorMessage);
    }
  } catch (err) {
    console.error('[KakaoMap] onMounted 에러:', err);
    error.value = err.message || '지도를 초기화하는 중 오류가 발생했습니다.';
  } finally {
    isLoading.value = false;
  }
});

// 컴포넌트가 언마운트될 때 정리
onUnmounted(() => {
  if (map.value) {
    map.value = null;
  }
  markers.value = [];
  filteredPlaces.value = [];
  isSDKLoaded.value = false;
});

</script>

<style scoped>
.map-container {
  width: 100%;
  height: 100vh;
  position: relative;
}

.search-container {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1;
  width: 90%;
  max-width: 500px;
  background: #ffffff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.search-box {
  display: flex;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  border-color: #4a90e2;
}

.search-button {
  padding: 12px 24px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s ease;
}

.search-button:hover {
  background: #357abd;
}

.bank-list {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 300px;
  max-height: calc(100vh - 40px);
  background: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  z-index: 1;
}

.bank-list-header {
  padding: 15px;
  border-bottom: 1px solid #eee;
  background: #f8f9fa;
  border-radius: 10px 10px 0 0;
}

.bank-list-header h3 {
  margin: 0;
  color: #333;
  font-size: 1.2rem;
}

.bank-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.bank-item:hover {
  background-color: #f8f9fa;
}

.bank-item h4 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 1.1rem;
}

.bank-item p {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.bank-item .distance {
  color: #4a90e2;
  font-weight: 500;
  margin-top: 5px;
}

.bank-info {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffffff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1;
  width: 90%;
  max-width: 500px;
}

.bank-info h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 1.3rem;
}

.bank-info p {
  margin: 5px 0;
  color: #666;
}

.bank-info .close-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background: none;
  border: none;
  color: #666;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 5px;
}

.bank-info .close-button:hover {
  color: #333;
}

/* 스크롤바 스타일링 */
.bank-list::-webkit-scrollbar {
  width: 8px;
}

.bank-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.bank-list::-webkit-scrollbar-thumb {
  background: #4a90e2;
  border-radius: 4px;
}

.bank-list::-webkit-scrollbar-thumb:hover {
  background: #357abd;
}

/* 로딩 상태 스타일 */
.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.9);
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 2;
}

.loading p {
  margin: 0;
  color: #333;
  font-size: 1.1rem;
}

/* 에러 메시지 스타일 */
.error-message {
  position: absolute;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: #fff3f3;
  color: #e74c3c;
  padding: 15px;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 2;
  text-align: center;
  width: 90%;
  max-width: 500px;
}

h1 {
  color: #333;
  margin-bottom: 20px;
  font-size: 2rem;
  font-weight: bold;
}

.controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 800px;
}

.controls select {
  padding: 10px 15px;
  border-radius: 5px;
  border: 1px solid #ddd;
  font-size: 1rem;
  cursor: pointer;
  background-color: #ffffff;
  color: #333;
  transition: all 0.3s ease;
  flex: 1;
}

.controls select:hover {
  border-color: #4a90e2;
}

.controls select:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.25);
}

.map-view {
  width: 100%;
  height: 600px;
  border-radius: 10px;
  border: 1px solid #ddd;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-indicator,
.error-message {
  margin-top: 20px;
  padding: 15px;
  border-radius: 10px;
  width: 100%;
  text-align: center;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-indicator p {
  color: #4a90e2;
  font-size: 1.1rem;
}

.error-message {
  background-color: #fff3f3;
  border: 1px solid #e74c3c;
}

.error-message p {
  color: #e74c3c;
  font-size: 1.1rem;
}

/* 인포윈도우 스타일 커스터마이징 */
:deep(.kakao-map-info-window) {
  background-color: #ffffff !important;
  color: #333 !important;
  border: 1px solid #ddd !important;
  border-radius: 10px !important;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
}

:deep(.kakao-map-info-window-content) {
  color: #333 !important;
}

:deep(.kakao-map-info-window-title) {
  color: #333 !important;
  font-weight: bold !important;
}

:deep(.kakao-map-info-window-address) {
  color: #666 !important;
}

:deep(.kakao-map-info-window-route) {
  color: #4a90e2 !important;
  font-weight: bold !important;
}
</style>