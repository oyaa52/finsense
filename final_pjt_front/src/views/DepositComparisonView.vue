<template>
  <div class="deposit-comparison">
    <!-- 상품 타입 토글 -->
    <div class="product-type-toggle">
      <button 
        :class="{ active: productType === 'deposit' }"
        @click="changeProductType('deposit')"
      >
        예금
      </button>
      <button 
        :class="{ active: productType === 'saving' }"
        @click="changeProductType('saving')"
      >
        적금
      </button>
    </div>

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
        <h2>상품 목록</h2>
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
const selectedBank = ref(null)
const selectedPeriod = ref('all')
const sortBy = ref('rate')
const selectedProduct = ref(null)
const products = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const totalPages = ref(1)
const pageSize = ref(50)
const productType = ref('deposit')  // 'deposit' 또는 'saving'

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
    const saveEndpoint = productType.value === 'deposit' 
      ? 'http://127.0.0.1:8000/api/v1/products/save-deposit-products/'
      : 'http://127.0.0.1:8000/api/v1/products/save-saving-products/'
    
    try {
      await axios.get(saveEndpoint)
    } catch (saveError) {
      console.warn('Failed to fetch latest data from API:', saveError)
      // 저장 실패해도 계속 진행
    }
    
    // 그 다음 저장된 상품 목록을 가져옴
    const listEndpoint = productType.value === 'deposit'
      ? 'http://127.0.0.1:8000/api/v1/products/deposit-products/'
      : 'http://127.0.0.1:8000/api/v1/products/saving-products/'
    
    const response = await axios.get(listEndpoint, {
      params: {
        page: page,
        page_size: pageSize.value,
        bank_id: selectedBank.value,
        period: selectedPeriod.value === 'all' ? undefined : selectedPeriod.value,
        sort_by: sortBy.value
      }
    })
    
    if (response.data.results && response.data.results.length > 0) {
      // 데이터 매핑
      products.value = response.data.results.map(product => {
        // 옵션 중에서 선택된 기간에 해당하는 옵션 찾기
        let selectedOption = null
        if (product.options && product.options.length > 0) {
          if (selectedPeriod.value === 'all') {
            // 전체 기간일 경우 가장 높은 금리의 옵션 선택
            selectedOption = product.options.reduce((max, option) => {
              const currentRate = parseFloat(option.intr_rate) || 0
              const maxRate = parseFloat(max.intr_rate) || 0
              return currentRate > maxRate ? option : max
            }, product.options[0])
          } else {
            // 특정 기간이 선택된 경우 해당 기간의 옵션 선택
            selectedOption = product.options.find(option => 
              option.save_trm === selectedPeriod.value
            ) || product.options[0]
          }
        }

        return {
          id: product.fin_prdt_cd,
          bankName: product.kor_co_nm,
          name: product.fin_prdt_nm,
          baseRate: selectedOption ? parseFloat(selectedOption.intr_rate) || 0 : 0,
          maxRate: selectedOption ? parseFloat(selectedOption.intr_rate2) || 0 : 0,
          period: selectedOption ? selectedOption.save_trm : '',
          minAmount: product.max_limit || 0,
          interestPayment: product.mtrt_int || '',
          description: product.spcl_cnd || '',
          features: [
            product.join_way,
            product.join_member,
            product.etc_note
          ].filter(Boolean),
          options: product.options || [] // 옵션 정보 저장
        }
      })

      // 금리순 정렬이 선택된 경우 금리 기준으로 정렬
      if (sortBy.value === 'rate') {
        products.value.sort((a, b) => b.baseRate - a.baseRate)
      }
      
      totalPages.value = response.data.total_pages
      currentPage.value = response.data.current_page
    } else {
      error.value = '상품 정보가 없습니다.'
    }
  } catch (err) {
    error.value = '상품 정보를 가져오는데 실패했습니다.'
    console.error('Error fetching products:', err)
  } finally {
    loading.value = false
  }
}

// 필터링된 상품 목록
const filteredProducts = computed(() => {
  if (selectedPeriod.value === 'all') {
    return products.value
  }

  // 선택된 기간에 해당하는 상품만 필터링
  return products.value.filter(product => {
    if (!product.options || product.options.length === 0) return false
    return product.options.some(option => option.save_trm === selectedPeriod.value)
  })
})

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

// 상품 타입 변경 시 데이터 다시 가져오기
const changeProductType = (type) => {
  productType.value = type
  currentPage.value = 1
  fetchProducts(1)
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

.product-type-toggle {
  display: flex;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.product-type-toggle button {
  padding: 0.75rem 2rem;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid #4a90e2;
  background: transparent;
  color: #4a90e2;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.product-type-toggle button.active {
  background: #4a90e2;
  color: white;
}

.product-type-toggle button:hover {
  background: #4a90e2;
  color: white;
  transform: translateY(-2px);
}

.filter-section {
  display: flex;
  gap: 30px;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
  border: 1px solid #4a90e2;
  background: transparent;
  color: #4a90e2;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.bank-buttons button.active {
  background-color: #4a90e2;
  color: #fff;
}

.period-filter select {
  width: 100%;
  padding: 8px;
  margin-top: 10px;
  background-color: #ffffff;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.products-section {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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
  border: 1px solid #ddd;
  background: transparent;
  color: #666;
  border-radius: 5px;
  cursor: pointer;
}

.sort-options button.active {
  background-color: #4a90e2;
  border-color: #4a90e2;
  color: #fff;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.bank-name-header {
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.bank-name-header h3 {
  color: #4a90e2;
  font-size: 1.2rem;
  margin: 0;
}

.product-title {
  font-size: 1.1rem;
  margin: 0 0 15px 0;
  color: #333;
  line-height: 1.4;
}

.product-card {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 20px;
  cursor: pointer;
  transition: transform 0.3s ease;
  border: 1px solid #eee;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(74, 144, 226, 0.1);
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
  color: #333;
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
  color: #666;
}

.rate-value {
  color: #4a90e2;
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
  background-color: #ffffff;
  border-radius: 10px;
  padding: 30px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: none;
  border: none;
  color: #666;
  font-size: 24px;
  cursor: pointer;
}

.detail-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.detail-header h2 {
  color: #333;
  margin: 0 0 10px 0;
  font-size: 1.8rem;
}

.detail-header .bank-name {
  color: #4a90e2;
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
  border-bottom: 1px solid #eee;
}

.info-row .label {
  color: #666;
}

.info-row .value {
  color: #333;
  font-weight: 500;
}

.detail-description, .detail-features {
  margin-top: 20px;
}

.detail-description h3, .detail-features h3 {
  color: #333;
  margin-bottom: 15px;
}

.detail-description p {
  color: #666;
  line-height: 1.6;
}

.detail-features ul {
  list-style: none;
  padding: 0;
}

.detail-features li {
  color: #666;
  margin-bottom: 10px;
  padding-left: 20px;
  position: relative;
}

.detail-features li::before {
  content: "•";
  color: #4a90e2;
  position: absolute;
  left: 0;
}

/* 로딩 및 에러 상태 스타일 추가 */
.loading-state, .error-state {
  text-align: center;
  padding: 40px;
  background-color: #ffffff;
  border-radius: 10px;
  margin-bottom: 20px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.loading-animation {
  margin-bottom: 20px;
}

.loader {
  width: 48px;
  height: 48px;
  border: 3px solid #4a90e2;
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
  background: linear-gradient(45deg, #4a90e2, #00BFFF);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-weight: 500;
}

.error-state p {
  color: #e74c3c;
  font-size: 1.2rem;
  margin-bottom: 20px;
}

.error-state button {
  padding: 10px 20px;
  background: #4a90e2;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.error-state button:hover {
  transform: translateY(-2px);
  background: #357abd;
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
  border: 1px solid #4a90e2;
  background-color: transparent;
  color: #4a90e2;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-button:hover:not(:disabled) {
  background-color: #4a90e2;
  color: white;
}

.page-button.active {
  background-color: #4a90e2;
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
  background: #f0f0f0;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
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
    rgba(255, 255, 255, 0.2) 20%,
    rgba(255, 255, 255, 0.5) 60%,
    rgba(255, 255, 255, 0)
  );
  animation: shimmer 1.5s infinite;
}

.skeleton-text {
  height: 1em;
  margin-bottom: 0.8em;
  background: #e0e0e0;
  border-radius: 4px;
  position: relative;
  overflow: hidden;
}

.skeleton-text:last-child {
  margin-bottom: 0;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  50% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 스켈레톤 카드 내부 요소들의 너비 조정 */
.skeleton .bank-name-header .skeleton-text {
  width: 60%;
  height: 1.5em;
  margin-bottom: 1em;
}

.skeleton .product-info .skeleton-text:nth-child(1) {
  width: 80%;
  height: 1.8em;
  margin-bottom: 1em;
}

.skeleton .product-info .skeleton-text:nth-child(2) {
  width: 40%;
  height: 1.2em;
  margin-bottom: 0.8em;
}

.skeleton .product-info .skeleton-text:nth-child(3) {
  width: 50%;
  height: 1.2em;
  margin-bottom: 0.8em;
}

/* 스켈레톤 카드 호버 효과 */
.skeleton:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
</style> 