<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'
import CommonHeader from '@/components/organisms/CommonHeader.vue'
import CommonFooter from '@/components/organisms/CommonFooter.vue'
import AppToast from '@/components/atoms/AppToast.vue'
import { useAuthStore } from '@/stores/auth'
import { useUiStore } from '@/stores/ui'
import PageShell from '@/components/atoms/PageShell.vue'

const route = useRoute()
const authStore = useAuthStore()
const uiStore = useUiStore()

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
    <!-- 라우트 전환 중(완성본 준비 전) 빈 프레임/깜빡임 방지 -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="uiStore.routeChanging" class="route-changing">
          <span class="loading loading-spinner loading-lg app-loading-spinner"></span>
        </div>
      </Transition>
    </Teleport>
    <CommonHeader />
    <main class="flex-1 min-h-0">
      <RouterView v-slot="{ Component, route: r }">
        <Transition name="page" mode="out-in" appear>
          <!-- Component가 준비되기 전에는 routeChanging 오버레이가 화면을 커버 -->
          <PageShell
            v-if="Component"
            :key="r.fullPath"
            :component="Component"
            :route-key="r.fullPath"
            :reveal-mode="r.path.startsWith('/profile') ? 'fast' : 'default'"
            @ready="uiStore.endRouteChange()"
          />
          <div v-else :key="`${r.fullPath}-empty`" />
        </Transition>
      </RouterView>
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

.page-enter-active {
  transition: opacity 650ms ease, transform 850ms cubic-bezier(0.22, 1, 0.36, 1);
  will-change: opacity, transform;
}
.page-leave-active {
  transition: none;
}
.page-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.page-leave-to {
  opacity: 0;
  transform: none;
}
.route-changing {
  position: fixed;
  inset: 0;
  z-index: 9997;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(245, 242, 232, 0.55);
  backdrop-filter: blur(2px);
}

@media (prefers-reduced-motion: reduce) {
  .page-enter-active,
  .page-leave-active {
    transition: none;
  }
  .page-enter-from,
  .page-leave-to {
    transform: none;
  }
}
</style>
