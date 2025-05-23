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

const KAKAO_MAP_API_KEY = ref(null)
const KAKAO_REST_API_KEY = ref(null) // REST API 키 저장용 변수
const map = ref(null)
const markers = ref([])
const allPlaces = ref([]) // 원본 데이터를 저장할 ref
const filteredPlaces = ref([]) // 필터링된 데이터를 저장할 ref
const selectedBank = ref('')
const selectedCity = ref('')
const isLoading = ref(true)
const error = ref(null)
let clusterer = null // 마커 클러스터러 객체를 저장할 변수

// data.json에서 은행 위치 데이터 로드
async function loadBankData() {
  try {
    // public 폴더에 있는 data.json을 직접 참조
    const response = await axios.get('/data.json')
    allPlaces.value = response.data
    filterMarkers() // 데이터 로드 후 필터링 적용
    return response.data
  } catch (err) {
    console.error('은행 데이터를 불러오는 데 실패했습니다:', err)
    error.value = '은행 데이터를 불러오는 데 실패했습니다. 나중에 다시 시도해주세요.'
    return [] // 오류 발생 시 빈 배열 반환
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
async function initMap(placesData) {
  if (!window.kakao || !window.kakao.maps || !placesData) {
    console.error('카카오맵 SDK 또는 장소 데이터가 준비되지 않았습니다.')
    isLoading.value = false
    if (!error.value) { // 기존 에러 메시지가 없다면 설정
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

  // 기본 중심 위치 (예: 서울 시청) 및 확대 레벨 설정
  const defaultCenter = new window.kakao.maps.LatLng(37.566826, 126.9786567)
  const options = {
    center: defaultCenter,
    level: 7 // 확대 레벨
  }

  map.value = new window.kakao.maps.Map(mapContainer, options)
  console.log('지도 객체 생성 완료:', map.value)

  // 마커 클러스터러 생성
  if (window.kakao.maps.MarkerClusterer) {
    clusterer = new window.kakao.maps.MarkerClusterer({
        map: map.value, // 마커들을 클러스터로 관리하고 표시할 지도 객체
        averageCenter: true, // 클러스터에 포함된 마커들의 평균 위치를 클러스터 마커 위치로 설정
        minLevel: 8, // 클러스터 할 최소 지도 레벨
        disableClickZoom: false // 클러스터 마커를 클릭했을 때 지도가 확대되지 않도록 설정 (커스텀 오버레이 사용 시 유용)
    })
    console.log('마커 클러스터러 생성 완료')
  } else {
    console.warn('마커 클러스터러 라이브러리를 사용할 수 없습니다.')
  }


  updateMarkers(placesData) // 초기 마커 표시
  isLoading.value = false // 로딩 완료
}

// 마커 및 인포윈도우 업데이트
function updateMarkers(places) {
  if (!map.value || !window.kakao || !window.kakao.maps) return

  // 기존 마커와 클러스터러 내용 제거
  if (clusterer) {
    clusterer.clear()
  } else {
    markers.value.forEach(marker => marker.setMap(null))
  }
  markers.value = []

  if (!places || places.length === 0) {
    console.log('표시할 장소가 없습니다.')
    // 필요하다면 사용자에게 "결과 없음" 메시지를 표시할 수 있습니다.
    return
  }

  const newMarkers = places.map(place => {
    if (!place.LAT || !place.LNG) {
      console.warn('위치 정보가 없는 데이터:', place.지점명)
      return null // 유효하지 않은 데이터는 건너뜀
    }
    const position = new window.kakao.maps.LatLng(parseFloat(place.LAT), parseFloat(place.LNG))
    const marker = new window.kakao.maps.Marker({
      position: position,
      clickable: true // 마커를 클릭할 수 있도록 설정
    })

    // 인포윈도우 생성 (기본적으로 닫힌 상태)
    const infowindow = new window.kakao.maps.InfoWindow({
      content: `<div style="padding:5px;font-size:12px;">${place.지점명}<br>${place.주소}</div>`,
      removable: true // 인포윈도우를 닫을 수 있는 x 버튼 표시
    })

    // 마커 클릭 시 인포윈도우 표시/숨김 토글
    window.kakao.maps.event.addListener(marker, 'click', function() {
      if (infowindow.getMap()) {
        infowindow.close()
      } else {
        infowindow.open(map.value, marker)
      }
    })
    return marker
  }).filter(marker => marker !== null) // null 값(잘못된 데이터) 제거

  markers.value = newMarkers
  if (clusterer) {
    clusterer.addMarkers(newMarkers)
    console.log(`${newMarkers.length}개의 마커가 클러스터러에 추가되었습니다.`)
  } else if (map.value && newMarkers.length > 0) {
    newMarkers.forEach(marker => marker.setMap(map.value))
    console.log(`${newMarkers.length}개의 마커가 지도에 직접 추가되었습니다.`)
  }

  // 필터링된 장소가 있을 경우, 첫 번째 장소로 지도 중심 이동 (선택적)
  if (places.length > 0 && places[0].LAT && places[0].LNG) {
    const firstPlacePosition = new window.kakao.maps.LatLng(parseFloat(places[0].LAT), parseFloat(places[0].LNG))
    map.value.panTo(firstPlacePosition)
  } else if (places.length === 0 && (selectedBank.value || selectedCity.value)) {
    // 필터링 결과가 없음을 사용자에게 알릴 수 있습니다.
    // 예: alert('선택한 조건에 맞는 은행이 없습니다.')
    console.log('선택한 조건에 맞는 장소가 없습니다.')
  }
}


// 필터링된 은행 목록 가져오기 (중복 제거)
const uniqueBanks = computed(() => {
  const banks = allPlaces.value.map(place => place.금융회사명).filter(Boolean) // null이나 undefined 제외
  return [...new Set(banks)].sort()
})

// 필터링된 도시 목록 가져오기 (중복 제거)
const uniqueCities = computed(() => {
  const cities = allPlaces.value.map(place => place.CITY).filter(Boolean)
  return [...new Set(cities)].sort()
})

// 마커 필터링 로직
function filterMarkers() {
  let tempPlaces = [...allPlaces.value]

  if (selectedBank.value) {
    tempPlaces = tempPlaces.filter(place => place.금융회사명 === selectedBank.value)
  }
  if (selectedCity.value) {
    tempPlaces = tempPlaces.filter(place => place.CITY === selectedCity.value)
  }
  filteredPlaces.value = tempPlaces
}

// selectedBank 또는 selectedCity 변경 시 마커 업데이트
watch([selectedBank, selectedCity], filterMarkers)

// filteredPlaces 변경 시 지도 마커 업데이트
watch(filteredPlaces, (newPlaces) => {
  if (map.value) { // 지도가 초기화된 후에만 마커 업데이트
    updateMarkers(newPlaces)
  }
})

// 컴포넌트 마운트 시 실행
onMounted(async () => {
  isLoading.value = true
  error.value = null
  try {
    // 백엔드에서 API 키 가져오기 (URL 수정됨)
    const response = await axios.get('http://127.0.0.1:8000/api/v1/kakaomap/get_kakao_map_api_key/')
    KAKAO_MAP_API_KEY.value = response.data.kakaomap_api_key // JavaScript SDK용 키
    KAKAO_REST_API_KEY.value = response.data.kakaomap_rest_api_key // REST API용 키

    if (!KAKAO_MAP_API_KEY.value) {
      throw new Error('카카오맵 API 키를 가져오지 못했습니다.')
    }
    // 개발자 도구 콘솔에서 두 키가 정상적으로 수신되었는지 확인할 수 있습니다.
    console.log('Kakao JS API Key:', KAKAO_MAP_API_KEY.value)
    console.log('Kakao REST API Key:', KAKAO_REST_API_KEY.value)


    await loadKakaoMapSdk(KAKAO_MAP_API_KEY.value) // 지도 SDK 로드
    const bankData = await loadBankData() // 은행 데이터 로드
    if (bankData.length > 0) {
      await initMap(filteredPlaces.value) // 필터링된 데이터로 지도 초기화
    } else if (!error.value) { // 데이터 로드 실패했고, 아직 에러 메시지 설정 안됐으면
      error.value = '은행 데이터를 불러올 수 없어 지도를 초기화할 수 없습니다.'
    }
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