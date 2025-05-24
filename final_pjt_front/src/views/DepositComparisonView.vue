<template>
  <div class="deposit-comparison">
    <!-- 로딩 상태 표시 -->
    <div v-if="loading" class="loading-state">
      <p>상품 정보를 불러오는 중입니다...</p>
    </div>

    <!-- 에러 상태 표시 -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchProducts">다시 시도</button>
    </div>

    <!-- 필터 섹션 -->
    <div v-if="!loading && !error" class="filter-section">
      <div class="bank-filter">
        <h3>은행 선택</h3>
        <div class="bank-buttons">
          <button 
            v-for="bank in banks" 
            :key="bank.id"
            :class="{ active: selectedBank === bank.id }"
            @click="selectBank(bank.id)"
          >
            {{ bank.name }}
          </button>
        </div>
      </div>
      
      <div class="period-filter">
        <h3>가입 기간</h3>
        <select v-model="selectedPeriod">
          <option value="6">6개월</option>
          <option value="12">12개월</option>
          <option value="24">24개월</option>
          <option value="36">36개월</option>
        </select>
      </div>
    </div>

    <!-- 상품 목록 -->
    <div v-if="!loading && !error" class="products-section">
      <div class="products-header">
        <h2>예적금 상품 목록</h2>
        <div class="sort-options">
          <button 
            :class="{ active: sortBy === 'rate' }"
            @click="sortBy = 'rate'"
          >
            금리순
          </button>
          <button 
            :class="{ active: sortBy === 'name' }"
            @click="sortBy = 'name'"
          >
            상품명순
          </button>
        </div>
      </div>

      <div class="products-grid">
        <div 
          v-for="product in filteredProducts" 
          :key="product.id"
          class="product-card"
          @click="showProductDetail(product)"
        >
          <div class="bank-logo">
            <img :src="product.bankLogo" :alt="product.bankName">
          </div>
          <div class="product-info">
            <h3>{{ product.name }}</h3>
            <p class="bank-name">{{ product.bankName }}</p>
            <div class="rate-info">
              <span class="rate-label">기본 금리</span>
              <span class="rate-value">{{ product.baseRate }}%</span>
            </div>
            <div class="period-info">
              <span class="period-label">가입 기간</span>
              <span class="period-value">{{ product.period }}개월</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 상품 상세 모달 -->
    <div v-if="selectedProduct" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="close-button" @click="closeModal">&times;</button>
        <div class="product-detail">
          <div class="detail-header">
            <img :src="selectedProduct.bankLogo" :alt="selectedProduct.bankName">
            <h2>{{ selectedProduct.name }}</h2>
          </div>
          <div class="detail-info">
            <div class="info-row">
              <span class="label">은행명</span>
              <span class="value">{{ selectedProduct.bankName }}</span>
            </div>
            <div class="info-row">
              <span class="label">기본 금리</span>
              <span class="value">{{ selectedProduct.baseRate }}%</span>
            </div>
            <div class="info-row">
              <span class="label">최고 금리</span>
              <span class="value">{{ selectedProduct.maxRate }}%</span>
            </div>
            <div class="info-row">
              <span class="label">가입 기간</span>
              <span class="value">{{ selectedProduct.period }}개월</span>
            </div>
            <div class="info-row">
              <span class="label">최소 가입 금액</span>
              <span class="value">{{ selectedProduct.minAmount.toLocaleString() }}원</span>
            </div>
            <div class="info-row">
              <span class="label">이자 지급 방식</span>
              <span class="value">{{ selectedProduct.interestPayment }}</span>
            </div>
          </div>
          <div class="detail-description">
            <h3>상품 설명</h3>
            <p>{{ selectedProduct.description }}</p>
          </div>
          <div class="detail-features">
            <h3>특징</h3>
            <ul>
              <li v-for="(feature, index) in selectedProduct.features" :key="index">
                {{ feature }}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 상태 관리
const selectedBank = ref(null)
const selectedPeriod = ref('12')
const sortBy = ref('rate')
const selectedProduct = ref(null)
const products = ref([])
const loading = ref(false)
const error = ref(null)

// 은행 목록
const banks = ref([
  { id: 1, name: '전체' },
  { id: 2, name: '국민은행' },
  { id: 3, name: '신한은행' },
  { id: 4, name: '우리은행' },
  { id: 5, name: '하나은행' },
  { id: 6, name: '농협은행' },
])

// API에서 데이터 가져오기
const fetchProducts = async () => {
  loading.value = true
  error.value = null
  try {
    // 먼저 금융위원회 API에서 데이터를 가져와서 저장
    await axios.get('http://127.0.0.1:8000/api/v1/products/save-deposit-products/')
    
    // 그 다음 저장된 예금 상품 목록을 가져옴
    const response = await axios.get('http://127.0.0.1:8000/api/v1/products/deposit-products/')
    products.value = response.data.map(product => ({
      id: product.fin_prdt_cd,
      name: product.fin_prdt_nm,
      bankName: product.kor_co_nm,
      bankId: getBankId(product.kor_co_nm),
      bankLogo: getBankLogo(product.kor_co_nm),
      baseRate: product.options[0]?.intr_rate || 0,
      maxRate: product.options[0]?.intr_rate2 || 0,
      period: parseInt(product.options[0]?.save_trm) || 12,
      minAmount: 1000000, // 기본값 설정
      interestPayment: product.options[0]?.intr_rate_type_nm || '만기일시지급',
      description: product.join_way || '상품 설명이 없습니다.',
      features: [
        product.spcl_cnd || '우대조건이 없습니다.',
        product.join_member || '가입대상 정보가 없습니다.',
        product.etc_note || '기타 유의사항이 없습니다.'
      ].filter(Boolean)
    }))
  } catch (err) {
    error.value = '상품 정보를 가져오는데 실패했습니다.'
    console.error('Error fetching products:', err)
  } finally {
    loading.value = false
  }
}

// 은행 ID 매핑 함수
const getBankId = (bankName) => {
  const bankMap = {
    '국민은행': 2,
    '신한은행': 3,
    '우리은행': 4,
    '하나은행': 5,
    '농협은행': 6
  }
  return bankMap[bankName] || 1
}

// 은행 로고 매핑 함수
const getBankLogo = (bankName) => {
  const logoMap = {
    '국민은행': '/src/assets/bank-logos/kb.png',
    '신한은행': '/src/assets/bank-logos/shinhan.png',
    '우리은행': '/src/assets/bank-logos/woori.png',
    '하나은행': '/src/assets/bank-logos/hana.png',
    '농협은행': '/src/assets/bank-logos/nh.png'
  }
  return logoMap[bankName] || '/src/assets/bank-logos/default.png'
}

// 필터링된 상품 목록
const filteredProducts = computed(() => {
  let filtered = [...products.value]
  
  // 은행 필터링 (전체가 아닐 때만 필터링)
  if (selectedBank.value && selectedBank.value !== 1) {
    filtered = filtered.filter(product => product.bankId === selectedBank.value)
  }
  
  // 기간 필터링
  filtered = filtered.filter(product => product.period === parseInt(selectedPeriod.value))
  
  // 정렬
  filtered.sort((a, b) => {
    if (sortBy.value === 'rate') {
      return b.baseRate - a.baseRate
    } else {
      return a.name.localeCompare(b.name)
    }
  })
  
  return filtered
})

// 메서드
const selectBank = (bankId) => {
  selectedBank.value = bankId
}

const showProductDetail = (product) => {
  selectedProduct.value = product
}

const closeModal = () => {
  selectedProduct.value = null
}

// 컴포넌트 마운트 시 데이터 가져오기
onMounted(() => {
  fetchProducts()
})
</script>

<style scoped>
.deposit-comparison {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.filter-section {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #1a1a1a;
  border-radius: 10px;
}

.bank-filter, .period-filter {
  flex: 1;
}

.bank-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.bank-buttons button {
  padding: 8px 16px;
  border: 1px solid #0064FF;
  background: transparent;
  color: #fff;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.bank-buttons button.active {
  background-color: #0064FF;
  color: #fff;
}

.period-filter select {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  background-color: #2a2a2a;
  color: #fff;
  border: 1px solid #444;
  border-radius: 5px;
}

.products-section {
  background-color: #1a1a1a;
  border-radius: 10px;
  padding: 20px;
}

.products-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sort-options {
  display: flex;
  gap: 10px;
}

.sort-options button {
  padding: 8px 16px;
  border: 1px solid #444;
  background: transparent;
  color: #fff;
  border-radius: 5px;
  cursor: pointer;
}

.sort-options button.active {
  background-color: #0064FF;
  border-color: #0064FF;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.product-card {
  background-color: #2a2a2a;
  border-radius: 10px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.product-card:hover {
  transform: translateY(-5px);
}

.bank-logo {
  width: 60px;
  height: 60px;
  margin-bottom: 15px;
}

.bank-logo img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.product-info h3 {
  margin: 0 0 10px 0;
  color: #fff;
}

.bank-name {
  color: #888;
  margin-bottom: 15px;
}

.rate-info, .period-info {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.rate-label, .period-label {
  color: #888;
}

.rate-value {
  color: #0064FF;
  font-weight: bold;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #2a2a2a;
  border-radius: 10px;
  padding: 30px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 30px;
}

.detail-header img {
  width: 80px;
  height: 80px;
  object-fit: contain;
}

.detail-info {
  margin-bottom: 30px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #444;
}

.info-row .label {
  color: #888;
}

.info-row .value {
  color: #fff;
  font-weight: 500;
}

.detail-description, .detail-features {
  margin-top: 20px;
}

.detail-description h3, .detail-features h3 {
  color: #fff;
  margin-bottom: 15px;
}

.detail-description p {
  color: #ccc;
  line-height: 1.6;
}

.detail-features ul {
  list-style: none;
  padding: 0;
}

.detail-features li {
  color: #ccc;
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.detail-features li::before {
  content: "•";
  color: #0064FF;
  position: absolute;
  left: 0;
}

/* 로딩 및 에러 상태 스타일 추가 */
.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  background-color: #1a1a1a;
  border-radius: 10px;
  margin-bottom: 20px;
}

.error-state button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #0064FF;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.error-state button:hover {
  background-color: #0052cc;
}
</style> 