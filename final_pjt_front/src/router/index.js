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
import CommunityView from '@/views/CommunityView.vue'
import CommodityComparisonView from '@/views/CommodityComparisonView.vue'
import VideoDetailView from '@/views/VideoDetailView.vue'
import FavoriteChannelsView from '@/views/FavoriteChannelsView.vue'
import FavoriteVideosView from '@/views/FavoriteVideosView.vue'
import AIRecommendationView from '@/views/AIRecommendationView.vue'
import AdminPanelView from '@/views/AdminPanelView.vue'
import UserProfileView from '@/views/UserProfileView.vue'
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
            mainServiceView: AIRecommendationView
          },
          beforeEnter: (to, from, next) => {
            const token = localStorage.getItem('accessToken')
            if (token) {
              next()
            } else {
              alert('로그인이 필요한 서비스입니다.')
              next({ name: 'login' })
            }
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
          path: 'economic-news/:videoId',
          name: 'videoDetail',
          components: {
            mainServiceView: VideoDetailView
          },
          props: { mainServiceView: true }
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
            mainServiceView: CommunityView
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
        },
        {
          path: 'favorite-channels',
          name: 'favoriteChannels',
          components: {
            mainServiceView: FavoriteChannelsView
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
          path: 'favorite-videos',
          name: 'favoriteVideos',
          components: {
            mainServiceView: FavoriteVideosView
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
          path: 'admin-panel',
          name: 'adminPanel',
          components: {
            mainServiceView: AdminPanelView
          },
          beforeEnter: (to, from, next) => {
            const authStore = useAuthStore()
            if (authStore.isAuthenticated && authStore.currentUser && (authStore.currentUser.is_superuser || authStore.currentUser.is_staff)) {
              next()
            } else if (authStore.isAuthenticated) {
              alert('관리자 권한이 없습니다.')
              next(from.path || '/main')
            } else {
              alert('로그인이 필요한 서비스입니다.')
              next({ name: 'login' })
            }
          }
        },
        {
          path: 'profile/:username',
          name: 'userProfile',
          components: {
            mainServiceView: UserProfileView
          },
          props: { mainServiceView: true }
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
    },
    {
      path: '/ai-recommendation',
      name: 'AIRecommendation',
      component: AIRecommendationView,
      meta: { requiresAuth: true }
    }
  ]
})

export default router
