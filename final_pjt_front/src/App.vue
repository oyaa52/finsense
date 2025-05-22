<template>
  <h1>Hello!</h1>
  <p>Lorem ipsum dolor sit amet consectetur, adipisicing elit. Est earum perspiciatis ullam tempora voluptas quis
    aliquid quisquam! Ipsa corrupti, unde nam perspiciatis impedit vero eligendi assumenda doloribus rerum blanditiis
    maxime!</p>
  <p v-for="i in 30" :key="i">Dummy content {{ i }}</p>
  <div data-aos="fade-in" data-aos-once="false">
    <img src="@/assets/travel.png" alt="travel" style="max-width: 100%; height: auto;">
  </div>

</template>

<script setup>
import { onMounted } from 'vue'
import AOS from 'aos'
import 'aos/dist/aos.css'  // AOS 스타일시트 import

onMounted(() => {
  AOS.init({
    duration: 3000,
    once: true
  })
  AOS.refresh()
})
</script>

<style scoped>
img {
  display: block;
  margin: 20px auto;
}
</style>