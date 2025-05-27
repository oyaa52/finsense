<template>
  <div class="ai-recommendation">
    <!-- 프로필이 없는 경우 -->
    <div v-if="!hasProfile" class="chat-interface">
      <div class="chat-container">
        <div class="chat-messages" ref="chatContainer">
          <div v-for="(message, index) in messages" :key="index" 
               :class="['message', message.type]">
            <div class="message-content">
              {{ message.content }}
            </div>
          </div>
        </div>
      </div>

      <!-- 프로필 입력 폼 -->
      <div class="profile-form">
        <h3>투자 성향 분석</h3>
        <div class="form-group">
          <label>투자 목적</label>
          <select v-model="profileData.investment_purpose">
            <option value="house">집 마련</option>
            <option value="car">차량 구매</option>
            <option value="wedding">결혼 자금</option>
            <option value="education">교육 자금</option>
            <option value="retirement">노후 자금</option>
            <option value="travel">여행 자금</option>
            <option value="business">사업 자금</option>
            <option value="other">기타</option>
          </select>
        </div>
        <div class="form-group">
          <label>투자 성향</label>
          <select v-model="profileData.investment_tendency">
            <option value="stable">안정 추구형</option>
            <option value="stable_seeking">안정 추구 중립형</option>
            <option value="neutral">중립형</option>
            <option value="aggressive">공격 투자형</option>
          </select>
        </div>
        <div class="form-group">
          <label>투자 기간 (개월)</label>
          <select v-model="profileData.investment_term">
            <option value="6">6개월</option>
            <option value="12">12개월</option>
            <option value="24">24개월</option>
            <option value="36">36개월</option>
          </select>
        </div>
        <div class="form-group">
          <label>투자 가능 금액 (원)</label>
          <input type="number" v-model="profileData.amount_available" min="0">
        </div>
        <button @click="submitProfile" class="submit-btn">분석 시작</button>
      </div>
    </div>

    <!-- 프로필이 있는 경우 -->
    <div v-else class="simulation-interface">
      <!-- 로딩 애니메이션: 초기 단계(GPT 호출 전까지)에만 전체 차단형으로 표시 -->
      <div v-if="isLoading && currentStep < 3" class="loading-container">
        <div class="loading-steps">
          <div class="step" :class="{ active: currentStep >= 1 }">
            <i class="fas fa-chart-line"></i>
            <span>프로필 분석</span>
          </div>
          <div class="step" :class="{ active: currentStep >= 2 }">
            <i class="fas fa-brain"></i>
            <span>GPT 추천 생성 중</span>
          </div>
          <!-- 수익률 계산 및 이미지 생성 단계는 아래 결과 섹션과 함께 표시될 수 있음 -->
        </div>
      </div>

      <!-- 시뮬레이션 결과: 프로필이 있으면 항상 이 섹션의 골격은 그림 -->
      <div class="simulation-results" v-if="hasProfile">
        
        <h3>미래 시나리오</h3>

        <div class="main-scenario-content-wrapper">
          <!-- GPT 응답 텍스트 + gpt_load.png 배경 -->
          <div class="scenario-text-container" v-if="simulationData.future_scenario">
            <div class="scenario-text-background"></div>
            <div class="scenario-text-content">
              <p>{{ simulationData.future_scenario.description }}</p>
            </div>
          </div>

          <!-- DALL-E 생성 이미지 및 관련 정보 (기존 .future-scenario div 활용) -->
          <div class="future-scenario" v-if="simulationData.future_scenario?.visualization">
            <div class="scenario-visualization">
              <div class="visualization-info">
                <span class="object-type">{{ simulationData.future_scenario.visualization.object }}</span>
                <span class="style-info">{{ simulationData.future_scenario.visualization.style }}</span>
                <span class="emotion-info">{{ simulationData.future_scenario.visualization.emotion }}</span>
              </div>
              <div class="cute-3d-container">
                <img v-if="simulationData.future_scenario.visualization.image_url"
                     :src="simulationData.future_scenario.visualization.image_url" 
                     :alt="simulationData.future_scenario.visualization.object"
                     class="cute-3d-image"
                     @error="handleImageError">
                <div v-else-if="isLoading && currentStep === 4 && !simulationData.future_scenario.visualization.image_url" class="loading-image">
                  <i class="fas fa-palette fa-spin"></i> 
                  {{ simulationData.future_scenario.visualization.object ? simulationData.future_scenario.visualization.object + ' 관련' : '' }} 미래를 그려보는 중...
                </div>
                <div v-else-if="!simulationData.future_scenario.visualization.image_url" class="loading-image">
                  {{ simulationData.future_scenario.visualization.object ? simulationData.future_scenario.visualization.object + ' 관련' : '' }} 시각화 준비 중입니다.
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 나머지 시뮬레이션 상세 정보 및 추천 상품 목록 -->
        <!-- 이 부분들은 관련 데이터(simulationData.expectedReturn 등)가 있을 때만 표시 -->
        <div v-if="simulationData.expectedReturn || (recommendations && recommendations.length > 0)">
          <div class="simulation-details" v-if="simulationData.expectedReturn || simulationData.initialInvestmentAmount">
            <div class="detail-item">
              <i class="fas fa-coins"></i>
              <div class="detail-content">
                <h4>예상 수익금</h4>
                <p>
                  <span v-if="simulationData.initialInvestmentAmount">초기 투자금 {{ formatCurrency(simulationData.initialInvestmentAmount) }}원 기준 / </span>
                  {{ formatCurrency(simulationData.expectedReturn) }}원
                </p>
              </div>
            </div>
            <div class="detail-item">
              <i class="fas fa-percentage"></i>
              <div class="detail-content">
                <h4>예상 수익률</h4>
                <p>{{ simulationData.returnRate }}%</p>
              </div>
            </div>
          </div>

          <div class="recommendations" v-if="recommendations && recommendations.length > 0">
            <h3>맞춤 투자 추천</h3>
            <div class="portfolio-summary" v-if="simulationData.risk_analysis || simulationData.diversification">
              <div class="summary-item" v-if="simulationData.risk_analysis">
                <h4>포트폴리오 분석</h4>
                <p>{{ simulationData.risk_analysis }}</p>
              </div>
              <div class="summary-item" v-if="simulationData.diversification">
                <h4>자산 분산 전략</h4>
                <p>{{ simulationData.diversification }}</p>
              </div>
            </div>
            <div class="recommendation-grid">
              <div v-for="(product, index) in recommendations" 
                   :key="index" 
                   class="recommendation-card"
                   :class="[product.product_type, `risk-${product.risk_level}`]">
                <div class="card-header">
                  <h4>{{ product.product_name }}</h4>
                  <div class="card-badges">
                    <span class="score">{{ product.score }}점</span>
                    <span class="risk-badge" :class="product.risk_level">
                      {{ product.risk_level === 'low' ? '안전' : 
                         product.risk_level === 'medium' ? '중간' : '고위험' }}
                    </span>
                  </div>
                </div>
                <div class="card-body">
                  <div class="product-info">
                    <div class="info-item">
                      <i class="fas fa-percentage"></i>
                      <span>예상 수익률: {{ product.max_rate }}%</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-calendar-alt"></i>
                      <span>투자 기간: {{ product.term }}</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-coins"></i>
                      <span>최소 투자금: {{ formatCurrency(product.min_amount) }}원</span>
                    </div>
                    <div class="info-item">
                      <i class="fas fa-chart-line"></i>
                      <span>예상 수익금: {{ formatCurrency(product.expected_return) }}원</span>
                    </div>
                  </div>
                  <div class="recommendation-reason">
                    <h5>추천 이유</h5>
                    <p>{{ product.reason }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 모든 데이터가 아직 준비되지 않았지만, GPT 호출(currentStep 2 이상)은 시작되었고 전체 로딩중일 때 간단한 메시지 -->
        <div v-else-if="isLoading && currentStep >= 2 && currentStep < 4" class="initial-loading-message">
          <p><i class="fas fa-spinner fa-spin"></i> AI가 맞춤 추천을 생성하고 있습니다. 잠시만 기다려주세요...</p>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import Chart from 'chart.js/auto'

const router = useRouter()
const messages = ref([])
const recommendations = ref([])
const isLoading = ref(false)
const currentStep = ref(0)
const simulationChart = ref(null)
const hasProfile = ref(false)
const profileData = ref({
  investment_purpose: '',
  investment_tendency: '',
  investment_term: '',
  amount_available: null
})
const simulationData = ref({
  expectedReturn: 0,
  returnRate: '0',
  risk_analysis: '',
  diversification: '',
  future_scenario: null,
  visualization: null,
  initialInvestmentAmount: null
})

let chart = null

// 프로필 정보 확인
const checkProfile = async () => {
  try {
    const token = localStorage.getItem('accessToken')
    const response = await axios.get('http://127.0.0.1:8000/api/v1/accounts/profile/', {
      headers: { Authorization: `Token ${token}` }
    })
    const userProfile = response.data
    hasProfile.value = !!(userProfile.investment_purpose && 
                         userProfile.investment_tendency && 
                         userProfile.investment_term && 
                         userProfile.amount_available !== null && userProfile.amount_available !== '')
    
    if (hasProfile.value) {
      fetchRecommendations()
    } else {
      addMessage('ai', '안녕하세요! 맞춤형 금융상품을 추천해드리기 위해 프로필 정보가 필요합니다.')
    }
  } catch (error) {
    console.error('프로필 정보 조회 실패:', error)
    hasProfile.value = false
    addMessage('ai', '프로필 정보를 불러오는 데 실패했습니다. 먼저 로그인하거나 프로필을 완성해주세요.')
  }
}

// 프로필 저장
const submitProfile = async () => {
  try {
    const token = localStorage.getItem('accessToken')
    await axios.put('http://127.0.0.1:8000/api/v1/accounts/profile/', profileData.value, {
      headers: { Authorization: `Token ${token}` }
    })
    hasProfile.value = true
    messages.value = []
    fetchRecommendations()
  } catch (error) {
    console.error('프로필 업데이트 실패:', error)
    addMessage('ai', '프로필 업데이트에 실패했습니다. 다시 시도해주세요.')
    if (error.response) {
      console.error("Error response data:", error.response.data)
    }
  }
}

// 메시지 추가 함수
const addMessage = (type, content) => {
  messages.value.push({ type, content })
  setTimeout(() => {
    const chatMessages = document.querySelector('.chat-messages')
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight
    }
  }, 100)
}

// 로딩 애니메이션 시작
const startLoading = () => {
  isLoading.value = true
  currentStep.value = 0
  
  const interval = setInterval(() => {
    currentStep.value++
    if (currentStep.value >= 4) {
      clearInterval(interval)
      isLoading.value = false
    }
  }, 1500)
}

// 차트 생성
const createSimulationChart = (data) => {
  if (!simulationChart.value) {
    console.log('Chart container not found')
    return
  }

  if (chart) {
    chart.destroy()
  }

  const ctx = simulationChart.value.getContext('2d')
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['현재', '1년 후', '2년 후', '3년 후'],
      datasets: [{
        label: '예상 자산',
        data: data,
        borderColor: '#4f46e5',
        backgroundColor: 'rgba(79, 70, 229, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            callback: (value) => `${(value / 10000).toFixed(0)}만원`
          }
        }
      },
      animation: {
        duration: 2000,
        easing: 'easeInOutQuart'
      }
    }
  })
}

// 이미지 에러 핸들러 추가
const handleImageError = (e) => {
  console.warn('이미지 로드 실패, 대체 이미지 사용 또는 메시지 표시', e.target.src);
  if (simulationData.value.future_scenario?.visualization) {
    simulationData.value.future_scenario.visualization.image_url = null;
  }
}

// 금액 문자열을 숫자로 변환하는 헬퍼 함수
const parseCurrencyString = (currencyString) => {
  if (typeof currencyString === 'number') {
    return currencyString;
  }
  if (typeof currencyString !== 'string') {
    return NaN;
  }
  // "원" 글자 및 쉼표 제거, 공백 제거
  const cleanedString = currencyString.replace(/원|,/g, '').trim();
  const number = parseFloat(cleanedString);
  return isNaN(number) ? 0 : number; // NaN이면 0으로 처리 (또는 다른 기본값)
};

// 추천 상품 조회
const fetchRecommendations = async () => {
  isLoading.value = true
  currentStep.value = 1

  try {
    const token = localStorage.getItem('accessToken')

    // API를 통해 최신 프로필 정보 가져오기
    const profileResponse = await axios.get('http://127.0.0.1:8000/api/v1/accounts/profile/', {
      headers: { Authorization: `Token ${token}` }
    })
    const profile = profileResponse.data
    
    // simulationData에 초기 투자금 저장
    simulationData.value.initialInvestmentAmount = profile.amount_available;

    if (!profile.investment_tendency) {
      addMessage('ai', '프로필 정보가 충분하지 않아 추천을 드릴 수 없습니다. 프로필을 완성해주세요.')
      isLoading.value = false
      return
    }

    const prompt = `
    당신은 사용자의 금융 목표 달성을 돕는 따뜻한 금융 스토리텔러이자 전문 어드바이저입니다. 
    사용자의 프로필을 깊이 이해하고, 단순한 상품 추천을 넘어 그들의 꿈이 현실이 되었을 때의 감동적인 미래를 생생하게 그려주세요. 
    구체적이고 실행 가능한 금융 상품 추천과 함께, 희망찬 미래 시나리오를 제공해야 합니다.
    "지금 당장 목표를 이루기엔 부족해 보여도 괜찮아요. 이 작은 시작이 꿈을 향한 든든한 첫걸음이 될 거예요! 더 큰 미래를 위한 디딤돌로 만들어가요."


    사용자 프로필:
    - 투자 목적: ${profile.investment_purpose || '미정'} (예: '집 마련', '세계 여행', '조기 은퇴')
    - 투자 성향: ${profile.investment_tendency} (예: '안정 추구형', '공격 투자형')
    - 투자 기간: ${profile.investment_term}개월
    - 매월 투자 가능 금액: ${profile.amount_available}원 (이 금액은 사용자가 한 달에 투자할 수 있는 금액으로 간주합니다.)

    요청 사항:
    위 사용자 프로필을 바탕으로, 3가지의 다양한 투자 상품을 추천해주세요.
    각 상품에 대해 다음 정보를 포함해야 합니다: "product_name", "product_type" (deposit, saving, stock, fund, bond, real_estate 중 하나), "score" (0-100점), "max_rate" (최고 금리, %), "term" (투자 기간, 개월), "reason" (이 사용자에게 적합한 추천 이유), "risk_level" (low, medium, high 중 하나), "min_amount" (최소 가입 금액, 원), "expected_return" (예상 수익금, 원).

    가장 중요한 부분은 "simulation" 섹션입니다. 다음 내용을 포함해주세요:
    1.  "expectedReturn": 전체 포트폴리오의 총 예상 수익금 (원).
    2.  "returnRate": 전체 포트폴리오의 총 예상 수익률 (%).
    3.  "risk_analysis": 전체 포트폴리오의 위험도에 대한 분석.
    4.  "diversification": 자산 분산 전략에 대한 설명.
    5.  "future_scenario": 여기가 핵심입니다!
        *   "description": 사용자의 '투자 목적', '투자 기간', '매월 투자 가능 금액'을 바탕으로, **카카오뱅크 저금통 문구처럼 간결하지만 임팩트 있고, 현실적이면서도 희망찬 메시지를 전달하는** 미래 시나리오를 작성해주세요. 사용자가 무엇을 경험하고 어떤 긍정적인 감정을 느낄 수 있는지에 초점을 맞춰주세요.
            사용자가 매월 제시된 금액을 ${profile.investment_term}개월 동안 꾸준히 투자했을 때 달성 가능한 구체적인 목표와 총 누적 투자액을 언급하며, 그로 인해 펼쳐질 긍정적 미래를 현실적이면서도 매력적으로 묘사해야 합니다.

            예시 (투자 목적: '유럽 여행 자금', 투자 기간: 12개월, 매월 투자 가능 금액: 50만원 가정):
            "매월 50만원씩, 1년 뒤 총 600만원으로 떠나는 꿈의 유럽 여행! 로맨틱한 파리의 밤, 상상만으로도 설레지 않나요?"

            사용자의 투자 목적이 '집 마련'이라면 아늑한 보금자리를, '차량 구매'라면 도로를 달리는 자유를, '노후 자금'이라면 여유로운 황혼을 그려주세요. 현실적이면서도 가슴 뛰는 이야기로 만들어주세요.

        *   "visualization":
            *   "type": 사용자의 투자 목적 (예: '${profile.investment_purpose || '목표 달성'}').
            *   "object": 투자 목적의 핵심 키워드를 구체적으로 지정해주세요. (예: 집 마련 -> '따뜻한 햇살이 드는 거실', 차량 구매 -> '새 차와 함께하는 해안도로 드라이브', 세부 여행 -> '세부의 청록색 바다와 해변').
            *   "style": "현실적이면서도 따뜻한 감성이 느껴지는 3D 렌더링, 밝고 희망찬 색감, 보는 이에게 행복과 성취감을 전달하는 스타일."
            *   "emotion": "성취감, 행복, 기대감, 자유, 평온함."
            *   "image_prompt": 위 "description"과 "visualization"의 세부 사항을 바탕으로 DALL-E가 이미지를 생성할 수 있도록, 매우 구체적이고 생생한 장면을 묘사하는 프롬프트를 작성해주세요.
                예시 (세부 여행): "따스한 햇살 아래, 필리핀 세부의 청록색 수정처럼 맑은 바다에서 친구들과 함께 스노클링을 즐기며 환하게 웃고 있는 모습. 다채로운 산호초와 열대어들이 보이고, 멀리 야자수가 우거진 하얀 모래사장이 펼쳐져 있음. 현실적이면서도 꿈같은 휴가의 행복감과 자유로움이 넘치는 밝고 선명한 3D 렌더링."
                예시 (집 마련): "따스한 오후 햇살이 가득 들어오는 넓은 창을 가진 현대적이고 아늑한 거실 풍경. 편안한 소파와 예쁜 화분들이 놓여있고, 창밖으로는 푸른 정원이 보임. 가족의 행복과 안락함, 꿈을 이룬 성취감이 느껴지는 고품질 3D 렌더링. 부드럽고 따뜻한 색조 사용."

    출력 형식:
    반드시 아래와 같은 순수 JSON 객체만을 출력해야 합니다. JSON 객체 앞뒤로 어떠한 설명이나 추가 텍스트도 포함하지 마세요.
    {
      "products": [
        {
          "product_name": "상품명",
          "product_type": "deposit (예금), saving (적금), stock (주식), fund (펀드), bond (채권), real_estate (부동산) 중 하나",
          "score": "점수 (0-100)",
          "max_rate": "최고 예상 수익률 (%)",
          "term": "투자 기간 (개월)",
          "reason": "추천 이유 상세 설명",
          "risk_level": "low, medium, high 중 하나",
          "min_amount": "최소 투자 금액 (원)",
          "expected_return": "예상 수익금 (원)"
        }
        // ... (최대 2개까지 추가 상품 추천)
      ],
      "simulation": {
        "expectedReturn": "전체 예상 수익금 (원)",
        "returnRate": "전체 예상 수익률 (%)",
        "risk_analysis": "포트폴리오 위험도 종합 분석",
        "diversification": "자산 분산 전략 및 이유 설명",
        "future_scenario": {
          "description": "위에서 설명한 감동적이고 구체적인 미래 시나리오",
          "visualization": {
            "type": "사용자 투자 목적",
            "object": "미래 시나리오의 핵심 대상 또는 장면",
            "style": "이미지 스타일",
            "emotion": "이미지에 담길 감정",
            "image_prompt": "DALL-E 이미지 생성용 상세 프롬프트"
          }
        }
      }
    }
    `;
    console.log("Sending prompt to GPT:", prompt)
    currentStep.value = 2

    const gptApiResponse = await axios.post('http://127.0.0.1:8000/api/v1/product-recommender/gpt/', 
      { prompt }, 
      { headers: { Authorization: `Token ${token}` } }
    )
    
    console.log("GPT Response raw object:", gptApiResponse.data)
    let gptResponseText = gptApiResponse.data.response;

    if (typeof gptResponseText === 'string') {
      if (gptResponseText.startsWith("```json")) {
        gptResponseText = gptResponseText.substring(7, gptResponseText.length - 3).trim();
      } else if (gptResponseText.startsWith("```")) {
        gptResponseText = gptResponseText.substring(3, gptResponseText.length - 3).trim();
      }
    }
    
    let parsedData;
    try {
      parsedData = JSON.parse(gptResponseText);
    } catch (e) {
      console.error("GPT 응답 파싱 실패:", e);
      console.error("파싱 시도한 텍스트:", gptResponseText); 
      addMessage('ai', '추천 데이터를 이해하는 데 실패했습니다. 응답 형식을 확인해주세요.');
      isLoading.value = false;
      return;
    }
    console.log("Parsed GPT Data:", parsedData)
    currentStep.value = 3

    recommendations.value = parsedData.products.map(p => ({
      ...p,
      score: parseInt(p.score) || 0,
      max_rate: parseFloat(String(p.max_rate).replace('%','')) || 0,
      min_amount: parseCurrencyString(p.min_amount),
      expected_return: parseCurrencyString(p.expected_return)
    }));

    simulationData.value = {
      initialInvestmentAmount: profile.amount_available,
      expectedReturn: parseCurrencyString(parsedData.simulation.expectedReturn),
      returnRate: parseFloat(String(parsedData.simulation.returnRate).replace('%','')) || 0,
      risk_analysis: parsedData.simulation.risk_analysis,
      diversification: parsedData.simulation.diversification,
      future_scenario: parsedData.simulation.future_scenario,
    };

    addMessage('ai', '다음은 맞춤형 투자 추천입니다.')

    if (simulationData.value.future_scenario?.visualization?.image_prompt) {
      currentStep.value = 4;
      try {
        const imagePrompt = simulationData.value.future_scenario.visualization.image_prompt;
        const imageType = simulationData.value.future_scenario.visualization.object || simulationData.value.future_scenario.visualization.type || 'goal';
        
        const imageResponse = await axios.post('http://127.0.0.1:8000/api/v1/product-recommender/generate-image/', 
          { prompt: imagePrompt, type: imageType }, 
          { headers: { Authorization: `Token ${token}` } }
        );

        if (imageResponse.data && imageResponse.data.status === 'success' && imageResponse.data.image_url) {
          simulationData.value.future_scenario.visualization.image_url = `http://127.0.0.1:8000${imageResponse.data.image_url}`; 
        } else {
          console.error('이미지 생성 실패:', imageResponse.data.message || '응답 없음');
          if (simulationData.value.future_scenario?.visualization) {
            simulationData.value.future_scenario.visualization.image_url = null;
          }
        }
      } catch (imageError) {
        console.error('이미지 생성 API 호출 오류:', imageError);
        if (simulationData.value.future_scenario?.visualization) {
            simulationData.value.future_scenario.visualization.image_url = null;
          }
      }
    }

  } catch (error) {
    console.error('추천 정보 조회 또는 처리 중 오류:', error)
    let errorMessage = '추천 정보를 가져오는 데 실패했습니다.';
    if (error.response) {
      console.error("오류 응답 데이터:", error.response.data);
      errorMessage = error.response.data.message || error.response.data.error || errorMessage;
    } else {
      console.error("오류 메시지:", error.message)
    }
    addMessage('ai', errorMessage)
  } finally {
    isLoading.value = false
    currentStep.value = 0;
  }
}

// 숫자 포맷팅 함수 추가
const formatCurrency = (value) => {
  const numValue = parseCurrencyString(String(value));
  if (isNaN(numValue)) {
    return '0';
  }
  return numValue.toLocaleString('ko-KR');
}

// 상품 상세보기
const viewProductDetail = (recommendation) => {
  const productId = recommendation.deposit_product?.id || recommendation.saving_product?.id
  const productType = recommendation.deposit_product ? 'deposit' : 'saving'
  router.push(`/products/${productType}/${productId}`)
}

onMounted(async () => {
  await checkProfile();
});

onUnmounted(() => {
  if (chart) {
    chart.destroy()
    chart = null;
  }
})
</script>

<style scoped>
.ai-recommendation {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.chat-interface {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.chat-container {
  background: #fff;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  height: 400px;
  overflow: hidden;
}

.chat-messages {
  height: 100%;
  overflow-y: auto;
  padding: 1rem;
}

.message {
  margin-bottom: 1rem;
  max-width: 80%;
}

.message.ai {
  margin-right: auto;
}

.message.user {
  margin-left: auto;
}

.message-content {
  padding: 0.8rem 1rem;
  border-radius: 1rem;
  background: #f5f5f5;
}

.message.ai .message-content {
  background: #e3f2fd;
}

.message.user .message-content {
  background: #e8f5e9;
}

.profile-form {
  background: #fff;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #333;
  font-weight: 500;
}

.form-group select,
.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 0.5rem;
  font-size: 1rem;
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.submit-btn:hover {
  background: #1565c0;
}

.simulation-interface {
  display: grid;
  gap: 2rem;
}

.loading-container {
  background: #fff;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.loading-steps {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.step {
  text-align: center;
  padding: 1rem;
  border-radius: 0.5rem;
  background: #f5f5f5;
  opacity: 0.5;
  transition: all 0.3s;
}

.step.active {
  background: #e3f2fd;
  opacity: 1;
}

.step i {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
  color: #1976d2;
}

.simulation-results {
  background: #fff;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.main-scenario-content-wrapper {
  display: flex;
  flex-direction: row;
  gap: 2rem;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.scenario-text-container {
  position: relative;
  width: 65%;
  min-width: 450px;
  max-width: 800px;
  aspect-ratio: 740 / 700;
}

.scenario-text-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('@/assets/gpt_load.png');
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  z-index: 1;
}

.scenario-text-content {
  position: absolute;
  top: 68%; 
  left: 55%;
  transform: translate(-50%, -50%); 
  width: 68%; 
  max-height: 38%;
  padding: 12px 18px;
  text-align: left; 
  color: #212529;
  font-size: 0.8rem; 
  font-weight: bold;
  line-height: 1.6;
  overflow-y: auto; 
  z-index: 2; 
  background-color: #e7f3fe;
  border-radius: 8px;
  box-sizing: border-box; 
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.scenario-text-content p {
  margin: 0;
}

.future-scenario {
  width: 35%;
  min-width: 300px;
  background: #fff;
  padding: 0;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.scenario-visualization {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  width: 100%;
}

.visualization-info {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  background-color: rgba(243, 244, 246, 0.8);
  padding: 0.75rem;
  border-radius: 0.5rem;
  width: 100%;
}

.visualization-info span {
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.8rem;
  background: #e9ecef;
  color: #495057;
  font-weight: 500;
}

.cute-3d-container {
  width: 100%;
  height: 380px;
  background: #f9fafb;
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
}

.cute-3d-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  transition: transform 0.3s ease;
}

.loading-image {
  color: #666;
  font-size: 1.2rem;
  text-align: center;
}

.simulation-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 0.5rem;
}

.detail-item i {
  font-size: 1.5rem;
  color: #1976d2;
  margin-right: 1rem;
}

.detail-content h4 {
  margin: 0;
  color: #666;
  font-size: 0.9rem;
}

.detail-content p {
  margin: 0.5rem 0 0;
  color: #333;
  font-size: 1.2rem;
  font-weight: 500;
}

.recommendations {
  background: #fff;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

.recommendation-card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: 1rem;
  overflow: hidden;
  transition: transform 0.3s, box-shadow 0.3s;
  padding: 1.5rem;
}

.recommendation-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.recommendation-card.deposit {
  border-left: 4px solid #4f46e5;
}

.recommendation-card.saving {
  border-left: 4px solid #10b981;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h4 {
  margin: 0;
  color: #1f2937;
  font-size: 1.25rem;
}

.score {
  background: #4f46e5;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 600;
}

.product-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #4b5563;
}

.info-item i {
  color: #4f46e5;
}

.recommendation-reason {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 0.5rem;
}

.recommendation-reason h5 {
  color: #1f2937;
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
}

.recommendation-reason p {
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
  font-size: 0.875rem;
}

.portfolio-summary {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.summary-item {
  margin-bottom: 1.5rem;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-item h4 {
  color: #1f2937;
  margin: 0 0 0.5rem 0;
  font-size: 1.1rem;
}

.summary-item p {
  color: #4b5563;
  margin: 0;
  line-height: 1.6;
}

.card-badges {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.risk-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.risk-badge.low {
  background: #dcfce7;
  color: #166534;
}

.risk-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.risk-badge.high {
  background: #fee2e2;
  color: #991b1b;
}

.recommendation-card.stock {
  border-left: 4px solid #f59e0b;
}

.recommendation-card.fund {
  border-left: 4px solid #8b5cf6;
}

.recommendation-card.bond {
  border-left: 4px solid #3b82f6;
}

.recommendation-card.real_estate {
  border-left: 4px solid #ef4444;
}

@media (max-width: 768px) {
  .ai-recommendation {
    padding: 1rem;
  }

  .loading-steps {
    grid-template-columns: 1fr;
  }

  .simulation-details {
    grid-template-columns: 1fr;
  }

  .recommendation-grid {
    grid-template-columns: 1fr;
  }
  
  .product-info {
    grid-template-columns: 1fr;
  }

  .model-container {
    height: 300px;
  }

  .scenario-content {
    grid-template-columns: 1fr;
  }
  
  .cute-3d-container {
    height: 250px;
  }
}

.simulation-results > h3 {
  color: #1f2937;
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
}
</style> 