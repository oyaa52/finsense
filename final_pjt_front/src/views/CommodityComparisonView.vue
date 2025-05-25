<template>
  <div class="commodity-comparison-container" data-aos="fade-up">
    <h2 class="view-title">현물 상품 비교</h2>
    <div class="controls-container">
      <div class="asset-selector">
        <button 
          @click="selectAsset('gold')" 
          :class="{ 'active': selectedAsset === 'gold' }"
          class="asset-button gold-button"
        >
          금 (Gold)
        </button>
        <button 
          @click="selectAsset('silver')" 
          :class="{ 'active': selectedAsset === 'silver' }"
          class="asset-button silver-button"
        >
          은 (Silver)
        </button>
      </div>
      <div class="date-selector">
        <div class="date-input-group">
          <label for="start-date">시작일:</label>
          <input type="date" id="start-date" v-model="startDate" class="date-input">
        </div>
        <div class="date-input-group">
          <label for="end-date">종료일:</label>
          <input type="date" id="end-date" v-model="endDate" class="date-input">
        </div>
        <button @click="fetchAssetPrices" class="fetch-button">조회</button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-indicator">
      <p>데이터를 불러오는 중입니다...</p>
    </div>
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>

    <div class="chart-container" v-show="chartData.labels && chartData.labels.length > 0 && !isLoading && !errorMessage">
      <Line :data="chartData" :options="chartOptions" ref="lineChart" :key="chartKey" />
    </div>
     <div v-if="!isLoading && !errorMessage && chartData.labels && chartData.labels.length === 0 && searchAttempted" class="no-data-message">
      <p>선택하신 조건에 해당하는 데이터가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch, nextTick } from 'vue';
import axios from 'axios';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale, Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';
import AOS from 'aos';
import 'aos/dist/aos.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, TimeScale, Filler);

const lineChart = ref(null);
const chartKey = ref(0);
const selectedAsset = ref('gold');
const startDate = ref('');
const endDate = ref('');
const chartData = reactive({ // 백엔드가 Chart.js 형식을 반환하므로, 초기 구조는 간단하게
  labels: [],
  datasets: []
});
const isLoading = ref(false);
const errorMessage = ref(null);
const searchAttempted = ref(false);

const chartOptions = reactive({
  responsive: true,
  maintainAspectRatio: false,
  scales: {
    x: {
      type: 'time',
      time: {
        unit: 'day',
        tooltipFormat: 'yyyy-MM-dd',
        displayFormats: { day: 'yyyy-MM-dd' }
      },
      title: { display: true, text: '날짜' }
    },
    y: {
      title: { display: true, text: '가격' },
      ticks: { callback: value => value.toLocaleString() }
    }
  },
  plugins: {
    legend: { display: true, position: 'top' },
    title: { display: true, text: '가격 변동 추이' }, // 동적으로 업데이트됨
    tooltip: {
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || '';
          if (label) label += ': ';
          if (context.parsed.y !== null) label += context.parsed.y.toLocaleString();
          return label;
        }
      }
    }
  }
});

// AssetPriceListAPIView를 사용하고, 파라미터는 asset_name, start_date, end_date
const API_BASE_URL = 'http://127.0.0.1:8000/api/v1/assetinfo/list-prices/';


const fetchAssetPrices = async () => {
  isLoading.value = true;
  errorMessage.value = null;
  searchAttempted.value = true;

  if (!selectedAsset.value) {
    errorMessage.value = '자산(금 또는 은)을 선택해주세요.';
    isLoading.value = false;
    clearChartDataAndSetDefault();
    return;
  }
  
  if (startDate.value && endDate.value && startDate.value > endDate.value) {
    errorMessage.value = '시작일은 종료일보다 이전 날짜여야 합니다.';
    isLoading.value = false;
    clearChartDataAndSetDefault();
    return;
  }

  try {
    const params = { asset_name: selectedAsset.value }; 
    if (startDate.value) params.start_date = startDate.value;
    if (endDate.value) params.end_date = endDate.value;

    const response = await axios.get(API_BASE_URL, { params });
    console.log('API Response Data:', response.data);
    
    if (response.data && Array.isArray(response.data)) {
      if (response.data.length === 0) {
        chartData.labels = [];
        chartData.datasets = [];
      } else {
        chartData.labels = response.data.map(item => item.date);
        const assetNameDisplay = selectedAsset.value === 'gold' ? '금' : '은';
        const color = selectedAsset.value === 'gold' ? 'rgb(255, 215, 0)' : 'rgb(192, 192, 192)';
        const bgColor = selectedAsset.value === 'gold' ? 'rgba(255, 215, 0, 0.1)' : 'rgba(192, 192, 192, 0.1)';

        chartData.datasets = [{
          label: `${assetNameDisplay} 가격`,
          data: response.data.map(item => parseFloat(item.price)),
          borderColor: color,
          backgroundColor: bgColor,
          tension: 0.1,
          fill: true
        }];
      }
    } else {
      clearChartDataAndSetDefault();
      errorMessage.value = '데이터를 불러오는 데 실패했습니다. 응답 형식을 확인해주세요.';
    }

  } catch (error) {
    console.error('Error fetching asset prices:', error);
    if (error.response && error.response.data && error.response.data.error) {
      errorMessage.value = error.response.data.error;
    } else {
      errorMessage.value = '데이터를 불러오는 중 오류가 발생했습니다.';
    }
    clearChartDataAndSetDefault();
  }
  chartKey.value++;
  updateChartTitle();
  isLoading.value = false;

  // DOM 업데이트 후 차트 업데이트 시도
  await nextTick(); 
  if (lineChart.value && lineChart.value.chart) {
    console.log("Chart Instance Data (after fetch):", lineChart.value.chart.data);
    console.log("Chart Instance Options (after fetch):", lineChart.value.chart.options);
  } else {
    console.log("Chart instance not found for update (after fetch)", lineChart.value);
  }
};

const selectAsset = (asset) => {
  selectedAsset.value = asset;
  fetchAssetPrices(); // 자산 변경 시 바로 데이터 조회
};

const updateChartTitle = () => {
  const assetNameDisplay = selectedAsset.value === 'gold' ? '금' : (selectedAsset.value === 'silver' ? '은' : '');
  chartOptions.plugins.title.text = `${assetNameDisplay} 가격 변동 추이`;
};

const clearChartDataAndSetDefault = () => {
  chartData.labels = [];
  chartData.datasets = [];
  updateChartTitle();
  chartKey.value++;
};

// chartData의 datasets를 감시하여 변경이 감지되면 차트를 업데이트
watch(() => chartData.datasets, (newDatasets, oldDatasets) => {
  if (lineChart.value && lineChart.value.chart && newDatasets && newDatasets.length > 0) {
    console.log("Datasets changed via watch, updating chart:", newDatasets);
    lineChart.value.chart.update();
  } else if (newDatasets && newDatasets.length === 0) {
    console.log("Datasets cleared via watch, chart should be empty or updated.");
    if (lineChart.value && lineChart.value.chart) {
        lineChart.value.chart.update();
    }
  }
}, { deep: true });

watch([startDate, endDate], () => {
    // 날짜 변경 시 자동으로 조회하지 않고, 사용자가 조회 버튼을 누르도록 함.
    // 필요시 여기서 fetchAssetPrices() 호출 가능
});

onMounted(() => {
  AOS.init();
  fetchAssetPrices(); // 컴포넌트 마운트 시 기본 선택(금)으로 데이터 조회
});

</script>

<style scoped>
.commodity-comparison-container {
  padding: 20px;
  background-color: #ffffff;
  color: #333333;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.view-title {
  font-size: 1.8rem;
  font-weight: 600;
  color: #4a90e2;
  margin-bottom: 25px;
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 15px;
}

.controls-container {
  display: flex;
  flex-wrap: wrap; /* 작은 화면에서 줄바꿈 허용 */
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px; /* 컨트롤 그룹 간 간격 */
  background-color: #f8f9fa; /* 배경색 추가 */
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.asset-selector {
  display: flex;
  gap: 10px;
}

.asset-button {
  padding: 10px 20px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #e9ecef;
  color: #495057;
}

.asset-button.gold-button.active {
  background-color: #FFD700; /* 금색 */
  color: #423000;
  border-color: #e6c300;
  box-shadow: 0 0 8px rgba(255, 215, 0, 0.5);
}

.asset-button.silver-button.active {
  background-color: #C0C0C0; /* 은색 */
  color: #36454F;
  border-color: #adb5bd;
  box-shadow: 0 0 8px rgba(192, 192, 192, 0.5);
}

.asset-button:not(.active):hover {
  background-color: #dee2e6;
  border-color: #ced4da;
}

.date-selector {
  display: flex;
  align-items: center;
  gap: 15px; /* 요소들 사이 간격 */
  flex-wrap: wrap; /* 작은 화면에서 줄바꿈 */
}

.date-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-input-group label {
  font-size: 0.9rem;
  color: #495057;
}

.date-input {
  padding: 8px 10px;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 0.9rem;
  background-color: #fff;
}

.fetch-button {
  padding: 10px 20px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.fetch-button:hover {
  background-color: #357abd;
}

.loading-indicator,
.error-message,
.no-data-message {
  text-align: center;
  padding: 20px;
  margin-top: 20px;
  border-radius: 6px;
}

.loading-indicator p {
  color: #666666;
  font-size: 1.1rem;
}

.error-message {
  background-color: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.no-data-message {
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

.chart-container {
  flex-grow: 1; /* 남은 공간을 모두 차지하도록 */
  width: 100%;
  min-height: 400px; /* 최소 높이 설정 */
  position: relative; /* 내부 차트의 position 기준 */
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-top: 20px;
}

/* AOS Animations */
[data-aos] {
  transition-property: transform, opacity;
}
</style> 