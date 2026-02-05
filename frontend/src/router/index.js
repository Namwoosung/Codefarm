import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useIdeStore } from '@/stores/ide'
import { useUiStore } from '@/stores/ui'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior() {
    return { left: 0, top: 0 }
  },
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
      component: () => import('@/views/LoginView.vue'),
      props: { initialMode: 'signup' }
    },
    {
      path: '/ide/:id',
      name: 'ide',
      component: () => import('@/views/IdeView.vue')
    },
  ],
})

// 메인 페이지 복원용 storage 키 (MainView와 동일한 문자열)
const MAIN_PAGE_STORAGE_KEY = 'main_page'
const MAIN_SCROLL_STORAGE_KEY = 'main_scroll'

router.beforeEach((to, from, next) => {
  const ideStore = useIdeStore()
  const uiStore = useUiStore()

  // 메인(/)에서 IDE가 아닌 다른 페이지로 나갈 때: 복원용 저장값 초기화 → 다른 곳에서 메인 올 때 1페이지·맨 위로
  if (from.path === '/' && !to.path.startsWith('/ide/')) {
    try {
      sessionStorage.removeItem(MAIN_PAGE_STORAGE_KEY)
      sessionStorage.removeItem(MAIN_SCROLL_STORAGE_KEY)
    } catch (_) {}
  }

  // 모든 화면 이동: 새 화면이 "완성본"으로 준비될 때까지 오버레이 유지
  if (to.fullPath !== from.fullPath) uiStore.startRouteChange()

  if (to.path.startsWith('/ide/')) {
    ideStore.ideRouteLoading = true
  }
  if (from.path.startsWith('/ide/') && !to.path.startsWith('/ide/')) {
    ideStore.ideRouteLoading = false
  }
  next()
})

export default router
