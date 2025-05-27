import { defineStore } from 'pinia';

export const useAlertStore = defineStore('alert', {
    state: () => ({
        isVisible: false,
        title: '',
        message: '',
        type: 'info', // 'info', 'success', 'warning', 'error'
        confirmCallback: null, // 확인 버튼 클릭 시 실행될 콜백
        closeCallback: null,   // 닫기 버튼 클릭 시 실행될 콜백
    }),
    actions: {
        openAlert({ title = '알림', message, type = 'info', onConfirm = null, onClose = null }) {
            this.title = title;
            this.message = message;
            this.type = type;
            this.confirmCallback = onConfirm;
            this.closeCallback = onClose;
            this.isVisible = true;
        },
        closeAlert() {
            if (this.closeCallback) {
                this.closeCallback();
            }
            this.resetAlert();
        },
        confirmAlert() {
            if (this.confirmCallback) {
                this.confirmCallback();
            }
            this.resetAlert();
        },
        resetAlert() {
            this.isVisible = false;
            this.title = '';
            this.message = '';
            this.type = 'info';
            this.confirmCallback = null;
            this.closeCallback = null;
        }
    },
}); 