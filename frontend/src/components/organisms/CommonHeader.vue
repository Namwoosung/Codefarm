<template>
  <header class="bg-farm-paper border-b border-farm-cream shadow-sm sticky top-0 z-50 overflow-visible">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between gap-4 h-16">
        <!-- 로고 영역 -->
        <div class="flex-shrink-0">
          <router-link to="/" class="block">
            <img
              :src="logoUrl"
              alt="CODE FARM"
              class="h-[92px] md:h-[105px] w-auto max-w-[85vw] object-contain -translate-y-1 drop-shadow-sm select-none"
              draggable="false"
            />
          </router-link>
        </div>

        <!-- 네비게이션 메뉴 (데스크톱) -->
        <nav class="hidden md:flex md:items-center h-full gap-2 me-auto mx-4">
          <router-link
            to="/"
            class="relative px-4 py-2 text-sm font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('home')"
          >
            메인페이지
          </router-link>
          <router-link
            to="/roadmap"
            class="relative px-4 py-2 text-sm font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('roadmap')"
            @click="onCurriculumClick"
          >
            커리큘럼
          </router-link>
          <router-link
            v-if="isLoggedIn"
            to="/cards"
            class="relative px-4 py-2 text-sm font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('cards')"
          >
            카드
          </router-link>
          <router-link
            v-if="isLoggedIn && user && user.userId"
            :to="`/profile/${user.userId}`"
            class="relative px-4 py-2 text-sm font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('profile')"
          >
            마이페이지
          </router-link>
        </nav>

        <!-- 우측 영역 -->
        <div class="flex items-center space-x-4">
          <!-- 사용자 정보 -->
          <div v-if="isLoggedIn && user && user.userId" class="flex items-center space-x-3">
            <!-- 로그아웃 버튼 -->
            <button
              class="text-sm font-medium text-farm-brown-dark hover:text-farm-green transition-colors"
              @click="handleLogout"
            >
              로그아웃
            </button>
            <!-- 프로필 아이콘 -->
            <router-link
              :to="`/profile/${user.userId}`"
              class="flex items-center justify-center w-8 h-8 rounded-full bg-farm-green-light hover:bg-farm-green transition-colors"
            >
              <span class="text-sm font-medium text-farm-green-dark">
                {{ user.nickname?.[0]?.toUpperCase() || user.name?.[0]?.toUpperCase() || 'U' }}
              </span>
            </router-link>
          </div>

          <!-- 비로그인 상태: 회원가입 링크와 로그인 버튼 -->
          <template v-else>
            <router-link
              to="/signup"
              class="text-sm font-medium text-farm-brown-dark hover:text-farm-green transition-colors"
            >
              회원가입
            </router-link>
            <router-link
              to="/login"
              class="px-4 py-2 text-sm font-medium text-farm-brown-dark bg-white border border-farm-brown rounded-lg hover:bg-farm-cream transition-colors"
            >
              로그인
            </router-link>
          </template>

          <!-- 모바일 메뉴 버튼 -->
          <button
            class="md:hidden p-2 text-farm-brown-dark hover:text-farm-green transition-colors"
            @click="toggleMobileMenu"
            aria-label="메뉴"
          >
            <i :class="showMobileMenu ? 'pi pi-times' : 'pi pi-bars'" class="text-xl"></i>
          </button>
        </div>
      </div>

      <!-- 모바일 네비게이션 메뉴 -->
      <div v-if="showMobileMenu" class="md:hidden border-t border-farm-cream py-4">
        <div class="flex flex-col space-y-2">
          <router-link
            to="/"
            class="px-3 py-2 text-base font-medium text-farm-brown-dark hover:text-farm-green hover:bg-farm-cream rounded-lg transition-colors"
            active-class="text-farm-green bg-farm-cream"
            @click="closeMobileMenu"
          >
            메인페이지
          </router-link>
          <router-link
            to="/roadmap"
            class="px-3 py-2 text-base font-medium text-farm-brown-dark hover:text-farm-green hover:bg-farm-cream rounded-lg transition-colors"
            active-class="text-farm-green bg-farm-cream"
            @click="onCurriculumClickMobile"
          >
            커리큘럼
          </router-link>
          <router-link
            v-if="isLoggedIn"
            to="/cards"
            class="px-3 py-2 text-base font-medium text-farm-brown-dark hover:text-farm-green hover:bg-farm-cream rounded-lg transition-colors"
            active-class="text-farm-green bg-farm-cream"
            @click="closeMobileMenu"
          >
            카드
          </router-link>
          <router-link
            v-if="isLoggedIn && user && user.userId"
            :to="`/profile/${user.userId}`"
            class="px-3 py-2 text-base font-medium text-farm-brown-dark hover:text-farm-green hover:bg-farm-cream rounded-lg transition-colors"
            active-class="text-farm-green bg-farm-cream"
            @click="closeMobileMenu"
          >
            마이페이지
          </router-link>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import logoUrl from '@/assets/logo.png'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const user = computed(() => authStore.user)

const showMobileMenu = ref(false)

const isActiveKey = (key) => {
  if (key === 'profile') return route.path.startsWith('/profile/')
  if (key === 'home') return route.path === '/'
  if (key === 'roadmap') return route.path === '/roadmap'
  if (key === 'cards') return route.path === '/cards'
  return false
}

const navLinkClass = (key) => {
  // 이전 상태로: 효과 없이 "활성 글자색만" 변경
  return isActiveKey(key) ? 'text-farm-olive' : ''
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}

const onCurriculumClick = (ev) => {
  if (route.path === '/roadmap') {
    ev.preventDefault()
    router.push({ path: '/roadmap', query: { ...route.query, refresh: Date.now() } })
  }
}

const onCurriculumClickMobile = (ev) => {
  onCurriculumClick(ev)
  closeMobileMenu()
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
