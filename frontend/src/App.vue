<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'
import CommonHeader from '@/components/organisms/CommonHeader.vue'
import CommonFooter from '@/components/organisms/CommonFooter.vue'
import AppToast from '@/components/atoms/AppToast.vue'
import { useAuthStore } from '@/stores/auth'
import { useIdeStore } from '@/stores/ide'

const route = useRoute()
const authStore = useAuthStore()
const ideStore = useIdeStore()

// IDE 화면에서는 푸터를 제외
const showFooter = computed(() => {
  return !route.path.startsWith('/ide/')
})

// 새로고침 시 토큰은 있는데 user가 비어 있으면 프로필 API로 복구 → 헤더 로그인 상태 유지
onMounted(() => {
  authStore.fetchUserIfNeeded()
})
</script>

<template>
  <div class="min-h-screen bg-farm-cream flex flex-col">
    <AppToast />
    <!-- 메인/커리큘럼 → IDE 진입 시 로딩 오버레이 -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="ideStore.ideRouteLoading" class="fixed inset-0 flex items-center justify-center bg-[rgba(245,242,232,0.95)] z-[9999]">
          <div class="card bg-base-100 shadow-lg rounded-2xl p-6">
            <p class="text-base font-semibold text-[var(--color-farm-brown-dark)]">로딩 중...</p>
          </div>
        </div>
      </Transition>
    </Teleport>
    <CommonHeader />
    <main class="flex-1">
      <RouterView />
    </main>
    <CommonFooter v-if="showFooter" />
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
