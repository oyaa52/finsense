<template>
  <div class="page-layout"> <!-- 전체 페이지 레이아웃 컨테이너 -->
    <div class="controls-bar"> <!-- 상단 컨트롤 바 -->
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

    <div class="content-area"> <!-- 지도와 특화 지점 패널을 감싸는 영역 -->
      <div id="map" class="map-view"></div>

      <div class="special-banks-panel" v-if="isDataReady">
        <h4>특화 지점 안내</h4>
        <div v-if="!selectedCity">
          <p>도시를 선택하시면 해당 지역의 특화 지점 정보를 확인할 수 있습니다.</p>
        </div>
        <div v-else-if="displayedSpecialBanks.nineToSix.length === 0 && displayedSpecialBanks.lunchFocus.length === 0">
          <p>선택하신 <span style="font-weight: bold;">{{ selectedCity }}</span> 지역에는 특화 은행 정보가 없습니다.</p>
        </div>
        <div v-else>
          <div v-if="displayedSpecialBanks.nineToSix.length > 0">
            <h5><img :src="specialMarkerImageSrc" alt="9to6" class="special-icon"> 9To6 Bank (09:00 ~ 18:00)</h5>
            <ul>
              <li v-for="(bank, index) in displayedSpecialBanks.nineToSix" :key="`9to6-${index}`">
                {{ bank.name }}
              </li>
            </ul>
          </div>
          <div v-if="displayedSpecialBanks.lunchFocus.length > 0">
            <h5><img :src="specialMarkerImageSrc" alt="점심집중" class="special-icon"> 점심시간 집중상담 은행</h5>
            <ul>
              <li v-for="(bank, index) in displayedSpecialBanks.lunchFocus" :key="`lunch-${index}`">
                {{ bank.name }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 로딩 및 에러 메시지는 content-area 내부 또는 외부에 위치시킬 수 있음 (현재는 외부 유지) -->
    <div v-if="isLoading && !isDataReady" class="loading-indicator page-level"> <!-- 초기 전체 로딩 -->
      <p>지도 및 데이터를 불러오는 중입니다...</p>
    </div>
    <div v-if="error" class="error-message page-level">
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

// 특화 지점 마커 이미지 URL (computed 외부에서 접근 가능하도록)
const specialMarkerImageSrc = '/KB_SymbolMark.png';

// 전역 변수로 SDK 로드 상태 관리
const isSDKLoaded = ref(false)
// 데이터 준비 완료 상태 플래그 추가
const isDataReady = ref(false)

// 특화 지점 정보를 저장할 ref (지역별 객체 형태)
const nineToSixKbBanksByRegion = ref({}) // { "서울": ["지점1", ...], ... }
const lunchFocusKbBanksByRegion = ref({}) // { "서울": ["지점1", ...], ... }

// 지점명 정규화 함수
function normalizePlaceName(placeName) {
  if (!placeName) return '';
  // 주요 은행 이름 패턴 및 일반적인 "은행" 단어 제거
  let normalized = placeName.replace(/(KB국민은행|신한은행|우리은행|하나은행|NH농협은행|IBK기업은행|은행)/g, '');
  // 괄호와 그 안의 내용 제거 (예: (점), (출장소) 등)
  normalized = normalized.replace(/\s*\(.*?\)\s*/g, '');
  // "지점"이라는 단어 제거 (양쪽 공백도 고려)
  normalized = normalized.replace(/\s*지점\s*$/, '').trim(); 
  // 지점, 출장소 등의 단어 제거 (선택적, 필요에 따라 추가) - 이전 주석 유지
  // normalized = normalized.replace(/(지점|출장소)$/g, '');
  // 연속 공백을 단일 공백으로 변경하고 양쪽 끝 공백 제거
  return normalized.replace(/\s\s+/g, ' ').trim();
}

// 지역명 -> JSON 키 매핑 함수
function getJsonKeyForRegion(rawRegionName) {
  if (!rawRegionName) return null;

  const normalizedRegion = rawRegionName
    .replace('특별시', '')
    .replace('광역시', '')
    .replace('특별자치도', '') // 제주특별자치도 처리
    .replace('특별자치시', ''); // 세종특별자치시 처리

  // 실제 JSON 파일에 있는 키들을 기준으로 매핑
  // nineToSixKbBanksByRegion와 lunchFocusKbBanksByRegion의 키들을 합쳐서 사용
  const allJsonKeys = [
    ...Object.keys(nineToSixKbBanksByRegion.value),
    ...Object.keys(lunchFocusKbBanksByRegion.value)
  ];
  const uniqueJsonKeys = [...new Set(allJsonKeys)];

  for (const jsonKey of uniqueJsonKeys) {
    if (jsonKey.includes(normalizedRegion)) {
      return jsonKey;
    }
  }
  // 도 단위 매핑 (예: '경기' -> '경기·인천')
  if (normalizedRegion === '경기' && uniqueJsonKeys.includes('경기·인천')) return '경기·인천';
  if (normalizedRegion === '인천' && uniqueJsonKeys.includes('경기·인천')) return '경기·인천';
  if (normalizedRegion === '경남' && uniqueJsonKeys.includes('부산·울산·경남')) return '부산·울산·경남';
  if (normalizedRegion === '울산' && uniqueJsonKeys.includes('부산·울산·경남')) return '부산·울산·경남';
  if (normalizedRegion === '경북' && uniqueJsonKeys.includes('대구·경북')) return '대구·경북';
  if (normalizedRegion === '충남' && uniqueJsonKeys.includes('세종·대전·충청')) return '세종·대전·충청';
  if (normalizedRegion === '충북' && uniqueJsonKeys.includes('세종·대전·충청')) return '세종·대전·충청';
  if (normalizedRegion === '전남' && uniqueJsonKeys.includes('광주·전라')) return '광주·전라';
  if (normalizedRegion === '전북' && uniqueJsonKeys.includes('광주·전라')) return '광주·전라';


  // 정확히 일치하는 키가 있는 경우 (예: '서울', '부산' 등)
  if (uniqueJsonKeys.includes(normalizedRegion)) {
      return normalizedRegion;
  }
  
  console.warn(`[getJsonKeyForRegion] No matching JSON key found for rawRegionName: ${rawRegionName} (Normalized: ${normalizedRegion}). Unique keys:`, uniqueJsonKeys);
  return null; // 매칭되는 키가 없으면 null 반환
}

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
async function loadAllBankData() {
  try {
    // 기존 data.json 로드 (필요하다면 유지, 아니라면 제거 가능)
    const generalResponse = await api.get('/data.json');
    if (generalResponse.data) {
      if (Array.isArray(generalResponse.data.mapInfo)) {
        cityInfoList.value = generalResponse.data.mapInfo;
      }
      if (Array.isArray(generalResponse.data.bankInfo)) {
        bankNameList.value = generalResponse.data.bankInfo;
      }
    }
    console.log('[KakaoMap] 일반 은행/도시 데이터 (data.json) 로드 시도 완료.');

    // 9to6 KB 은행 목록 로드
    try {
      const nineToSixResponse = await api.get('/9to6_kb_banks.json');
      if (typeof nineToSixResponse.data === 'object' && nineToSixResponse.data !== null) {
        nineToSixKbBanksByRegion.value = nineToSixResponse.data;
        console.log('[KakaoMap] 9to6 KB 은행 목록 로드 완료.', Object.keys(nineToSixKbBanksByRegion.value).length, "개 지역");
        console.log('[KakaoMap] Loaded 9to6 KB banks data:', JSON.parse(JSON.stringify(nineToSixKbBanksByRegion.value)));
      } else {
        console.warn('[KakaoMap] 9to6_kb_banks.json 데이터가 객체가 아닙니다.');
        nineToSixKbBanksByRegion.value = {};
      }
    } catch (err) {
      console.error('[KakaoMap] 9to6 KB 은행 목록 로드 실패:', err);
      nineToSixKbBanksByRegion.value = {};
    }

    // 점심시간 집중 상담 KB 은행 목록 로드
    try {
      const lunchFocusResponse = await api.get('/lunch_focus_kb_banks.json');
      if (typeof lunchFocusResponse.data === 'object' && lunchFocusResponse.data !== null) {
        lunchFocusKbBanksByRegion.value = lunchFocusResponse.data;
        console.log('[KakaoMap] 점심시간 집중 KB 은행 목록 로드 완료.', Object.keys(lunchFocusKbBanksByRegion.value).length, "개 지역");
      } else {
        console.warn('[KakaoMap] lunch_focus_kb_banks.json 데이터가 객체가 아닙니다.');
        lunchFocusKbBanksByRegion.value = {};
      }
    } catch (err) {
      console.error('[KakaoMap] 점심시간 집중 KB 은행 목록 로드 실패:', err);
      lunchFocusKbBanksByRegion.value = {}; // 실패 시 빈 객체로 초기화
    }

    isDataReady.value = true;
    console.log('[KakaoMap] 모든 은행 관련 데이터 로드 완료.');

  } catch (err) {
    console.error('[KakaoMap] 은행 데이터 전체 로드 실패:', err);
    error.value = '은행 데이터를 불러오는 데 실패했습니다.';
    // 필요한 값들 초기화
    cityInfoList.value = [];
    bankNameList.value = [];
    nineToSixKbBanksByRegion.value = {};
    lunchFocusKbBanksByRegion.value = {};
    allPlaces.value = [];
    isDataReady.value = false; 
    throw err; // 에러를 다시 던져서 상위 호출자가 처리하도록 함
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

// 카카오맵 장소 검색 API 호출 함수 개선 (페이지네이션 적용)
async function searchPlaces() {
  if (!selectedBank.value && !selectedCity.value) {
    allPlaces.value = [];
    filterMarkers();
    return;
  }

  isLoading.value = true;
  error.value = null;
  allPlaces.value = []; // 결과를 누적하기 전에 항상 초기화

  let searchQuery = selectedBank.value;
  if (selectedCity.value) {
    searchQuery = `${selectedCity.value} ${selectedBank.value}`.trim(); // trim 추가
  }

  if (!searchQuery) { // 은행과 도시 둘 다 선택 안된 경우 (selectedBank만 있는 경우 방지)
    isLoading.value = false;
    filterMarkers();
    return;
  }

  let currentPage = 1;
  const MAX_PAGES_TO_FETCH = 5; // 최대 5페이지까지 조회 (15 * 5 = 75개)
  let isLastPage = false;

  console.log(`[searchPlaces] Starting multi-page search for query: "${searchQuery}"`);

  try {
    while (currentPage <= MAX_PAGES_TO_FETCH && !isLastPage) {
      console.log(`[searchPlaces] Fetching page ${currentPage}...`);
      const response = await axios.get(
        'https://dapi.kakao.com/v2/local/search/keyword.json',
        {
          params: {
            query: searchQuery,
            size: 15, // 페이지 당 결과 수 (최대 15개)
            page: currentPage,
          },
          headers: {
            Authorization: `KakaoAK ${KAKAO_REST_API_KEY.value}`,
          },
        }
      );

      if (response.data && response.data.documents) {
        if (response.data.documents.length > 0) {
            allPlaces.value = allPlaces.value.concat(response.data.documents);
            console.log(`[searchPlaces] Page ${currentPage} loaded ${response.data.documents.length} items. Total items: ${allPlaces.value.length}`);
        } else {
            console.log(`[searchPlaces] Page ${currentPage} had 0 documents.`);
        }
        
        if (response.data.meta && typeof response.data.meta.is_end !== 'undefined') {
          isLastPage = response.data.meta.is_end;
          if (isLastPage) {
            console.log('[searchPlaces] Reached the last page of results.');
          }
        } else {
          // meta 정보가 없거나 is_end 필드가 없는 경우, 안전하게 더 이상 호출하지 않도록 함
          console.warn('[searchPlaces] Meta data or is_end flag not found. Stopping pagination.');
          isLastPage = true; 
        }
      } else {
        console.warn(`[searchPlaces] No data or documents for page ${currentPage}. Stopping pagination.`);
        isLastPage = true; // 데이터가 없으면 더 이상 시도하지 않음
      }
      
      if (!isLastPage) {
        currentPage++;
      }
    }

    console.log('[searchPlaces] Kakao API multi-page search completed. Total results:', allPlaces.value.length);
    // console.log('[searchPlaces] Full results:', JSON.parse(JSON.stringify(allPlaces.value))); // 필요시 전체 결과 로그
    filterMarkers();

  } catch (err) {
    console.error('[searchPlaces] Error during multi-page search:', err);
    // Axios 에러의 경우, 응답 내용 확인
    if (err.response) {
      console.error('[searchPlaces] Axios error response data:', err.response.data);
      console.error('[searchPlaces] Axios error response status:', err.response.status);
      console.error('[searchPlaces] Axios error response headers:', err.response.headers);
    }
    error.value = '장소 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
    // 에러 발생 시 allPlaces를 초기화할 수도 있지만, 이미 로드된 데이터는 유지할 수도 있음.
    // allPlaces.value = []; 
    filterMarkers(); // 현재까지 로드된 데이터로 필터링 시도 (또는 빈 배열로)
  } finally {
    isLoading.value = false;
    console.log('[searchPlaces] Search process finished.');
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

  const markerImageSize = new window.kakao.maps.Size(45, 45);
  const specialMarkerImage = new window.kakao.maps.MarkerImage(specialMarkerImageSrc, markerImageSize);
  console.log('[updateMarkers] specialMarkerImage object created:', specialMarkerImage);

  const newMarkers = places.map(place => {
    if (!place.y || !place.x) {
      console.warn('[updateMarkers] Invalid coordinates for place:', place.place_name)
      return null
    }

    const position = new window.kakao.maps.LatLng(parseFloat(place.y), parseFloat(place.x));
    
    // 이 장소가 특화 지점인지 확인 (KB국민은행만 대상)
    let isSpecialBank = false;
    if (place.place_name && place.place_name.includes('KB국민')) {
      // 현재 검색된 place의 주소에서 지역명 키워드를 추출해야 함
      let rawRegionName = selectedCity.value; // 드롭다운에서 선택한 도시명을 우선 사용
      console.log(`[updateMarkers] Initial rawRegionName (from selectedCity): ${rawRegionName}`);

      if (!rawRegionName) { // 도시 선택이 "모든 도시"인 경우, 장소의 주소에서 지역명 추출 시도
          if (place.address_name) {
            const addressParts = place.address_name.split(' ');
            if (addressParts.length > 0) rawRegionName = addressParts[0];
            console.log(`[updateMarkers] rawRegionName from place.address_name: ${rawRegionName} (Original Address: ${place.address_name})`);
          }
      }
      
      const regionKey = getJsonKeyForRegion(rawRegionName);
      console.log(`[updateMarkers] Mapped regionKey: ${regionKey} (from raw: ${rawRegionName})`);
      
      // 디버깅 로그는 유지 (필요시 삭제)
      // console.log(`[updateMarkers] nineToSixKbBanksByRegion.value:`, nineToSixKbBanksByRegion.value);
      // console.log(`[updateMarkers] lunchFocusKbBanksByRegion.value:`, lunchFocusKbBanksByRegion.value);

      const nineToSixBranchesInRegion = regionKey ? (nineToSixKbBanksByRegion.value[regionKey] || []) : [];
      const lunchFocusBranchesInRegion = regionKey ? (lunchFocusKbBanksByRegion.value[regionKey] || []) : [];

      console.log(`[updateMarkers] For place: ${place.place_name} (Mapped Region: ${regionKey})`);
      console.log(`[updateMarkers] 9to6 branches in ${regionKey}:`, nineToSixBranchesInRegion);
      console.log(`[updateMarkers] Lunch focus branches in ${regionKey}:`, lunchFocusBranchesInRegion);

      const normalizedPlaceNameForComparison = normalizePlaceName(place.place_name);
      console.log(`[updateMarkers] Normalized place name for comparison: '${normalizedPlaceNameForComparison}'`);

      const isNineToSix = nineToSixBranchesInRegion.some(branchName => {
        const normalizedJsonBranchName = normalizePlaceName(branchName.trim());
        // console.log(`[updateMarkers] Comparing 9to6: API Norm: '${normalizedPlaceNameForComparison}' vs JSON Norm: '${normalizedJsonBranchName}' (Original JSON: '${branchName.trim()}')`);
        return normalizedPlaceNameForComparison.includes(normalizedJsonBranchName);
      });
      const isLunchFocus = lunchFocusBranchesInRegion.some(branchName => {
        const normalizedJsonBranchName = normalizePlaceName(branchName.trim());
        if (place.place_name.toLowerCase().includes('해운대') || branchName.toLowerCase().includes('해운대')) {
          console.log(`[DEBUG LunchFocus Compare] API Norm: '${normalizedPlaceNameForComparison}', JSON Norm: '${normalizedJsonBranchName}', JSON Original: '${branchName.trim()}', Includes: ${normalizedPlaceNameForComparison.includes(normalizedJsonBranchName)}`);
        }
        return normalizedPlaceNameForComparison.includes(normalizedJsonBranchName);
      });

      // 해운대지점 디버깅용 로그
      if (place.place_name.includes('해운대')) {
        console.log(`[updateMarkers] DEBUG HEAWUNDAE: Place - ${place.place_name}, isLunchFocus: ${isLunchFocus}, LunchFocusList:`, lunchFocusBranchesInRegion);
      }

      if (isNineToSix || isLunchFocus) {
        isSpecialBank = true;
        console.log(`[updateMarkers] SPECIAL BANK FOUND: ${place.place_name} (9to6: ${isNineToSix}, LunchFocus: ${isLunchFocus})`);
      } else {
        console.log(`[updateMarkers] Not a special bank (or regionKey null): ${place.place_name}`);
      }
    }

    const markerOptions = {
      position: position,
      clickable: true
    };

    if (isSpecialBank) {
      markerOptions.image = specialMarkerImage; // 특화 지점인 경우 노란색 마커
      console.log(`[updateMarkers] Applied specialMarkerImage for: ${place.place_name}`, markerOptions); // 디버깅 로그 추가
    } else {
      console.log(`[updateMarkers] Applied DEFAULT marker for: ${place.place_name}`, markerOptions); // 디버깅 로그 추가
    }

    const marker = new window.kakao.maps.Marker(markerOptions);

    window.kakao.maps.event.addListener(marker, 'mouseover', () => showInfoWindow(place, marker));
    window.kakao.maps.event.addListener(marker, 'mouseout', closeInfoWindow);
    window.kakao.maps.event.addListener(marker, 'click', () => showRoute(place));

    return marker;
  }).filter(marker => marker !== null);

  markers.value = newMarkers;

  if (newMarkers.length > 0) {
    newMarkers.forEach(marker => marker.setMap(map.value));

    const bounds = new window.kakao.maps.LatLngBounds();
    const startLatLng = new window.kakao.maps.LatLng(35.0993, 128.8581); // 삼성전기 부산사업장
    bounds.extend(startLatLng);
    newMarkers.forEach(marker => bounds.extend(marker.getPosition()));
    map.value.setBounds(bounds, 100);

    await nextTick();
    if (map.value) {
        map.value.relayout();
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

// 인포윈도우 표시 함수 수정
function showInfoWindow(place, marker) {
  if (!window.kakao || !window.kakao.maps) {
    console.error('카카오맵 SDK가 준비되지 않았습니다.')
    return
  }

  if (currentInfoWindow.value) {
    currentInfoWindow.value.close()
  }

  let specialInfo = '';
  if (place.place_name && place.place_name.includes('KB국민')) {
    let rawRegionName = selectedCity.value; // 드롭다운 선택 도시
    // allPlaces 검색 결과에서 지역명 추출 로직 (updateMarkers와 유사하게)
    if (!rawRegionName && place.address_name) {
        const addressParts = place.address_name.split(' ');
        if (addressParts.length > 0) rawRegionName = addressParts[0];
    }
    
    const regionKey = getJsonKeyForRegion(rawRegionName);
    console.log(`[showInfoWindow] Mapped regionKey: ${regionKey} (from raw: ${rawRegionName}) for place: ${place.place_name}`);

    const normalizedPlaceNameForInfo = normalizePlaceName(place.place_name);
    console.log(`[showInfoWindow] Normalized place name for info: '${normalizedPlaceNameForInfo}'`);

    const nineToSixBranches = regionKey ? (nineToSixKbBanksByRegion.value[regionKey] || []) : [];
    const isNineToSix = nineToSixBranches.some(branchName => {
      const normalizedJsonBranchName = normalizePlaceName(branchName.trim());
      return normalizedPlaceNameForInfo.includes(normalizedJsonBranchName);
    });

    const lunchFocusBranches = regionKey ? (lunchFocusKbBanksByRegion.value[regionKey] || []) : [];
    const isLunchFocus = lunchFocusBranches.some(branchName => {
      const normalizedJsonBranchName = normalizePlaceName(branchName.trim());
      if (place.place_name.toLowerCase().includes('해운대') || branchName.toLowerCase().includes('해운대')) {
        console.log(`[DEBUG InfoWindow LunchFocus Compare] API Norm: '${normalizedPlaceNameForInfo}', JSON Norm: '${normalizedJsonBranchName}', JSON Original: '${branchName.trim()}', Includes: ${normalizedPlaceNameForInfo.includes(normalizedJsonBranchName)}`);
      }
      return normalizedPlaceNameForInfo.includes(normalizedJsonBranchName);
    });

    if (isNineToSix) {
      specialInfo += `<div style="color:orange; font-weight:bold; margin-top:5px;">운영: 09:00 ~ 18:00 (9To6 Bank)</div>`;
    }
    if (isLunchFocus) {
      specialInfo += `<div style="color:green; font-weight:bold; margin-top:5px;">점심시간 집중상담 운영</div>`;
    }
  }

  const infowindowContent = `
    <div style="padding:15px;font-size:13px;width:auto;min-width:250px;word-break:break-all;">
      <div style="font-size:15px;font-weight:bold;margin-bottom:8px;color:#333;line-height:1.4;">
        ${place.place_name}
      </div>
      <div style="color:#666;margin-bottom:5px;line-height:1.4;">
        ${place.road_address_name || place.address_name}
      </div>
      ${place.phone ? `<div style="color:#666;line-height:1.4;">전화: ${place.phone}</div>` : ''}
      ${specialInfo}
    </div>
  `;

  currentInfoWindow.value = new window.kakao.maps.InfoWindow({
    content: infowindowContent,
    removable: true,
    zIndex: 3 // 다른 인포윈도우/마커보다 위에 표시되도록
  });

  currentInfoWindow.value.open(map.value, marker);
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

// displayedSpecialBanks computed 속성 수정
const displayedSpecialBanks = computed(() => {
  const result = {
    nineToSix: [],
    lunchFocus: []
  };

  // 도시가 선택되지 않았으면 ("모든 도시" 등) 빈 목록 반환
  if (!selectedCity.value) {
    return result;
  }

  const targetRegionKey = getJsonKeyForRegion(selectedCity.value);

  if (targetRegionKey) {
    // 9To6 은행 처리
    if (nineToSixKbBanksByRegion.value[targetRegionKey]) {
      nineToSixKbBanksByRegion.value[targetRegionKey].forEach(name => {
        result.nineToSix.push({ name: name.trim(), region: targetRegionKey });
      });
    }

    // 점심시간 집중 은행 처리
    if (lunchFocusKbBanksByRegion.value[targetRegionKey]) {
      lunchFocusKbBanksByRegion.value[targetRegionKey].forEach(name => {
        result.lunchFocus.push({ name: name.trim(), region: targetRegionKey });
      });
    }
  }
  
  // 이름순 정렬
  result.nineToSix.sort((a, b) => a.name.localeCompare(b.name));
  result.lunchFocus.sort((a, b) => a.name.localeCompare(b.name));
  
  return result;
});

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
    await loadAllBankData();
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
.page-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: hidden; /* 내부 요소가 넘치는 것을 방지 */
}

.controls-bar {
  display: flex;
  gap: 15px;
  padding: 15px;
  background-color: #f8f9fa; /* 배경색 변경 */
  border-bottom: 1px solid #dee2e6; /* 하단 경계선 추가 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-shrink: 0; /* 컨트롤 바 크기 고정 */
}

.controls-bar select {
  padding: 10px 15px;
  border-radius: 5px;
  border: 1px solid #ced4da; /* 테두리 색상 변경 */
  font-size: 1rem;
  cursor: pointer;
  background-color: #ffffff;
  color: #495057; /* 텍스트 색상 변경 */
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  min-width: 180px; /* 최소 너비 증가 */
}

.controls-bar select:hover {
  border-color: #adb5bd;
}

.controls-bar select:focus {
  outline: 0;
  border-color: #80bdff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
}

.controls-bar .search-button {
  padding: 10px 24px; /* 패딩 조정 */
  background-color: #007bff; /* Bootstrap primary color */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.15s ease-in-out;
}

.controls-bar .search-button:hover {
  background-color: #0056b3; /* Darker shade on hover */
}

.content-area {
  display: flex;
  flex-direction: row;
  flex-grow: 1; /* 남은 공간을 모두 차지 */
  width: 100%;
  overflow: hidden; /* 내부 요소가 넘치는 것을 방지 */
}

.map-view {
  flex-grow: 1; /* 지도가 가능한 많은 공간을 차지하도록 */
  height: 100%; /* content-area 높이에 맞춤 */
  min-width: 0; /* 지도가 축소될 수 있도록 */
  border-right: 1px solid #dee2e6; /* 패널과의 구분선 */
}

.special-banks-panel {
  width: 350px; /* 패널 너비 고정 */
  flex-shrink: 0; /* 패널 너비 고정 */
  height: 100%; /* content-area 높이에 맞춤 */
  background: #f9f9f9;
  padding: 20px; /* 패딩 증가 */
  border-left: 1px solid #e0e0e0; /* 왼쪽 경계선 추가 */
  box-shadow: -2px 0 5px rgba(0,0,0,0.05); /* 왼쪽에 그림자 효과 */
  overflow-y: auto; /* 내용이 많을 경우 스크롤 */
  font-size: 0.9rem;
}

.special-banks-panel h4 {
  margin-top: 0;
  margin-bottom: 20px; /* 간격 증가 */
  font-size: 1.2rem; /* 크기 증가 */
  color: #333;
  border-bottom: 1px solid #ddd; /* 경계선 색상 변경 */
  padding-bottom: 12px; /* 간격 증가 */
}
.special-banks-panel h5 {
  font-size: 1.05rem; /* 크기 약간 증가 */
  color: #444; /* 색상 약간 어둡게 */
  margin-top: 20px; /* 간격 증가 */
  margin-bottom: 10px; /* 간격 증가 */
  display: flex;
  align-items: center;
}
.special-banks-panel ul {
  list-style: none;
  padding-left: 10px; /* 패딩 추가 */
  margin-bottom: 20px; /* 간격 증가 */
}
.special-banks-panel li {
  padding: 8px 0; /* 패딩 증가 */
  border-bottom: 1px dashed #e0e0e0; /* 경계선 색상 변경 */
  color: #555; /* 색상 약간 어둡게 */
  font-size: 0.95rem; /* 글자 크기 약간 증가 */
}
.special-banks-panel li:last-child {
  border-bottom: none;
}
.special-banks-panel li span { /* 현재 사용 안함 */
  font-size: 0.8em;
  color: #777;
}
.special-banks-panel p {
  color: #555; /* 색상 약간 어둡게 */
  font-size: 0.95rem; /* 글자 크기 약간 증가 */
  line-height: 1.6; /* 줄 간격 추가 */
}
.special-icon {
  width: 18px; /* 아이콘 크기 약간 증가 */
  height: auto;
  margin-right: 10px; /* 아이콘과 텍스트 간격 증가 */
}

/* 로딩 및 에러 메시지 스타일 조정 */
.loading-indicator.page-level,
.error-message.page-level {
  /* 기존 스타일 중 page-level로 옮기지 않은 것들은 여기서 관리하거나 제거 */
  /* 예를 들어, margin-top 등은 page-level에서 다르게 처리되므로 여기선 불필요 */
}

/* 인포윈도우 스타일은 유지 */
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