<template>
    <div class="my-products-container">
        <h1 class="view-title">나의 가입 상품</h1>

        <section class="subscribed-list-section">
            <h2>가입한 상품 목록</h2>
            <div v-if="loading" class="loading-message">
                <p>상품 정보를 불러오는 중입니다...</p>
            </div>
            <div v-else-if="error" class="error-message">
                <p>{{ error }}</p>
            </div>
            <div v-else-if="subscribedProducts.length === 0" class="no-products-message">
                <p>가입한 금융 상품이 없습니다.</p>
            </div>
            <ul v-else class="product-list">
                <li v-for="(product, index) in subscribedProducts" :key="product.id || index" class="product-item">
                    <div class="product-info">
                        <span class="product-type">[{{ getProductType(product) }}]</span>
                        <span class="bank-name">{{ product.fin_co_no_nm }}</span> -
                        <span class="product-name">{{ product.fin_prdt_nm }}</span>
                    </div>
                    <div class="rates">
                        기본 금리: <span class="rate">{{ product.intr_rate?.toFixed(2) || '-' }}%</span>
                        <span v-if="product.intr_rate2 && product.intr_rate2 !== product.intr_rate"> | 최고 우대 금리: <span
                                class="rate special-rate">{{ product.intr_rate2?.toFixed(2) }}%</span></span>
                    </div>
                </li>
            </ul>
        </section>

        <section class="interest-rate-chart-section">
            <h2>가입 상품 금리 비교</h2>
            <div v-if="!loading && subscribedProducts.length > 0" class="chart-wrapper">
                <Bar :data="chartData" :options="chartOptions" />
            </div>
            <div v-else-if="!loading && subscribedProducts.length === 0" class="no-products-message">
                <p>차트를 표시할 상품이 없습니다.</p>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale
} from 'chart.js';
import axios from 'axios';
import { useAuthStore } from '@/stores/authStore';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const authStore = useAuthStore();
const subscribedProducts = ref([]);
const loading = ref(true);
const error = ref(null);

const fetchSubscribedProducts = async () => {
    loading.value = true;
    error.value = null;
    try {
        // TODO: 실제 API 엔드포인트로 교체해야 합니다.
        // 현재는 모든 예금과 적금 상품을 가져와서, 그 중 일부를 "가입한" 것으로 가정합니다.
        // 실제로는 /api/v1/products/my-subscriptions/ 와 같은 엔드포인트가 필요합니다.

        const depositRes = await axios.get('/api/v1/products/deposit-products/');
        const savingRes = await axios.get('/api/v1/products/saving-products/');

        let allProducts = [];
        if (depositRes.data && Array.isArray(depositRes.data)) {
            allProducts = allProducts.concat(depositRes.data.map(p => ({ ...p, type: 'deposit' })));
        }
        if (savingRes.data && Array.isArray(savingRes.data)) {
            allProducts = allProducts.concat(savingRes.data.map(p => ({ ...p, type: 'saving' })));
        }

        // 임시로 처음 5개 상품을 가입한 것으로 설정 (실제로는 사용자의 구독 정보에 따라 필터링)
        // 또한, API 응답에 따라 intr_rate, intr_rate2 필드가 숫자형인지 확인이 필요합니다.
        // subscribedProducts.value = allProducts.slice(0, 5);

        // 백엔드에 사용자가 가입한 상품 목록을 요청하는 API가 필요 (예: /api/v1/products/subscribed/)
        // 여기서는 임시로 전체 예금/적금 상품 중 사용자가 가입했다고 가정할 수 있는 상품을 표시합니다.
        // 실제 구현에서는 백엔드 API를 호출하여 사용자가 가입한 상품 목록을 받아와야 합니다.

        // 가정한 API 응답 (실제로는 백엔드에서 이 형태로 받아와야 함)
        const mockSubscribed = [
            // 예시: 사용자가 가입한 상품의 ID 또는 전체 객체 목록
            // 여기서는 전체 상품 중 일부를 임의로 선택 + type 추가
        ];

        // 사용자가 실제 가입한 예금 상품 가져오기 (DepositSubscription 모델 기반)
        const depositSubscriptionsRes = await axios.get(`/api/v1/products/deposit-subscriptions/my/`);
        const subscribedDepositProducts = depositSubscriptionsRes.data.map(sub => ({
            ...sub.deposit_option.product, // 상품 기본 정보
            fin_prdt_nm: sub.deposit_option.product.fin_prdt_nm, // 상품명
            fin_co_no_nm: sub.deposit_option.product.fin_co_no.kor_co_nm, // 은행명
            intr_rate: parseFloat(sub.deposit_option.intr_rate),
            intr_rate2: parseFloat(sub.deposit_option.intr_rate2),
            type: 'deposit'
        }));

        // 사용자가 실제 가입한 적금 상품 가져오기 (SavingSubscription 모델 기반)
        const savingSubscriptionsRes = await axios.get(`/api/v1/products/saving-subscriptions/my/`);
        const subscribedSavingProducts = savingSubscriptionsRes.data.map(sub => ({
            ...sub.saving_option.product, // 상품 기본 정보
            fin_prdt_nm: sub.saving_option.product.fin_prdt_nm, // 상품명
            fin_co_no_nm: sub.saving_option.product.fin_co_no.kor_co_nm, // 은행명 
            intr_rate: parseFloat(sub.saving_option.intr_rate),
            intr_rate2: parseFloat(sub.saving_option.intr_rate2),
            rsrv_type_nm: sub.saving_option.rsrv_type_nm, // 자유적립식 or 정액적립식
            type: 'saving'
        }));

        subscribedProducts.value = [...subscribedDepositProducts, ...subscribedSavingProducts];

        if (subscribedProducts.value.length === 0) {
            // error.value = '가입한 상품 정보를 찾을 수 없습니다.'; // 메시지를 다르게 표시할 수 있음
        }

    } catch (e) {
        console.error('가입 상품 정보 로딩 실패:', e);
        error.value = '상품 정보를 불러오는 중 오류가 발생했습니다.';
        if (e.response && e.response.status === 401 && authStore.isAuthenticated) {
            error.value = '상품 정보를 불러오려면 로그인이 필요합니다. 세션이 만료되었을 수 있습니다.'
        } else if (e.response && e.response.status === 404) {
            error.value = '가입한 상품 정보를 찾을 수 없습니다. (서버 응답 404)'
        }
    } finally {
        loading.value = false;
    }
};

const getProductType = (product) => {
    if (product.type === 'deposit') return '예금';
    if (product.type === 'saving') return '적금';
    return '기타';
};

onMounted(() => {
    if (authStore.isAuthenticated) {
        fetchSubscribedProducts();
    } else {
        loading.value = false;
        error.value = "상품 정보를 보려면 로그인이 필요합니다."
    }
});

const chartData = computed(() => {
    if (!subscribedProducts.value || subscribedProducts.value.length === 0) {
        return {
            labels: [],
            datasets: []
        };
    }
    return {
        labels: subscribedProducts.value.map(p => `${p.fin_co_no_nm} - ${p.fin_prdt_nm}`.substring(0, 20) + '...'), // 너무 길면 잘라내기
        datasets: [
            {
                label: '기본 금리 (%)',
                backgroundColor: '#42A5F5',
                borderColor: '#1E88E5',
                borderWidth: 1,
                data: subscribedProducts.value.map(p => p.intr_rate)
            },
            {
                label: '최고 우대 금리 (%)',
                backgroundColor: '#9CCC65',
                borderColor: '#7CB342',
                borderWidth: 1,
                data: subscribedProducts.value.map(p => p.intr_rate2 || p.intr_rate) // intr_rate2 없으면 intr_rate 사용
            }
        ]
    };
});

const chartOptions = ref({
    responsive: true,
    maintainAspectRatio: false,
    scales: {
        y: {
            beginAtZero: true,
            ticks: {
                callback: function (value) {
                    return value + '%';
                }
            },
            title: {
                display: true,
                text: '금리 (%)'
            }
        },
        x: {
            ticks: {
                autoSkip: false, // 모든 레이블 표시
                maxRotation: 70, // 레이블 회전 각도
                minRotation: 45  // 레이블 최소 회전 각도
            }
        }
    },
    plugins: {
        legend: {
            position: 'top',
        },
        title: {
            display: true,
            text: '가입 상품별 금리 비교'
        },
        tooltip: {
            callbacks: {
                label: function (context) {
                    let label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }
                    if (context.parsed.y !== null) {
                        label += context.parsed.y.toFixed(2) + '%';
                    }
                    return label;
                }
            }
        }
    }
});

</script>

<style scoped>
.my-products-container {
    padding: 30px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.view-title {
    font-size: 2rem;
    color: #333;
    margin-bottom: 30px;
    text-align: center;
    font-weight: 600;
}

section {
    background-color: #fff;
    padding: 25px;
    border-radius: 8px;
    margin-bottom: 30px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

section h2 {
    font-size: 1.5rem;
    color: #0064FF;
    /* 포인트 색상 */
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #0064FF;
    display: inline-block;
}

.loading-message,
.error-message,
.no-products-message {
    text-align: center;
    padding: 20px;
    color: #555;
    font-size: 1.1rem;
}

.error-message {
    color: #D32F2F;
    /* 에러 메시지 색상 */
}

.product-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.product-item {
    background-color: #f0f6ff;
    /* 밝은 파란색 계열 배경 */
    padding: 15px 20px;
    margin-bottom: 12px;
    border-radius: 6px;
    border-left: 5px solid #0064FF;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.product-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 100, 255, 0.15);
}

.product-info {
    font-size: 1.1rem;
    margin-bottom: 8px;
    color: #222;
}

.product-type {
    font-weight: 600;
    color: #0052cc;
    margin-right: 5px;
}

.bank-name {
    font-weight: 500;
}

.product-name {
    color: #191919;
    font-weight: bold;
}

.rates {
    font-size: 1rem;
    color: #444;
}

.rate {
    font-weight: bold;
    color: #007bff;
    /* 기본 금리 색상 */
}

.special-rate {
    color: #28a745;
    /* 우대 금리 색상 */
    background-color: #e6ffe6;
    /* 우대 금리 배경 하이라이트 */
    padding: 2px 5px;
    border-radius: 4px;
}

.chart-wrapper {
    height: 450px;
    /* 차트 높이 조절 */
    position: relative;
    /* 툴팁 등이 올바르게 표시되도록 */
}

/* 다크 모드 스타일은 src/assets/main.css 또는 App.vue에서 body.dark-mode 기준으로 관리 */
/* MyProductsView.vue에 특화된 다크모드 조정이 필요하다면 여기에 추가 */
body.dark-mode .my-products-container {
    background-color: #1e1e1e;
}

body.dark-mode .view-title {
    color: #f0f0f0;
}

body.dark-mode section {
    background-color: #2a2a2a;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

body.dark-mode section h2 {
    color: #0A84FF;
    border-bottom-color: #0A84FF;
}

body.dark-mode .loading-message,
body.dark-mode .error-message,
body.dark-mode .no-products-message {
    color: #bbb;
}

body.dark-mode .error-message {
    color: #ff8a80;
    /* 다크모드용 에러 색상 */
}

body.dark-mode .product-item {
    background-color: #303845;
    /* 어두운 파란색 계열 배경 */
    border-left-color: #0A84FF;
}

body.dark-mode .product-item:hover {
    box-shadow: 0 4px 10px rgba(10, 132, 255, 0.25);
}

body.dark-mode .product-info {
    color: #e0e0e0;
}

body.dark-mode .product-type {
    color: #4fc3f7;
    /* 밝은 파란색 */
}

body.dark-mode .product-name {
    color: #ffffff;
}

body.dark-mode .rates {
    color: #cccccc;
}

body.dark-mode .rate {
    color: #64B5F6;
    /* 다크모드 기본 금리 */
}

body.dark-mode .special-rate {
    color: #81C784;
    /* 다크모드 우대 금리 */
    background-color: #2e4b30;
    /* 다크모드 우대 금리 배경 */
}

/* 차트의 텍스트, 축 색상은 chartOptions에서 plugins.legend.labels.color, scales.y.ticks.color 등으로 설정 */
/* Chart.js는 캔버스에 직접 그리므로, CSS로 색상 변경이 제한적입니다. */
/* 스크립트 내 chartOptions에서 다크모드에 따른 색상 변경 로직 추가 필요 */
</style>