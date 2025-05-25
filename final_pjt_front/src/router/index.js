import { createRouter, createWebHistory } from 'vue-router'
import LandingPageView from '@/views/LandingPageView.vue'
import MainPageView from '@/views/MainPageView.vue'
import KakaomapPageView from '@/views/KakaomapPageView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import ProfileManagementView from '@/views/ProfileManagementView.vue'
import DepositComparisonView from '@/views/DepositComparisonView.vue'
import EconomicNewsView from '@/views/EconomicNewsView.vue'
import MainPageDefaultView from '@/views/MainPageDefaultView.vue'
import CommodityComparisonView from '@/views/CommodityComparisonView.vue'
import { useAuthStore } from '@/stores/authStore'

// 임시 플레이스홀더 컴포넌트 (실제 컴포넌트로 교체 필요)
const PlaceholderComponent = (text) => ({
  template: `<div><h2>${text}</h2><p>이 페이지는 현재 개발 중입니다.</p></div>`,
  props: ['text']
})

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landingPage',
      component: LandingPageView
    },
    {
      path: '/main',
      name: 'mainPage',
      component: MainPageView,
      children: [
        {
          path: '',
          name: 'mainPageDefault',
          components: {
            mainServiceView: MainPageDefaultView
          }
        },
        {
          path: 'deposit-comparison',
          name: 'depositComparison',
          components: {
            mainServiceView: DepositComparisonView
          }
        },
        {
          path: 'commodity-comparison',
          name: 'commodityComparison',
          components: {
            mainServiceView: CommodityComparisonView
          }
        },
        {
          path: 'product-recommendation',
          name: 'productRecommendation',
          components: {
            mainServiceView: PlaceholderComponent('금융상품 추천')
          }
        },
        {
          path: 'economic-news',
          name: 'economicNews',
          components: {
            mainServiceView: EconomicNewsView
          }
        },
        {
          path: 'nearby-banks',
          name: 'nearbyBanks',
          components: {
            mainServiceView: KakaomapPageView
          }
        },
        {
          path: 'community',
          name: 'community',
          components: {
            mainServiceView: PlaceholderComponent('커뮤니티')
          }
        },
        {
          path: 'profile-management',
          name: 'profileManagement',
          components: {
            mainServiceView: ProfileManagementView
          },
          beforeEnter: (to, from, next) => {
            const authStore = useAuthStore()
            if (authStore.isAuthenticated) {
              next()
            } else {
              alert('로그인이 필요한 서비스입니다.')
              next({ name: 'login' })
            }
          }
        },
        {
          path: 'settings',
          name: 'settings',
          components: {
            mainServiceView: PlaceholderComponent('설정')
          }
        }
      ]
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    }
  ]
})

export default router
