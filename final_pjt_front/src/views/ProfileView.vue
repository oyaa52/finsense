<template>
  <div class="profile-container" data-aos="fade-up">
    <div class="profile-header">
      <div class="profile-image">
        <img :src="profileImage" alt="Profile Image" />
      </div>
      <div class="profile-info">
        <h2>{{ username }}</h2>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-value">{{ followersCount }}</span>
            <span class="stat-label">팔로워</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ followingCount }}</span>
            <span class="stat-label">팔로잉</span>
          </div>
        </div>
      </div>
    </div>

    <div class="subscriptions-section" v-if="subscriptions.deposit_subscriptions.length > 0 || subscriptions.saving_subscriptions.length > 0">
      <h3>가입한 상품</h3>
      
      <div v-if="subscriptions.deposit_subscriptions.length > 0" class="subscription-list">
        <h4>예금 상품</h4>
        <div v-for="sub in subscriptions.deposit_subscriptions" :key="sub.id" class="subscription-card">
          <div class="subscription-info">
            <h5>{{ sub.bank_name }}</h5>
            <p class="product-name">{{ sub.product_name }}</p>
            <p class="subscription-details">
              <span class="period">{{ sub.period }}개월</span>
              <span class="rate">{{ sub.interest_rate }}%</span>
            </p>
            <p class="subscription-date">가입일: {{ new Date(sub.subscribed_at).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>

      <div v-if="subscriptions.saving_subscriptions.length > 0" class="subscription-list">
        <h4>적금 상품</h4>
        <div v-for="sub in subscriptions.saving_subscriptions" :key="sub.id" class="subscription-card">
          <div class="subscription-info">
            <h5>{{ sub.bank_name }}</h5>
            <p class="product-name">{{ sub.product_name }}</p>
            <p class="subscription-details">
              <span class="period">{{ sub.period }}개월</span>
              <span class="rate">{{ sub.interest_rate }}%</span>
            </p>
            <p class="subscription-date">가입일: {{ new Date(sub.subscribed_at).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import AOS from 'aos'
import 'aos/dist/aos.css'

const route = useRoute()
const username = ref('')
const profileImage = ref('')
const followersCount = ref(0)
const followingCount = ref(0)
const subscriptions = ref({
  deposit_subscriptions: [],
  saving_subscriptions: []
})

const VITE_API_BASE_URL = import.meta.env.VITE_API_URL
const fetchProfile = async () => {
  try {
    const response = await axios.get(`${VITE_API_BASE_URL}/api/v1/accounts/profile/${route.params.username}/`)
    username.value = response.data.username
    profileImage.value = response.data.profile_image || 'https://via.placeholder.com/150'
    followersCount.value = response.data.followers_count
    followingCount.value = response.data.following_count
  } catch (err) {
    console.error('Failed to fetch profile:', err)
  }
}

const fetchSubscriptions = async () => {
  try {
    const response = await axios.get(`${VITE_API_BASE_URL}/api/v1/products/subscriptions/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    subscriptions.value = response.data
  } catch (err) {
    console.error('Failed to fetch subscriptions:', err)
  }
}

onMounted(() => {
  AOS.init()
  fetchProfile()
  fetchSubscriptions()
})
</script>

<style scoped>
.profile-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 30px;
  margin-bottom: 40px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.profile-image img {
  width: 150px;
  height: 150px;
  border-radius: 50%;
  object-fit: cover;
}

.profile-info h2 {
  color: #333;
  margin-bottom: 15px;
}

.stats {
  display: flex;
  gap: 30px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 1.5em;
  font-weight: bold;
  color: #4a90e2;
}

.stat-label {
  color: #666;
}

.subscriptions-section {
  margin-top: 40px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.subscriptions-section h3 {
  color: #333;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.subscription-list {
  margin-top: 20px;
}

.subscription-list h4 {
  color: #4a90e2;
  margin-bottom: 15px;
}

.subscription-card {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.subscription-info h5 {
  color: #333;
  margin-bottom: 5px;
}

.product-name {
  color: #666;
  margin-bottom: 10px;
}

.subscription-details {
  display: flex;
  gap: 15px;
  margin-bottom: 10px;
}

.period {
  color: #4a90e2;
  font-weight: bold;
}

.rate {
  color: #28a745;
  font-weight: bold;
}

.subscription-date {
  color: #666;
  font-size: 0.9em;
}
</style> 