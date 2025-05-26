<template>
  <div class="landing-container">
    <!--  Logo Section -->
    <section class="logo-section" data-aos="fade-up">
      <div class="logo-content">
        <img src="@/assets/FS_logo.png" alt="Fin Sense Logo" class="logo-image" />
        <h2>Finance에 감각을 더하다, Fin Sense.</h2>
        <p>당신만을 위한 금융 인사이트, 지금 깨워보세요.</p>
        <router-link to="/main" class="cta-button">바로 가기</router-link>
      </div>
    </section>

    <section class="image-section" data-aos="fade-up">
      <div class="image-container">
        <div class="image-wrapper">
          <img src="@/assets/travel.png" alt="travel" class="scroll-reveal-image" width="100%"
            :style="{ clipPath: `inset(0 ${20 - scrollProgress * 20}% 0 ${20 - scrollProgress * 20}%)` }" />
        </div>
      </div>

      <!-- 여행 자금 섹션 내용 통합 -->
      <div class="service-content integrated-service-content">
        <h2>지금 당신 손의 10만원,<br>
          내년엔 해외여행도 꿈이 아닙니다</h2><br>
        <p>친구들과의 여행, 비용이 고민되시나요? 기간과 금액을 입력하면,<br />
          맞춤형 여행 자금 금융 상품을 딱 맞게 추천해드립니다.</p>
      </div>
    </section>

    <!-- 주거 금융 섹션 -->
    <section class="transfer-section" data-aos="fade-up">
      <div class="transfer-content">
        <img src="@/assets/house.png" alt="House Image" class="section-image" data-aos="zoom-in"
          data-aos-duration="800" />
        <h2>자가 마련을 꿈꾸는 당신, 아무 적금을 드는 것만으로 괜찮을까 고민되시죠?</h2>
        <p>Fin Sense는 당신의 소득과 지출 패턴에 맞는 주거금융 상품을 자동 분석해 추천해드립니다.</p>
      </div>
    </section>

    <!-- 자동차 금융 섹션 -->
    <section class="loan-section" data-aos="fade-up">
      <div class="loan-content">
        <img src="@/assets/car.png" alt="Car Image" class="section-image" data-aos="zoom-in" data-aos-duration="800" />
        <h2>자동차 바꾸고 싶은데, 대출이 걱정된다면?</h2>
        <p>지금 보고 있는 그 차, Fin Sense와 함께라면 가능성은 더 커집니다.</p>
      </div>
    </section>

    <!-- Hero 섹션  -->
    <section class="hero-section">
      <div class="hero-content">
        <h2 data-aos="fade-down">여러 은행 조건, 일일이 비교하지 마세요</h2>
        <p data-aos="fade-down" data-aos-delay="200">Fin Sense가 10초 만에 당신에게 꼭 맞는 조건만 골라드립니다.</p>

        <div style="margin-top: 50px;">
          <h1 data-aos="fade-up" data-aos-delay="400">당신의 금융 라이프에 가장 가까운 길잡이</h1>
          <p data-aos="fade-up" data-aos-delay="600">Fin Sense</p>
        </div>
      </div>
    </section>
  </div>

  <!-- Scroll to Top Button -->
  <button v-if="showScrollTopButton" @click="scrollToTop" class="scroll-top-btn">
  </button>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

const scrollProgress = ref(0)
const showScrollTopButton = ref(false)

const handleScroll = () => {
  const imageSection = document.querySelector('.image-section')
  if (imageSection) {
    const rect = imageSection.getBoundingClientRect()
    const windowHeight = window.innerHeight
    const sectionTop = rect.top
    const sectionHeight = rect.height

    const progress = Math.min(
      Math.max(
        (windowHeight - sectionTop) / (windowHeight + sectionHeight),
        0
      ),
      1
    )
    scrollProgress.value = Math.min(progress * 2, 1)
  }

  if (window.scrollY > 300) {
    showScrollTopButton.value = true;
  } else {
    showScrollTopButton.value = false;
  }
}

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.landing-container {
  width: 100%;
  min-height: 1277px;
  background-color: #ffffff;
}

/* New Logo Section  */
.logo-section {
  background-color: #ffffff;
  color: #191919;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 80vh;
}

.logo-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.logo-image {
  max-width: 200px;
  margin-bottom: 30px;
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
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
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.service-content,
.transfer-content,
.loan-content,
.compare-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
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

.section-image {
  max-width: 500px;
  height: auto;
  margin-bottom: 20px;
  display: block;
  margin-left: auto;
  margin-right: auto;
}

.cta-button {
  display: inline-block;
  margin-top: 25px;
  padding: 12px 25px;
  background-color: #0064FF;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: bold;
  font-size: 1.1rem;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.cta-button:hover {
  background-color: #0052cc;
  transform: translateY(-2px);
}

.integrated-service-content {
  padding-top: 40px;
  color: #191919;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

/* Scroll to Top Button Styles */
.scroll-top-btn {
  position: fixed;
  bottom: 25px;
  right: 25px;
  background-color: #ffffff;
  color: #0064FF;
  border: none !important;
  border-radius: 50%;
  width: 45px;
  height: 45px;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, color 0.3s ease, opacity 0.3s ease, transform 0.3s ease;
  opacity: 0;
  transform: translateY(20px);
  z-index: 1000;
  line-height: 1;
}

/* CSS로 화살표 만들기 */
.scroll-top-btn::before {
  content: '';
  border: solid #0064FF;
  border-width: 0 3px 3px 0;
  display: inline-block;
  padding: 4px;
  transform: rotate(-135deg);
  -webkit-transform: rotate(-135deg);
  position: relative;
}

.scroll-top-btn:hover {
  background-color: #f0f0f0;
  color: #0052cc;
}

.scroll-top-btn:hover::before {
  border-color: #0052cc;
}

/* 버튼이 표시될 때 (v-if 조건 충족 시) */
.scroll-top-btn[style*="display: none;"]~.scroll-top-btn,
.scroll-top-btn {
  opacity: 1;
  transform: translateY(0);
}
</style>
