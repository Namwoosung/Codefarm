import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useIdeStore } from '@/stores/ide'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: () => import('@/views/MainView.vue')
    },
    {
      path: '/profile/:id',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      beforeEnter: (to, from, next) => {
        const authStore = useAuthStore()
        const userId = to.params.id
        
        // 로그인하지 않은 경우
        if (!authStore.isLoggedIn || !authStore.user) {
          next('/login')
          return
        }
        
        // URL의 id가 현재 로그인한 사용자의 id와 다른 경우
        if (userId !== String(authStore.user.userId)) {
          // 자신의 프로필로 리다이렉트
          next(`/profile/${authStore.user.userId}`)
          return
        }
        
        next()
      }
    },
    {
      path: '/problem/:id',
      name: 'problem',
      component: () => import('@/views/ProblemView.vue')
    },
    {
      path: '/roadmap',
      name: 'roadmap',
      component: () => import('@/views/RoadmapView.vue')
    },
    {
      path: '/cards',
      name: 'cards',
      component: () => import('@/views/CardView.vue'),
      beforeEnter: (to, from, next) => {
        const authStore = useAuthStore()
        if (!authStore.isLoggedIn || !authStore.user) {
          next('/login')
          return
        }
        next()
      }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue')
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('@/views/SignupView.vue')
    },
    {
      path: '/ide/:id',
      name: 'ide',
      component: () => import('@/views/IdeView.vue')
    },
  ],
})

router.beforeEach((to, from, next) => {
  const ideStore = useIdeStore()
  if (to.path.startsWith('/ide/')) {
    ideStore.ideRouteLoading = true
  }
  if (from.path.startsWith('/ide/') && !to.path.startsWith('/ide/')) {
    ideStore.ideRouteLoading = false
  }
  next()
})

export default router
