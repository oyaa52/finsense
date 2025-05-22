<template>
  <div class="landing-container">
    <!-- Hero 섹션 -->
    <section class="hero-section" data-aos="fade-up">
      <div class="hero-content">
        <h1>당신의 금융 라이프에 가장 가까운 길잡이</h1>
        <p>Fin Sense</p>
      </div>
    </section>

    <section class="image-section">
      <div class="image-container">
        <div class="image-wrapper">
          <img src="@/assets/travel.png" alt="travel" class="scroll-reveal-image" width="100%" :style="{ clipPath: `inset(0 ${20 - scrollProgress * 20}% 0 ${20 - scrollProgress * 20}%)` }" />
        </div>
      </div>
    </section>

    <!-- 여행 자금 섹션 -->
    <section class="service-section" data-aos="fade-up">
      <div class="service-content">
        <h2>지금 당신 손의 10만원, 내년엔 해외여행도 꿈이 아닙니다</h2>
        <p>친구들과의 여행, 비용이 고민되시나요? 기간과 금액을 입력하면, 맞춤형 여행 자금 금융 상품을 딱 맞게 추천해드립니다.</p>
      </div>
    </section>

    <!-- 주거 금융 섹션 -->
    <section class="transfer-section" data-aos="fade-up">
      <div class="transfer-content">
        <h2>자가 마련을 꿈꾸는 당신, 적금만으로 괜찮을까 고민되시죠?</h2>
        <p>Fin Sense는 당신의 소득과 지출 패턴에 맞는 주거금융 상품을 자동 분석해 추천해드립니다.</p>
      </div>
    </section>

    <!-- 자동차 금융 섹션 -->
    <section class="loan-section" data-aos="fade-up">
      <div class="loan-content">
        <h2>자동차 바꾸고 싶은데, 대출이 걱정된다면?</h2>
        <p>지금 보고 있는 그 차, Fin Sense와 함께라면 가능성은 더 커집니다.</p>
      </div>
    </section>

    <!-- 금융 상품 비교 섹션 -->
    <section class="compare-section" data-aos="fade-up">
      <div class="compare-content">
        <h2>여러 은행 조건, 일일이 비교하지 마세요</h2>
        <p>Fin Sense가 10초 만에 당신에게 꼭 맞는 조건만 골라드립니다.</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import AOS from 'aos'
import 'aos/dist/aos.css'

const scrollProgress = ref(0)

onMounted(() => {
  AOS.init({
    duration: 1000,
    once: false,
    offset: 100
  })
  AOS.refresh()

  const handleScroll = () => {
    const imageSection = document.querySelector('.image-section')
    if (!imageSection) return

    const rect = imageSection.getBoundingClientRect()
    const windowHeight = window.innerHeight
    const sectionTop = rect.top
    const sectionHeight = rect.height

    // 섹션이 화면에 들어오기 시작할 때부터 완전히 지나갈 때까지의 진행도 계산
    const progress = Math.min(
      Math.max(
        (windowHeight - sectionTop) / (windowHeight + sectionHeight),
        0
      ),
      1
    )

    // 이미지가 중앙에 오기 전에 이미 다 펼쳐지도록 조정
    scrollProgress.value = Math.min(progress * 2, 1)
  }

  window.addEventListener('scroll', handleScroll)
  handleScroll() // 초기 로드 시에도 실행
})
</script>

<style scoped>
.landing-container {
  width: 100%;
  min-height: 1277px;
  background-color: #ffffff;
}

section {
  width: 100%;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
}

.hero-section {
  background-color: #0064FF;
  color: white;
}

.service-section {
  background-color: #f5f5f5;
  color: #191919;
}

.transfer-section {
  background-color: white;
  color: #191919;
}

.loan-section {
  background-color: #f5f5f5;
  color: #191919;
}

.compare-section {
  background-color: white;
  color: #191919;
}

.image-section {
  background-color: #f5f5f5;
  color: #191919;
  position: relative;
  overflow: hidden;
}

.hero-content,
.service-content,
.transfer-content,
.loan-content,
.compare-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
}

h1 {
  font-size: 4rem;
  font-weight: 700;
  margin-bottom: 20px;
}

h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 20px;
}

p {
  font-size: 1.2rem;
  line-height: 1.6;
}

.image-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-wrapper {
  width: 100%;
  max-width: 800px;
  position: relative;
  overflow: hidden;
}

.scroll-reveal-image {
  width: 100%;
  height: auto;
  display: block;
  transform-origin: center;
  transition: clip-path 0.1s ease-out;
}

.image-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to right, #f5f5f5 0%, transparent 50%, #f5f5f5 100%);
  opacity: 0.8;
  pointer-events: none;
}
</style>