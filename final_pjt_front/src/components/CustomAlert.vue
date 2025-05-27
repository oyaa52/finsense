<template>
  <div v-if="localVisible" class="custom-alert-backdrop" @click.self="handleClose">
    <div class="custom-alert-box" :class="`alert-${type}`">
      <div class="alert-header">
        <i :class="iconClass" class="alert-icon"></i>
        <h3 class="alert-title">{{ title }}</h3>
        <button class="close-button" @click="handleClose">&times;</button>
      </div>
      <div class="alert-body">
        <p>{{ message }}</p>
      </div>
      <div class="alert-footer">
        <button v-if="showConfirmButton" class="btn btn-confirm" @click="handleConfirm">확인</button>
        <button class="btn btn-close" @click="handleClose">{{ showConfirmButton ? '취소' : '닫기' }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, defineProps, defineEmits } from 'vue';

const props = defineProps({
  title: {
    type: String,
    default: '알림'
  },
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    default: 'info' // info, success, warning, error
  },
  visible: {
    type: Boolean, // App.vue에서 v-if로 제어하므로, 직접적인 prop 'visible'은 제거 가능
    default: true  // 또는 alertStore.isVisible을 직접 참조하도록 App.vue에서 이미 처리함
  },
  showConfirmButton: {
    type: Boolean,
    default: false // 기본값은 false (확인 버튼 숨김)
  }
});

const emit = defineEmits(['confirm', 'close']);

// App.vue에서 v-if로 렌더링을 제어하므로, 내부 localVisible 상태는 불필요해짐.
// 만약 애니메이션 등을 위해 내부 상태가 필요하다면 유지할 수 있으나, 여기서는 단순화.
const localVisible = ref(props.visible); 
watch(() => props.visible, (newValue) => {
  localVisible.value = newValue;
});

const iconClass = computed(() => {
  switch (props.type) {
    case 'success': return 'fas fa-check-circle';
    case 'warning': return 'fas fa-exclamation-triangle';
    case 'error': return 'fas fa-times-circle';
    case 'info':
    default: return 'fas fa-info-circle';
  }
});

const handleConfirm = () => {
  emit('confirm');
};

const handleClose = () => {
  emit('close');
};
</script>

<style scoped>
/* 기존 CustomAlert.vue 스타일 유지 */
.custom-alert-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
}

.custom-alert-box {
  background-color: #fff;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  width: 90%;
  max-width: 420px;
  text-align: center;
  border-top: 5px solid;
  animation: slideDown 0.4s ease-out forwards;
}

@keyframes slideDown {
  from {
    transform: translateY(-50px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.alert-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  position: relative; /* For close button positioning */
}

.alert-icon {
  font-size: 28px;
  margin-right: 15px;
}

.alert-title {
  font-size: 1.4em;
  font-weight: 600;
  margin: 0;
  text-align: left;
}

.close-button {
  position: absolute;
  top: -15px; /* Header padding 감안 */
  right: -10px; /* Header padding 감안 */
  background: none;
  border: none;
  font-size: 28px;
  font-weight: bold;
  color: #aaa;
  cursor: pointer;
  padding: 5px;
  line-height: 1;
}
.close-button:hover {
  color: #777;
}

.alert-body p {
  font-size: 1.05em;
  color: #555;
  margin-top: 0;
  margin-bottom: 20px;
  text-align: left;
  word-break: keep-all; /* 단어 단위 줄바꿈 */
}

.alert-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, box-shadow 0.2s ease;
  font-size: 0.95em;
}

.btn-confirm {
  background-color: #007bff;
  color: white;
}
.btn-confirm:hover {
  background-color: #0056b3;
  box-shadow: 0 2px 5px rgba(0,123,255,0.3);
}

.btn-close {
  background-color: #6c757d;
  color: white;
}
.btn-close:hover {
  background-color: #545b62;
  box-shadow: 0 2px 5px rgba(108,117,125,0.3);
}

/* Type-specific styling */
.alert-info .alert-icon, .alert-info .alert-title {
  color: #007bff;
}
.alert-info {
  border-top-color: #007bff;
}

.alert-success .alert-icon, .alert-success .alert-title {
  color: #28a745;
}
.alert-success {
  border-top-color: #28a745;
}

.alert-warning .alert-icon, .alert-warning .alert-title {
  color: #ffc107;
}
.alert-warning {
  border-top-color: #ffc107;
}

.alert-error .alert-icon, .alert-error .alert-title {
  color: #dc3545;
}
.alert-error {
  border-top-color: #dc3545;
}
</style>