<template>
    <div class="admin-panel-container">
        <iframe :src="adminUrl" frameborder="0" class="admin-iframe"></iframe>
    </div>
</template>

<script setup>
import { ref } from 'vue';

// Django admin URL - Vite 프록시를 통해 /admin/ 경로를 직접 사용합니다.
const adminUrl = ref('/admin/');
</script>

<style scoped>
.admin-panel-container {
    width: 100%;
    height: calc(100vh - 70px);
    /* 상단 네비게이션 바 높이(70px)를 제외한 전체 높이 */
    overflow: hidden;
    /* 스크롤바는 iframe 내부에서 처리 */
}

.admin-iframe {
    width: 100%;
    height: 100%;
    border: none;
    /* iframe 테두리 제거 */
}
</style>