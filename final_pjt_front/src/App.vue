<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue'
import AOS from 'aos'
import 'aos/dist/aos.css'

onMounted(() => {
  // 메인 App 컴포넌트가 마운트될 때 AOS 라이브러리를 초기화
  // => data-aos 속성을 사용하는 모든 컴포넌트에서 AOS 효과를 전역적으로 사용할 수 있음
  AOS.init({
    duration: 1000, // 애니메이션 지속 시간 (단위 : ms)
    once: false,    // 애니메이션이 한 번만 실행되어야 하는지 여부 (스크롤 내릴 때)
    offset: 100     // 원래 트리거 지점에서의 오프셋 (픽셀 단위)
  })
})
</script>

<style>
/* 전역 스타일 */
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}

*, *::before, *::after {
  box-sizing: inherit;
}

</style>