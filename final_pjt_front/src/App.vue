<template>
    <h1>Hello!</h1>
    <p>Lorem ipsum dolor sit amet consectetur, adipisicing elit. Est earum perspiciatis ullam tempora voluptas quis aliquid quisquam! Ipsa corrupti, unde nam perspiciatis impedit vero eligendi assumenda doloribus rerum blanditiis maxime!</p>
    <p v-for="i in 30" :key="i">Dummy content {{ i }}</p>
    <div data-aos="fade-in">
        <img src="@/assets/travel.png" alt="travel">
    </div>

</template>

<script setup>
// <script setup>
import { onMounted } from 'vue'
import AOS from 'aos'

onMounted(() => {
  AOS.refresh() // 새로 로드된 요소에 적용
})
</script>

<style scoped>

</style>