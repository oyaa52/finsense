<template>
  <div class="deposit-comparison">
    <!-- 필터 섹션 -->
    <div class="filter-section">
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
          <option value="all">전체</option>
          <option value="6">6개월</option>
          <option value="12">12개월</option>
          <option value="24">24개월</option>
          <option value="36">36개월</option>
        </select>
      </div>
    </div>

    <!-- 에러 상태 표시 -->
    <div v-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="fetchProducts">다시 시도</button>
    </div>

    <!-- 상품 목록 -->
    <div class="products-section">
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

      <!-- 로딩 중일 때 스켈레톤 UI -->
      <div v-if="loading" class="products-grid">
        <div v-for="n in 12" :key="n" class="product-card skeleton">
          <div class="bank-name-header">
            <div class="skeleton-text"></div>
          </div>
          <div class="product-info">
            <div class="skeleton-text"></div>
            <div class="skeleton-text"></div>
            <div class="skeleton-text"></div>
          </div>
        </div>
      </div>

      <!-- 실제 상품 목록 -->
      <div v-else class="products-grid">
        <div 
          v-for="product in filteredProducts" 
          :key="product.id"
          class="product-card"
          @click="showProductDetail(product)"
        >
          <div class="bank-name-header">
            <h3>{{ product.bankName }}</h3>
          </div>
          <div class="product-info">
            <h3 class="product-title">{{ product.name }}</h3>
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

      <!-- 페이지네이션 -->
      <div class="pagination" v-if="!loading && totalPages > 1">
        <button 
          :disabled="currentPage === 1"
          @click="handlePageChange(currentPage - 1)"
          class="page-button"
        >
          이전
        </button>
        
        <button 
          v-for="page in totalPages" 
          :key="page"
          :class="{ active: currentPage === page }"
          @click="handlePageChange(page)"
          class="page-button"
        >
          {{ page }}
        </button>
        
        <button 
          :disabled="currentPage === totalPages"
          @click="handlePageChange(currentPage + 1)"
          class="page-button"
        >
          다음
        </button>
      </div>
    </div>

    <!-- 상품 상세 모달 -->
    <div v-if="selectedProduct" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <button class="close-button" @click="closeModal">&times;</button>
        <div class="product-detail">
          <div class="detail-header">
            <h2>{{ selectedProduct.name }}</h2>
            <p class="bank-name">{{ selectedProduct.bankName }}</p>
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
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

// 상태 관리
const selectedBank = ref(null)  // 초기값을 null로 설정
const selectedPeriod = ref('all')
const sortBy = ref('rate')
const selectedProduct = ref(null)
const products = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = ref(50)

// 은행 목록
const banks = ref([
  { id: 2, name: '국민은행' },
  { id: 3, name: '신한은행' },
  { id: 4, name: '우리은행' },
  { id: 5, name: '하나은행' },
  { id: 6, name: '농협은행' },
])

// API에서 데이터 가져오기
const fetchProducts = async (page = 1) => {
  loading.value = true
  error.value = null
  try {
    // 먼저 금융위원회 API에서 데이터를 가져와서 저장
    await axios.get('http://127.0.0.1:8000/api/v1/products/save-deposit-products/')
    
    // 그 다음 저장된 예금 상품 목록을 가져옴
    const response = await axios.get('http://127.0.0.1:8000/api/v1/products/deposit-products/', {
      params: {
        page: page,
        page_size: pageSize.value,
        bank_id: selectedBank.value,  // null이면 모든 은행
        period: selectedPeriod.value === 'all' ? undefined : selectedPeriod.value,
        sort_by: sortBy.value
      }
    })
    
    // 페이지네이션 정보 업데이트
    currentPage.value = page
    totalPages.value = Math.ceil(response.data.count / pageSize.value)
    
    // 상품 데이터 매핑
    products.value = response.data.results.map(product => {
      // 해당 기간의 옵션 찾기 (전체 선택 시 첫 번째 옵션 사용)
      const periodOption = selectedPeriod.value === 'all' 
        ? product.options[0] 
        : product.options.find(opt => opt.save_trm === selectedPeriod.value)
      
      return {
        id: product.fin_prdt_cd,
        name: product.fin_prdt_nm,
        bankName: product.kor_co_nm,
        bankId: getBankId(product.kor_co_nm),
        baseRate: periodOption?.intr_rate || 0,
        maxRate: periodOption?.intr_rate2 || 0,
        period: parseInt(periodOption?.save_trm) || 12,
        minAmount: 1000000,
        interestPayment: periodOption?.intr_rate_type_nm || '만기일시지급',
        description: product.join_way || '상품 설명이 없습니다.',
        features: [
          product.spcl_cnd || '우대조건이 없습니다.',
          product.join_member || '가입대상 정보가 없습니다.',
          product.etc_note || '기타 유의사항이 없습니다.'
        ].filter(Boolean)
      }
    })
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

// 필터링된 상품 목록 (단순히 products를 반환)
const filteredProducts = computed(() => products.value)

// 필터 변경 시 데이터 다시 가져오기
watch([selectedBank, selectedPeriod, sortBy], () => {
  currentPage.value = 1 // 필터 변경 시 첫 페이지로 이동
  fetchProducts(1)
})

// 메서드
const selectBank = (bankId) => {
  // 같은 은행을 다시 클릭하면 선택 해제
  selectedBank.value = selectedBank.value === bankId ? null : bankId
}

const showProductDetail = (product) => {
  selectedProduct.value = product
}

const closeModal = () => {
  selectedProduct.value = null
}

// 페이지 변경 핸들러
const handlePageChange = (page) => {
  currentPage.value = page
  fetchProducts(page)
}

// 데이터 새로고침 함수
const refreshData = async () => {
  try {
    loading.value = true
    await axios.get('http://127.0.0.1:8000/api/v1/products/save-deposit-products/')
    await fetchProducts(currentPage.value)
  } catch (err) {
    error.value = '데이터 새로고침에 실패했습니다.'
    console.error('Error refreshing data:', err)
  } finally {
    loading.value = false
  }
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

.bank-name-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #444;
}

.bank-name-header h3 {
  color: #0064FF;
  font-size: 1.2rem;
  margin: 0;
}

.product-title {
  font-size: 1.1rem;
  margin: 0 0 15px 0;
  color: #fff;
  line-height: 1.4;
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
  box-shadow: 0 5px 15px rgba(0, 100, 255, 0.1);
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
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #444;
}

.detail-header h2 {
  color: #fff;
  margin: 0 0 10px 0;
  font-size: 1.8rem;
}

.detail-header .bank-name {
  color: #0064FF;
  font-size: 1.2rem;
  margin: 0;
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
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

.loading-animation {
  margin-bottom: 20px;
}

.loader {
  width: 48px;
  height: 48px;
  border: 3px solid #0064FF;
  border-bottom-color: transparent;
  border-radius: 50%;
  display: inline-block;
  box-sizing: border-box;
  animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 1.2rem;
}

.text-gradient {
  background: linear-gradient(45deg, #0064FF, #00BFFF);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 500;
}

.error-state p {
  color: #ff6b6b;
  font-size: 1.2rem;
  margin-bottom: 20px;
  background: linear-gradient(45deg, #ff6b6b, #ff8787);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.error-state button {
  padding: 10px 20px;
  background: linear-gradient(45deg, #0064FF, #00BFFF);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.error-state button:hover {
  transform: translateY(-2px);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 2rem;
  gap: 0.5rem;
}

.page-button {
  padding: 0.5rem 1rem;
  border: 1px solid #0064FF;
  background-color: transparent;
  color: #0064FF;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-button:hover:not(:disabled) {
  background-color: #0064FF;
  color: white;
}

.page-button.active {
  background-color: #0064FF;
  color: white;
}

.page-button:disabled {
  border-color: #ccc;
  color: #ccc;
  cursor: not-allowed;
}

/* 스켈레톤 로딩 스타일 */
.skeleton {
  position: relative;
  overflow: hidden;
  background: #2a2a2a;
}

.skeleton::after {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  transform: translateX(-100%);
  background-image: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0,
    rgba(255, 255, 255, 0.05) 20%,
    rgba(255, 255, 255, 0.1) 60%,
    rgba(255, 255, 255, 0)
  );
  animation: shimmer 2s infinite;
}

.skeleton-text {
  height: 1em;
  margin-bottom: 0.5em;
  background: #3a3a3a;
  border-radius: 4px;
}

.skeleton-text:last-child {
  margin-bottom: 0;
}

@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}

/* 스켈레톤 카드 내부 요소들의 너비 조정 */
.skeleton .bank-name-header .skeleton-text {
  width: 60%;
}

.skeleton .product-info .skeleton-text:nth-child(1) {
  width: 80%;
}

.skeleton .product-info .skeleton-text:nth-child(2) {
  width: 40%;
}

.skeleton .product-info .skeleton-text:nth-child(3) {
  width: 50%;
}
</style> 