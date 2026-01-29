<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed, onMounted } from 'vue'
import CommonHeader from '@/components/organisms/CommonHeader.vue'
import CommonFooter from '@/components/organisms/CommonFooter.vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

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
    <CommonHeader />
    <main class="flex-1">
      <RouterView />
    </main>
    <CommonFooter v-if="showFooter" />
  </div>
</template>

<style scoped>
</style>
