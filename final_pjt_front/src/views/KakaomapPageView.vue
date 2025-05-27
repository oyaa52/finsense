<template>
  <div class="page-layout"> 
    <div class="controls-bar"> 
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

    <div class="content-area"> 
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

    <div v-if="isLoading && !isDataReady" class="loading-indicator page-level"> 
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

// Axios 인스턴스 (Vite 개발 서버 프록시 대상)
const api = axios.create({
  baseURL: 'http://localhost:5173' 
})

// 컴포넌트 상태 관리를 위한 ref 변수들
const KAKAO_MAP_API_KEY = ref(null) // 카카오맵 JavaScript API 키
const KAKAO_REST_API_KEY = ref(null) // 카카오 로컬 API (키워드 검색, 길찾기) REST API 키
const map = ref(null) // 카카오맵 인스턴스
const markers = ref([]) // 현재 지도에 표시된 마커 목록
const allPlaces = ref([]) // API로부터 검색된 모든 장소 목록 (페이지네이션 결과 포함)
const cityInfoList = ref([]) // data.json 에서 로드된 도시 정보 목록 (필터용)
const bankNameList = ref([]) // data.json 에서 로드된 은행 이름 목록 (필터용)
const filteredPlaces = ref([]) // 선택된 필터(은행, 도시)에 따라 필터링된 장소 목록
const selectedBank = ref('') // 사용자가 선택한 은행
const selectedCity = ref('') // 사용자가 선택한 도시
const isLoading = ref(true) // 로딩 상태 (초기 로드, API 호출 등)
const error = ref(null) // 에러 메시지 저장
const directions = ref(null) // (사용되지 않음, 필요시 길찾기 관련 데이터 저장용)
const startPosition = ref(null) // (사용되지 않음, 필요시 출발지 고정용)
const currentInfoWindow = ref(null) // 현재 열려있는 일반 정보 인포윈도우
const currentRoute = ref(null) // 현재 지도에 그려진 길찾기 폴리라인
const currentEndMarker = ref(null) // 길찾기 시 목적지 마커
const currentEndInfoWindow = ref(null) // 길찾기 시 목적지 인포윈도우
const currentRouteInfoWindow = ref(null) // 길찾기 시 경로 정보 인포윈도우

let clusterer = null // (사용되지 않음, 필요시 마커 클러스터러 인스턴스)
let searchDebounceTimer = null // 검색 입력 디바운싱을 위한 타이머 ID

// 특화 지점 마커 이미지 URL
const specialMarkerImageSrc = '/KB_SymbolMark.png'

// 카카오맵 SDK 로드 완료 여부
const isSDKLoaded = ref(false)
// 은행 관련 JSON 데이터 로드 완료 여부
const isDataReady = ref(false)

// 9To6 Bank 정보 (지역별 지점명 배열)
const nineToSixKbBanksByRegion = ref({})
// 점심시간 집중상담 은행 정보 (지역별 지점명 배열)
const lunchFocusKbBanksByRegion = ref({})

// 장소 이름(placeName)을 정규화하여 비교 용이하게 만듦.
// 은행명, 괄호 안 내용, "지점" 단어 등을 제거.
function normalizePlaceName(placeName) {
  if (!placeName) return ''
  let normalized = placeName.replace(/(KB국민은행|신한은행|우리은행|하나은행|NH농협은행|IBK기업은행|은행)/g, '')
  normalized = normalized.replace(/\s*\(.*?\)\s*/g, '') 
  normalized = normalized.replace(/\s*지점\s*$/, '').trim() 
  return normalized.replace(/\s\s+/g, ' ').trim()
}

// 카카오맵 API에서 반환된 주소의 지역명(rawRegionName)을
// 특화 은행 정보 JSON 파일의 지역 키(예: "부산·울산·경남")로 매핑.
function getJsonKeyForRegion(rawRegionName) {
  if (!rawRegionName) return null

  const normalizedRegion = rawRegionName
    .replace('특별시', '')
    .replace('광역시', '')
    .replace('특별자치도', '')
    .replace('특별자치시', '')

  const allJsonKeys = [
    ...Object.keys(nineToSixKbBanksByRegion.value),
    ...Object.keys(lunchFocusKbBanksByRegion.value)
  ]
  const uniqueJsonKeys = [...new Set(allJsonKeys)]

  for (const jsonKey of uniqueJsonKeys) {
    if (jsonKey.includes(normalizedRegion)) {
      return jsonKey
    }
  }
  // 도 단위 특별 매핑 규칙
  if (normalizedRegion === '경기' && uniqueJsonKeys.includes('경기·인천')) return '경기·인천'
  if (normalizedRegion === '인천' && uniqueJsonKeys.includes('경기·인천')) return '경기·인천'
  if (normalizedRegion === '경남' && uniqueJsonKeys.includes('부산·울산·경남')) return '부산·울산·경남'
  if (normalizedRegion === '울산' && uniqueJsonKeys.includes('부산·울산·경남')) return '부산·울산·경남'
  if (normalizedRegion === '경북' && uniqueJsonKeys.includes('대구·경북')) return '대구·경북'
  if (normalizedRegion === '충남' && uniqueJsonKeys.includes('세종·대전·충청')) return '세종·대전·충청'
  if (normalizedRegion === '충북' && uniqueJsonKeys.includes('세종·대전·충청')) return '세종·대전·충청'
  if (normalizedRegion === '전남' && uniqueJsonKeys.includes('광주·전라')) return '광주·전라'
  if (normalizedRegion === '전북' && uniqueJsonKeys.includes('광주·전라')) return '광주·전라'

  if (uniqueJsonKeys.includes(normalizedRegion)) {
      return normalizedRegion
  }
  
  return null // 매칭되는 키가 없을 경우
}

// 카카오맵 SDK를 동적으로 로드.
// 이미 로드된 경우 중복 로드를 방지하고, 로드 상태를 관리.
function loadKakaoMapSdk(apiKey) {
  return new Promise((resolve, reject) => {
    if (window.kakao && window.kakao.maps && window.kakao.maps.LatLng) {
      isSDKLoaded.value = true
      resolve()
      return
    }

    const existingScript = document.querySelector('script[src*="dapi.kakao.com/v2/maps/sdk.js"]')
    if (existingScript) {
      existingScript.remove()
    }

    const script = document.createElement('script')
    script.src = `//dapi.kakao.com/v2/maps/sdk.js?appkey=${apiKey}&libraries=services&autoload=false`

    const timeoutId = setTimeout(() => {
      isLoading.value = false
      reject(new Error('카카오맵 SDK 로드 시간이 초과되었습니다.'))
    }, 15000)

    script.onload = () => {
      clearTimeout(timeoutId)
      try {
        if (window.kakao && window.kakao.maps && window.kakao.maps.load) {
          window.kakao.maps.load(() => {
            try {
              let checkCount = 0
              const maxChecks = 50
              const checkSDK = () => {
                try {
                  if (window.kakao && window.kakao.maps && window.kakao.maps.LatLng) {
                    isSDKLoaded.value = true
                    resolve()
                    return
                  }
                  checkCount++
                  if (checkCount >= maxChecks) {
                    reject(new Error('카카오맵 SDK 초기화 시간이 초과되었습니다. (checkSDK)'))
                    return
                  }
                  setTimeout(checkSDK, 100)
                } catch (sdkCheckError) {
                  reject(new Error('카카오맵 SDK checkSDK 중 오류 발생: ' + sdkCheckError.message))
                }
              }
              checkSDK()
            } catch (loadCallbackError) {
              reject(new Error('카카오맵 SDK 로드 콜백 중 오류 발생: ' + loadCallbackError.message))
            }
          })
        } else {
          reject(new Error('카카오맵 SDK (window.kakao.maps.load)를 사용할 수 없습니다.'))
        }
      } catch (e) {
        reject(new Error('카카오맵 SDK 로드 중 동기적 오류 발생: ' + e.message))
      }
    }

    script.onerror = (err) => {
      clearTimeout(timeoutId)
      error.value = '카카오맵 SDK를 로드하는 데 실패했습니다. API 키 또는 네트워크 연결을 확인하세요.'
      isLoading.value = false
      reject(err)
    }
    document.head.appendChild(script)
  })
}

// 일반 은행/도시 정보(data.json) 및 특화 은행 정보(JSON 파일들)를 로드.
async function loadAllBankData() {
  try {
    const generalResponse = await api.get('/data.json')
    if (generalResponse.data) {
      if (Array.isArray(generalResponse.data.mapInfo)) {
        cityInfoList.value = generalResponse.data.mapInfo
      }
      if (Array.isArray(generalResponse.data.bankInfo)) {
        bankNameList.value = generalResponse.data.bankInfo
      }
    }

    try {
      const nineToSixResponse = await api.get('/9to6_kb_banks.json')
      if (typeof nineToSixResponse.data === 'object' && nineToSixResponse.data !== null) {
        nineToSixKbBanksByRegion.value = nineToSixResponse.data
      } else {
        nineToSixKbBanksByRegion.value = {}
      }
    } catch (err) {
      nineToSixKbBanksByRegion.value = {}
    }

    try {
      const lunchFocusResponse = await api.get('/lunch_focus_kb_banks.json')
      if (typeof lunchFocusResponse.data === 'object' && lunchFocusResponse.data !== null) {
        lunchFocusKbBanksByRegion.value = lunchFocusResponse.data
      } else {
        lunchFocusKbBanksByRegion.value = {}
      }
    } catch (err) {
      lunchFocusKbBanksByRegion.value = {}
    }

    isDataReady.value = true
  } catch (err) {
    error.value = '은행 데이터를 불러오는 데 실패했습니다.'
    cityInfoList.value = []
    bankNameList.value = []
    nineToSixKbBanksByRegion.value = {}
    lunchFocusKbBanksByRegion.value = {}
    allPlaces.value = []
    isDataReady.value = false
    throw err
  }
}

// 카카오맵을 초기화하고, 시작 지점(삼성전기 부산사업장)에 마커와 인포윈도우를 표시.
async function initMap() {
  if (!window.kakao || !window.kakao.maps || !window.kakao.maps.LatLng) {
    throw new Error('지도 초기화에 필요한 카카오맵 SDK가 준비되지 않았습니다.')
  }

  const mapContainer = document.getElementById('map')
  if (!mapContainer) {
    throw new Error('지도를 표시할 HTML 요소를 찾을 수 없습니다. (id=map)')
  }

  try {
    mapContainer.style.visibility = 'visible'
    await nextTick() // DOM 업데이트를 기다림

    const samsungPosition = new window.kakao.maps.LatLng(35.0993, 128.8581) // 삼성전기 부산사업장 좌표
    const options = {
      center: samsungPosition, // 초기 중심 좌표
      level: 3 // 초기 확대 수준
    }

    map.value = new window.kakao.maps.Map(mapContainer, options) // 지도 생성

    // 시작 지점 마커 생성
    const startMarker = new window.kakao.maps.Marker({
      position: samsungPosition,
      map: map.value
    })

    // 시작 지점 인포윈도우 생성
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
    })
    startInfoWindow.open(map.value, startMarker) // 인포윈도우 표시

    // 지도 레이아웃 변경 후 중앙 재조정 (딜레이 후 실행으로 안정성 확보)
    if (map.value) {
        setTimeout(() => {
            if (map.value) {
                map.value.relayout()
                const samsungPositionForRelayout = new window.kakao.maps.LatLng(35.0993, 128.8581)
                map.value.setCenter(samsungPositionForRelayout)
            }
        }, 200)
    }
    isLoading.value = false // 초기 로딩 완료
  } catch (e) {
    throw e // 에러 발생 시 상위로 전파
  }
}

// 선택된 은행(selectedBank)과 도시(selectedCity) 기준으로 장소를 필터링.
// 필터링된 결과(filteredPlaces)로 마커 업데이트를 요청.
function filterMarkers() {
  if (!allPlaces.value || allPlaces.value.length === 0) {
    filteredPlaces.value = []
    updateMarkers([]) // 표시할 장소가 없으면 빈 마커 목록으로 업데이트
    return
  }

  // 도시 이름에서 "특별시", "광역시" 등을 제거하여 검색 키워드 생성
  const getCityKeyword = (cityName) => {
    if (!cityName) return ''
    const cityNameWithoutSuffix = cityName
      .replace('특별시', '')
      .replace('광역시', '')
      .replace('특별자치시', '')
      .replace('도', '')
      .trim()
    return cityNameWithoutSuffix
  }

  const cityKeyword = getCityKeyword(selectedCity.value)

  // 장소 목록 필터링 로직
  filteredPlaces.value = allPlaces.value.filter(place => {
    const bankQuery = selectedBank.value || '' // 선택된 은행 없으면 빈 문자열
    const matchesBank = !bankQuery || (place.place_name && place.place_name.includes(bankQuery))

    let matchesCity = !cityKeyword // 선택된 도시 없으면 모든 도시 매칭
    if (cityKeyword) {
      const addressName = place.address_name || ''
      const roadAddressName = place.road_address_name || ''
      matchesCity = addressName.includes(cityKeyword) || roadAddressName.includes(cityKeyword)
    }
    return matchesBank && matchesCity // 은행과 도시 모두 매칭되는 장소만 반환
  })
  updateMarkers(filteredPlaces.value) // 필터링된 장소로 마커 업데이트
}

// 검색 버튼 클릭 또는 필터 변경 시 호출될 검색 함수를 위한 디바운싱 처리.
// 연속적인 API 호출 방지.
function debounceSearch() {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  searchDebounceTimer = setTimeout(() => {
    searchPlaces()
  }, 500) // 500ms 후 searchPlaces 실행
}

// 은행(selectedBank) 또는 도시(selectedCity) 선택이 변경될 때마다 디바운싱된 검색 실행.
watch([selectedBank, selectedCity], () => {
  debounceSearch()
})

// 카카오 로컬 API를 사용하여 키워드(은행명, 도시명)로 장소를 검색.
// 페이지네이션을 적용하여 최대 MAX_PAGES_TO_FETCH 페이지까지 결과를 가져옴.
async function searchPlaces() {
  if (!selectedBank.value && !selectedCity.value) {
    allPlaces.value = []
    filterMarkers()
    return
  }

  isLoading.value = true
  error.value = null
  allPlaces.value = [] // 새 검색 시 이전 결과 초기화

  let searchQuery = selectedBank.value
  if (selectedCity.value) {
    searchQuery = `${selectedCity.value} ${selectedBank.value}`.trim()
  }

  if (!searchQuery) { // 검색어가 없는 경우 (예: 은행만 선택되고 도시는 "모든 도시"인 경우)
    isLoading.value = false
    filterMarkers() // 현재 상태로 마커 업데이트 (아마도 빈 목록)
    return
  }

  let currentPage = 1
  const MAX_PAGES_TO_FETCH = 5 // 최대 가져올 페이지 수
  let isLastPage = false // API 응답의 마지막 페이지 여부

  try {
    while (currentPage <= MAX_PAGES_TO_FETCH && !isLastPage) {
      const response = await axios.get(
        'https://dapi.kakao.com/v2/local/search/keyword.json',
        {
          params: {
            query: searchQuery,
            size: 15, // 페이지 당 결과 수 (카카오 API 최대 15)
            page: currentPage,
          },
          headers: {
            Authorization: `KakaoAK ${KAKAO_REST_API_KEY.value}`,
          },
        }
      )

      if (response.data && response.data.documents) {
        if (response.data.documents.length > 0) {
            allPlaces.value = allPlaces.value.concat(response.data.documents) // 결과 누적
        }
        
        // API 응답 메타 정보에서 마지막 페이지 여부 확인
        if (response.data.meta && typeof response.data.meta.is_end !== 'undefined') {
          isLastPage = response.data.meta.is_end
        } else {
          isLastPage = true // 메타 정보 없으면 안전하게 중단
        }
      } else {
        isLastPage = true // 데이터 없으면 중단
      }
      
      if (!isLastPage) {
        currentPage++ // 다음 페이지로
      }
    }
    filterMarkers() // 누적된 전체 결과로 마커 필터링 및 업데이트
  } catch (err) {
    error.value = '장소 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    filterMarkers() // 에러 발생 시 현재까지의 결과로 필터링 (또는 빈 목록)
  } finally {
    isLoading.value = false // 로딩 상태 해제
  }
}

// 지도에 검색된 장소들의 마커를 표시/업데이트.
// 특화 지점(9To6, 점심시간 집중)은 별도 아이콘으로 표시.
async function updateMarkers(places) {
  if (!map.value || !window.kakao || !window.kakao.maps) {
    return // 지도 객체 또는 SDK 준비 안됐으면 실행 중단
  }

  // 기존 마커 모두 제거
  markers.value.forEach(marker => marker.setMap(null))
  markers.value = []

  if (!places || places.length === 0) {
    return // 표시할 장소가 없으면 실행 중단
  }

  // 특화 지점용 마커 이미지 설정
  const markerImageSize = new window.kakao.maps.Size(45, 45)
  const specialMarkerImage = new window.kakao.maps.MarkerImage(specialMarkerImageSrc, markerImageSize)

  const newMarkers = places.map(place => {
    if (!place.y || !place.x) { // 유효한 좌표 없는 경우 건너뜀
      return null
    }

    const position = new window.kakao.maps.LatLng(parseFloat(place.y), parseFloat(place.x))
    
    let isSpecialBank = false // 현재 장소가 특화 지점인지 여부
    // KB국민은행인 경우에만 특화 지점 여부 확인
    if (place.place_name && place.place_name.includes('KB국민')) {
      let rawRegionName = selectedCity.value // 드롭다운에서 선택된 도시 우선 사용
      // "모든 도시" 선택 시, 장소의 주소에서 지역명 추출 시도
      if (!rawRegionName) { 
          if (place.address_name) {
            const addressParts = place.address_name.split(' ')
            if (addressParts.length > 0) rawRegionName = addressParts[0]
          }
      }
      
      const regionKey = getJsonKeyForRegion(rawRegionName) // 주소 지역명을 JSON 키로 변환
      const normalizedPlaceNameForComparison = normalizePlaceName(place.place_name) // API 장소명 정규화

      const nineToSixBranchesInRegion = regionKey ? (nineToSixKbBanksByRegion.value[regionKey] || []) : []
      const lunchFocusBranchesInRegion = regionKey ? (lunchFocusKbBanksByRegion.value[regionKey] || []) : []

      // 9To6 Bank 여부 확인
      const isNineToSix = nineToSixBranchesInRegion.some(branchName => {
        const normalizedJsonBranchName = normalizePlaceName(branchName.trim()) // JSON 지점명 정규화
        return normalizedPlaceNameForComparison.includes(normalizedJsonBranchName)
      })
      // 점심시간 집중 은행 여부 확인
      const isLunchFocus = lunchFocusBranchesInRegion.some(branchName => {
        const normalizedJsonBranchName = normalizePlaceName(branchName.trim()) // JSON 지점명 정규화
        return normalizedPlaceNameForComparison.includes(normalizedJsonBranchName)
      })

      if (isNineToSix || isLunchFocus) {
        isSpecialBank = true
      }
    }

    // 마커 옵션 설정
    const markerOptions = {
      position: position,
      clickable: true
    }

    if (isSpecialBank) {
      markerOptions.image = specialMarkerImage // 특화 지점은 별도 이미지 사용
    }

    const marker = new window.kakao.maps.Marker(markerOptions)

    // 마커 이벤트 리스너 등록
    window.kakao.maps.event.addListener(marker, 'mouseover', () => showInfoWindow(place, marker)) // 정보창 표시
    window.kakao.maps.event.addListener(marker, 'mouseout', closeInfoWindow) // 정보창 닫기
    window.kakao.maps.event.addListener(marker, 'click', () => showRoute(place)) // 길찾기 실행

    return marker
  }).filter(marker => marker !== null) // null인 마커(좌표오류 등) 제외

  markers.value = newMarkers // 새 마커 목록으로 업데이트

  if (newMarkers.length > 0) {
    newMarkers.forEach(marker => marker.setMap(map.value)) // 새 마커들 지도에 추가

    // 모든 새 마커와 시작 지점을 포함하도록 지도 범위 조정
    const bounds = new window.kakao.maps.LatLngBounds()
    const startLatLng = new window.kakao.maps.LatLng(35.0993, 128.8581) // 삼성전기 부산사업장
    bounds.extend(startLatLng)
    newMarkers.forEach(marker => bounds.extend(marker.getPosition()))
    map.value.setBounds(bounds, 100) // bounds와 여백(padding)으로 범위 설정

    await nextTick() // DOM 업데이트 후 실행
    if (map.value) {
        map.value.relayout() // 지도 레이아웃 재조정 (특히 동적 크기 변경 시)
    }
  }
}

// 필터링 드롭다운을 위한 은행 목록 (data.json 기반, 중복 제거 및 정렬)
const uniqueBanks = computed(() => {
  if (!Array.isArray(bankNameList.value)) return []
  return [...new Set(bankNameList.value)].sort()
})

// 필터링 드롭다운을 위한 도시 목록 (data.json 기반, 중복 제거 및 정렬)
const uniqueCities = computed(() => {
  if (!Array.isArray(cityInfoList.value)) return []
  const cities = cityInfoList.value.map(place => place.name).filter(Boolean)
  return [...new Set(cities)].sort()
})

// 현재 선택된 도시(selectedCity)에 해당하는 특화 지점(9To6, 점심시간) 목록.
// 오른쪽 패널에 표시됨.
const displayedSpecialBanks = computed(() => {
  const result = {
    nineToSix: [],
    lunchFocus: []
  }

  if (!selectedCity.value) { // 도시 미선택 시 빈 목록 반환
    return result
  }

  const targetRegionKey = getJsonKeyForRegion(selectedCity.value) // 선택된 도시를 JSON 키로 변환

  if (targetRegionKey) {
    // 9To6 은행 목록 채우기
    if (nineToSixKbBanksByRegion.value[targetRegionKey]) {
      nineToSixKbBanksByRegion.value[targetRegionKey].forEach(name => {
        result.nineToSix.push({ name: name.trim(), region: targetRegionKey })
      })
    }
    // 점심시간 집중 은행 목록 채우기
    if (lunchFocusKbBanksByRegion.value[targetRegionKey]) {
      lunchFocusKbBanksByRegion.value[targetRegionKey].forEach(name => {
        result.lunchFocus.push({ name: name.trim(), region: targetRegionKey })
      })
    }
  }
  
  // 각 목록 이름순 정렬
  result.nineToSix.sort((a, b) => a.name.localeCompare(b.name))
  result.lunchFocus.sort((a, b) => a.name.localeCompare(b.name))
  
  return result
})


// 마커에 마우스오버 시 해당 장소의 인포윈도우를 표시.
// 특화 지점인 경우 운영 정보 추가 표시.
function showInfoWindow(place, marker) {
  if (!window.kakao || !window.kakao.maps) {
    return // SDK 준비 안됐으면 중단
  }

  if (currentInfoWindow.value) {
    currentInfoWindow.value.close() // 기존 정보창 닫기
  }

  let specialInfo = '' // 특화 정보 HTML 문자열
  // KB국민은행인 경우 특화 정보 확인
  if (place.place_name && place.place_name.includes('KB국민')) {
    let rawRegionName = selectedCity.value
    if (!rawRegionName && place.address_name) {
        const addressParts = place.address_name.split(' ')
        if (addressParts.length > 0) rawRegionName = addressParts[0]
    }
    
    const regionKey = getJsonKeyForRegion(rawRegionName)
    const normalizedPlaceNameForInfo = normalizePlaceName(place.place_name)

    const nineToSixBranches = regionKey ? (nineToSixKbBanksByRegion.value[regionKey] || []) : []
    const isNineToSix = nineToSixBranches.some(branchName => {
      const normalizedJsonBranchName = normalizePlaceName(branchName.trim())
      return normalizedPlaceNameForInfo.includes(normalizedJsonBranchName)
    })

    const lunchFocusBranches = regionKey ? (lunchFocusKbBanksByRegion.value[regionKey] || []) : []
    const isLunchFocus = lunchFocusBranches.some(branchName => {
      const normalizedJsonBranchName = normalizePlaceName(branchName.trim())
      return normalizedPlaceNameForInfo.includes(normalizedJsonBranchName)
    })

    if (isNineToSix) {
      specialInfo += `<div style="color:orange; font-weight:bold; margin-top:5px;">운영: 09:00 ~ 18:00 (9To6 Bank)</div>`
    }
    if (isLunchFocus) {
      specialInfo += `<div style="color:green; font-weight:bold; margin-top:5px;">점심시간 집중상담 운영</div>`
    }
  }

  // 인포윈도우 내용 구성
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
  `

  currentInfoWindow.value = new window.kakao.maps.InfoWindow({
    content: infowindowContent,
    removable: true,
    zIndex: 3 
  })

  currentInfoWindow.value.open(map.value, marker) // 인포윈도우 표시
}

// 현재 열려있는 일반 정보 인포윈도우를 닫음.
function closeInfoWindow() {
  if (currentInfoWindow.value) {
    currentInfoWindow.value.close()
    currentInfoWindow.value = null
  }
}

// 마커 클릭 시, 시작 지점(삼성전기 부산)부터 해당 장소까지의 길찾기 정보를 카카오모빌리티 API로 요청하고 지도에 표시.
async function showRoute(place) {
  if (!window.kakao || !window.kakao.maps) {
    return // SDK 준비 안됐으면 중단
  }

  const startPos = new window.kakao.maps.LatLng(35.0993, 128.8581) // 시작 위치 (삼성전기 부산)
  const endPos = new window.kakao.maps.LatLng(place.y, place.x) // 도착 위치 (클릭된 장소)
  
  // 기존 길찾기 관련 그래픽 요소들 제거
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

  closeInfoWindow() // 일반 정보창도 닫기

  try {
    // 도착지 마커 및 간단한 정보창 생성
    currentEndMarker.value = new window.kakao.maps.Marker({
      position: endPos,
      map: map.value
    })
    currentEndInfoWindow.value = new window.kakao.maps.InfoWindow({
      content: `<div style="padding:5px;font-size:12px;">${place.place_name}</div>`,
      removable: true
    })
    currentEndInfoWindow.value.open(map.value, currentEndMarker.value)

    // 카카오모빌리티 길찾기 API 호출
    const response = await axios.get(
      'https://apis-navi.kakaomobility.com/v1/directions',
      {
        params: {
          origin: `${startPos.getLng()},${startPos.getLat()},name=삼성전기 부산사업장`,
          destination: `${endPos.getLng()},${endPos.getLat()},name=${place.place_name}`,
          priority: 'RECOMMEND', // 추천 경로
          car_fuel: 'GASOLINE', // 차량 연료 타입
          car_hipass: false, // 하이패스 유무
          alternatives: false, // 대안 경로 미포함
          road_details: false // 도로 상세정보 미포함
        },
        headers: {
          'Authorization': `KakaoAK ${KAKAO_REST_API_KEY.value}`,
          'Content-Type': 'application/json'
        }
      }
    )

    if (response.data && response.data.routes && response.data.routes.length > 0) {
      const routeData = response.data.routes[0] // 첫 번째 추천 경로 사용
      const path = [] // 경로 좌표 배열
      // API 응답에서 경로 좌표 추출
      if (routeData.sections && routeData.sections[0] && routeData.sections[0].roads) {
        routeData.sections[0].roads.forEach(road => {
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
        // 경로 폴리라인 생성 및 지도에 추가
        currentRoute.value = new window.kakao.maps.Polyline({
          path: path,
          strokeColor: '#007bff', // 선 색상
          strokeWeight: 5, // 선 두께
          strokeOpacity: 0.8, // 선 불투명도
          strokeStyle: 'solid' // 선 스타일
        })
        currentRoute.value.setMap(map.value)

        // 경로를 포함하도록 지도 범위 재조정
        const bounds = new window.kakao.maps.LatLngBounds()
        bounds.extend(startPos)
        bounds.extend(endPos)
        path.forEach(point => bounds.extend(point))
        map.value.setBounds(bounds, 50) // 여백 50px

        // 경로 정보 인포윈도우 생성 및 표시
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
                  예상 거리: ${(routeData.summary.distance / 1000).toFixed(1)}km<br>
                  예상 소요시간: ${Math.ceil(routeData.summary.duration / 60)}분
                </div>
              </div>
            </div>
          `,
          removable: true,
          zIndex: 3
        })
        currentRouteInfoWindow.value.open(map.value, currentEndMarker.value)
      } else {
        error.value = '경로를 그릴 수 없습니다.'
      }
    }
  } catch (err) {
    error.value = '경로 안내를 불러오는데 실패했습니다.'
  }
}

// Vue 컴포넌트가 마운트될 때 실행되는 초기화 로직.
// API 키 로드, 카카오맵 SDK 로드, 은행 데이터 로드, 지도 초기화 순으로 진행.
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null
    isDataReady.value = false

    // Django 서버로부터 API 키 가져오기
    const response = await axios.get('http://127.0.0.1:8000/api/v1/kakaomap/get_kakao_map_api_key/')
    KAKAO_MAP_API_KEY.value = response.data.kakaomap_api_key
    KAKAO_REST_API_KEY.value = response.data.kakaomap_rest_api_key

    // SDK 및 데이터 로드
    await loadKakaoMapSdk(KAKAO_MAP_API_KEY.value)
    await loadAllBankData()
    await nextTick() // DOM 업데이트 보장

    // SDK와 데이터가 모두 준비되면 지도 초기화
    if (isSDKLoaded.value && isDataReady.value) {
      await initMap()
    } else {
      let errorMessage = '지도 초기화 실패:'
      if (!isSDKLoaded.value) errorMessage += ' SDK 로드 안됨.'
      if (!isDataReady.value) errorMessage += ' 데이터 준비 안됨.'
      throw new Error(errorMessage)
    }
  } catch (err) {
    error.value = err.message || '지도를 초기화하는 중 오류가 발생했습니다.'
  } finally {
    isLoading.value = false // 모든 작업 완료 후 로딩 상태 해제
  }
})

// Vue 컴포넌트가 언마운트될 때 실행되는 정리 로직.
// 지도 객체, 마커, SDK 상태 등 정리.
onUnmounted(() => {
  if (map.value) {
    map.value = null // 지도 객체 참조 해제
  }
  markers.value = [] // 마커 배열 초기화
  filteredPlaces.value = [] // 필터링된 장소 목록 초기화
  isSDKLoaded.value = false // SDK 로드 상태 초기화
})

</script>

<style scoped>
.page-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  overflow: hidden; 
}

.controls-bar {
  display: flex;
  gap: 15px;
  padding: 15px;
  background-color: #f8f9fa; 
  border-bottom: 1px solid #dee2e6; 
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  flex-shrink: 0; 
}

.controls-bar select {
  padding: 10px 15px;
  border-radius: 5px;
  border: 1px solid #ced4da; 
  font-size: 1rem;
  cursor: pointer;
  background-color: #ffffff;
  color: #495057; 
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  min-width: 180px; 
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
  padding: 10px 24px; 
  background-color: #007bff; 
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.15s ease-in-out;
}

.controls-bar .search-button:hover {
  background-color: #0056b3; 
}

.content-area {
  display: flex;
  flex-direction: row;
  flex-grow: 1; 
  width: 100%;
  overflow: hidden; 
}

.map-view {
  flex-grow: 1; 
  height: 100%; 
  min-width: 0; 
  border-right: 1px solid #dee2e6; 
}

.special-banks-panel {
  width: 350px; 
  flex-shrink: 0; 
  height: 100%; 
  background: #f9f9f9;
  padding: 20px; 
  border-left: 1px solid #e0e0e0; 
  box-shadow: -2px 0 5px rgba(0,0,0,0.05); 
  overflow-y: auto; 
  font-size: 0.9rem;
}

.special-banks-panel h4 {
  margin-top: 0;
  margin-bottom: 20px; 
  font-size: 1.2rem; 
  color: #333;
  border-bottom: 1px solid #ddd; 
  padding-bottom: 12px; 
}
.special-banks-panel h5 {
  font-size: 1.05rem; 
  color: #444; 
  margin-top: 20px; 
  margin-bottom: 10px; 
  display: flex;
  align-items: center;
}
.special-banks-panel ul {
  list-style: none;
  padding-left: 10px; 
  margin-bottom: 20px; 
}
.special-banks-panel li {
  padding: 8px 0; 
  border-bottom: 1px dashed #e0e0e0; 
  color: #555; 
  font-size: 0.95rem; 
}
.special-banks-panel li:last-child {
  border-bottom: none;
}
.special-banks-panel li span { 
  font-size: 0.8em;
  color: #777;
}
.special-banks-panel p {
  color: #555; 
  font-size: 0.95rem; 
  line-height: 1.6; 
}
.special-icon {
  width: 18px; 
  height: auto;
  margin-right: 10px; 
}

.loading-indicator.page-level,
.error-message.page-level {
  position: fixed; 
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(255, 255, 255, 0.95);
  padding: 25px; 
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  z-index: 1000; 
  text-align: center;
  min-width: 300px; 
}

.loading-indicator.page-level p {
  color: #007bff;
  font-size: 1.15rem; 
  margin: 0;
}

.error-message.page-level {
  background-color: #f8d7da; 
  border: 1px solid #f5c6cb; 
}

.error-message.page-level p {
  color: #721c24; 
  font-size: 1.15rem; 
  margin: 0;
}

.loading-indicator,
.error-message {
}

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