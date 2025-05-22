import { createRouter, createWebHistory } from 'vue-router'
import Main from '@/components/Main.vue'
import LandingPageView from '@/views/LandingPageView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingPageView,
    },
    {
      path: '/main',
      name: 'main',
      component: Main,
    },
  ],
})

export default router
