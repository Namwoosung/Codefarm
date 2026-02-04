<template>
  <header class="bg-farm-paper/98 backdrop-blur-sm border-b border-farm-brown/10 sticky top-0 z-50 overflow-visible">
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
        <nav class="hidden md:flex md:items-center md:justify-start flex-1 h-full gap-4 mx-4 font-dnf">
          <router-link
            to="/"
            class="relative flex items-center justify-center px-4 py-2 rounded-lg text-base font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('home')"
          >
            모든 문제
          </router-link>
          <router-link
            to="/roadmap"
            class="relative flex items-center justify-center px-4 py-2 rounded-lg text-base font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('roadmap')"
            @click="onCurriculumClick"
          >
            커리큘럼
          </router-link>
          <router-link
            v-if="isLoggedIn"
            to="/cards"
            class="relative flex items-center justify-center px-4 py-2 rounded-lg text-base font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('cards')"
          >
            카드
          </router-link>
          <router-link
            v-if="isLoggedIn && user && user.userId"
            :to="`/profile/${user.userId}`"
            class="relative flex items-center justify-center px-4 py-2 rounded-lg text-base font-medium text-farm-brown-dark/65 hover:text-farm-brown-dark transition-colors select-none"
            :class="navLinkClass('profile')"
          >
            마이페이지
          </router-link>
        </nav>

        <!-- 우측 영역 -->
        <div class="flex items-center gap-3 sm:gap-4">
          <!-- 사용자 정보 -->
          <div v-if="isLoggedIn && user && user.userId" class="flex items-center gap-3">
            <button
              class="text-sm font-medium text-farm-brown/70 hover:text-farm-brown-dark transition-colors"
              @click="handleLogout"
            >
              로그아웃
            </button>
            <router-link
              :to="`/profile/${user.userId}`"
              class="flex items-center justify-center w-8 h-8 rounded-full bg-farm-green-light hover:bg-farm-green text-farm-green-dark font-medium text-sm shadow-sm transition-colors"
            >
              {{ user.nickname?.[0]?.toUpperCase() || user.name?.[0]?.toUpperCase() || 'U' }}
            </router-link>
          </div>

          <!-- 비로그인 -->
          <template v-else>
            <router-link
              to="/signup"
              class="text-sm font-medium text-farm-brown/70 hover:text-farm-brown-dark transition-colors"
            >
              회원가입
            </router-link>
            <router-link
              to="/login"
              class="px-4 py-2 text-sm font-medium text-farm-paper bg-farm-point rounded-xl hover:bg-farm-point/90 transition-colors"
            >
              로그인
            </router-link>
          </template>

          <!-- 모바일 메뉴 버튼 -->
          <button
            class="md:hidden p-2 rounded-lg text-farm-brown-dark hover:bg-farm-cream/60 hover:text-farm-brown transition-colors"
            @click="toggleMobileMenu"
            aria-label="메뉴"
          >
            <i :class="showMobileMenu ? 'pi pi-times' : 'pi pi-bars'" class="text-xl"></i>
          </button>
        </div>
      </div>

      <!-- 모바일 네비게이션 메뉴 -->
      <div v-if="showMobileMenu" class="md:hidden border-t border-farm-brown/10 py-3 font-dnf">
        <div class="flex flex-col gap-0.5">
          <router-link
            to="/"
            class="w-full text-center px-4 py-2.5 text-base font-medium text-farm-brown-dark hover:bg-farm-cream/80 rounded-lg transition-colors"
            active-class="text-farm-brown-dark bg-farm-cream/80"
            @click="closeMobileMenu"
          >
            메인페이지
          </router-link>
          <router-link
            to="/roadmap"
            class="w-full text-center px-4 py-2.5 text-base font-medium text-farm-brown-dark hover:bg-farm-cream/80 rounded-lg transition-colors"
            active-class="text-farm-brown-dark bg-farm-cream/80"
            @click="onCurriculumClickMobile"
          >
            커리큘럼
          </router-link>
          <router-link
            v-if="isLoggedIn"
            to="/cards"
            class="w-full text-center px-4 py-2.5 text-base font-medium text-farm-brown-dark hover:bg-farm-cream/80 rounded-lg transition-colors"
            active-class="text-farm-brown-dark bg-farm-cream/80"
            @click="closeMobileMenu"
          >
            카드
          </router-link>
          <router-link
            v-if="isLoggedIn && user && user.userId"
            :to="`/profile/${user.userId}`"
            class="w-full text-center px-4 py-2.5 text-base font-medium text-farm-brown-dark hover:bg-farm-cream/80 rounded-lg transition-colors"
            active-class="text-farm-brown-dark bg-farm-cream/80"
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
import logoUrl from '@/assets/common/logo.png'

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
