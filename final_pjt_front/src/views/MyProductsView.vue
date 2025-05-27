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
        const response = await axios.get('/api/v1/products/subscriptions/');

        const deposits = response.data.deposit_subscriptions || [];
        const savings = response.data.saving_subscriptions || [];

        const subscribedDepositProducts = deposits.map(sub => ({
            id: sub.id,
            fin_prdt_nm: sub.product_name,
            fin_co_no_nm: sub.bank_name,
            intr_rate: parseFloat(sub.interest_rate),
            intr_rate2: parseFloat(sub.interest_rate2),
            type: sub.product_type, // 'deposit'
            period: sub.period,
            subscribed_at: sub.subscribed_at
        }));

        const subscribedSavingProducts = savings.map(sub => ({
            id: sub.id,
            fin_prdt_nm: sub.product_name,
            fin_co_no_nm: sub.bank_name,
            intr_rate: parseFloat(sub.interest_rate),
            intr_rate2: parseFloat(sub.interest_rate2),
            type: sub.product_type, // 'saving'
            rsrv_type_nm: sub.rsrv_type_nm,
            period: sub.period,
            subscribed_at: sub.subscribed_at
        }));

        subscribedProducts.value = [...subscribedDepositProducts, ...subscribedSavingProducts];

        if (subscribedProducts.value.length === 0) {
            // 가입한 상품이 없을 때의 메시지 처리 (현재 UI에 이미 있음)
        }

    } catch (e) {
        console.error('가입 상품 정보 로딩 실패:', e);
        error.value = '상품 정보를 불러오는 중 오류가 발생했습니다.';
        if (e.response && e.response.status === 401 && authStore.isAuthenticated) {
            error.value = '상품 정보를 불러오려면 로그인이 필요합니다. 세션이 만료되었을 수 있습니다.'
        } else if (e.response && e.response.status === 404) {
            error.value = '가입한 상품 정보를 찾을 수 없습니다. (API 경로 또는 서버 응답 확인 필요)'
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

    const products = subscribedProducts.value;
    let sumIntrRate = 0;
    let countForIntrRate = 0;
    let sumIntrRate2 = 0;
    let countForIntrRate2 = 0;

    products.forEach(p => {
        // 기본 금리 합산 (intr_rate)
        if (typeof p.intr_rate === 'number' && !isNaN(p.intr_rate)) {
            sumIntrRate += p.intr_rate;
            countForIntrRate++;
        }

        // 최고 우대 금리 합산 (intr_rate2, 없으면 intr_rate로 대체)
        let rateForAvg2 = null;
        if (typeof p.intr_rate2 === 'number' && !isNaN(p.intr_rate2)) {
            rateForAvg2 = p.intr_rate2;
        } else if (typeof p.intr_rate === 'number' && !isNaN(p.intr_rate)) {
            rateForAvg2 = p.intr_rate; // intr_rate2가 유효하지 않으면 intr_rate를 사용
        }

        if (rateForAvg2 !== null) {
            sumIntrRate2 += rateForAvg2;
            countForIntrRate2++;
        }
    });

    const avgIntrRate = countForIntrRate > 0 ? parseFloat((sumIntrRate / countForIntrRate).toFixed(2)) : 0;
    const avgIntrRate2 = countForIntrRate2 > 0 ? parseFloat((sumIntrRate2 / countForIntrRate2).toFixed(2)) : 0;

    const chartLabels = ['전체 평균', ...products.map(p => `${p.fin_prdt_nm}`.substring(0, 30))];

    const intrRateData = [avgIntrRate, ...products.map(p => (typeof p.intr_rate === 'number' && !isNaN(p.intr_rate) ? p.intr_rate : null))];
    // 개별 상품의 최고 우대 금리는 intr_rate2가 유효할 때만 사용, 아니면 전체 평균 intr_rate2를 사용
    const intrRate2Data = [avgIntrRate2, ...products.map(p => {
        if (typeof p.intr_rate2 === 'number' && !isNaN(p.intr_rate2)) {
            return p.intr_rate2;
        }
        return avgIntrRate2; // intr_rate2가 없거나 유효하지 않으면 전체 평균 intr_rate2 사용
    })];

    return {
        labels: chartLabels,
        datasets: [
            {
                label: '저축 금리',
                backgroundColor: '#42A5F5',
                borderColor: '#1E88E5',
                borderWidth: 1,
                data: intrRateData
            },
            {
                label: '최고 우대 금리',
                backgroundColor: '#9CCC65',
                borderColor: '#7CB342',
                borderWidth: 1,
                data: intrRate2Data
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

</style>