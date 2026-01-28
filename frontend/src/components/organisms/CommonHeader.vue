<template>
  <header class="bg-farm-paper border-b border-farm-cream shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <!-- 로고 영역 -->
        <div class="flex-shrink-0">
          <router-link to="/" class="flex items-center space-x-1">
            <span
              v-for="(char, index) in 'CODE FARM'.split('')"
              :key="index"
              class="w-8 h-8 bg-farm-yellow rounded-full flex items-center justify-center text-farm-brown-dark font-bold text-sm shadow-sm"
            >
              {{ char === ' ' ? '' : char }}
            </span>
          </router-link>
        </div>

        <!-- 네비게이션 메뉴 (데스크톱) -->
        <nav class="hidden md:flex md:items-center md:space-x-8">
          <router-link
            to="/"
            class="relative px-3 py-2 text-sm font-medium text-farm-brown-dark hover:text-farm-green transition-colors"
          >
            메인페이지
            <span
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#5E8D48] transition-opacity opacity-0"
              :class="{ 'opacity-100': isActiveRoute('/') }"
            ></span>
          </router-link>
          <router-link
            to="/roadmap"
            class="relative px-3 py-2 text-sm font-medium text-farm-brown-dark hover:text-farm-green transition-colors"
          >
            커리큘럼
            <span
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#5E8D48] transition-opacity opacity-0"
              :class="{ 'opacity-100': isActiveRoute('/roadmap') }"
            ></span>
          </router-link>
          <router-link
            v-if="isLoggedIn && user && user.userId"
            :to="`/profile/${user.userId}`"
            class="relative px-3 py-2 text-sm font-medium text-farm-brown-dark hover:text-farm-green transition-colors"
          >
            마이페이지
            <span
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-[#5E8D48] transition-opacity opacity-0"
              :class="{ 'opacity-100': route.path.startsWith('/profile/') }"
            ></span>
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
            @click="closeMobileMenu"
          >
            커리큘럼
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isLoggedIn = computed(() => authStore.isLoggedIn)
const user = computed(() => authStore.user)

const showMobileMenu = ref(false)

const isActiveRoute = (path) => {
  // 정확히 해당 경로일 때만 활성화
  return route.path === path
}

const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
}

const closeMobileMenu = () => {
  showMobileMenu.value = false
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
/* 스타일은 PrimeIcons CSS가 전역으로 import되어 있으므로 추가 스타일 불필요 */
</style>
