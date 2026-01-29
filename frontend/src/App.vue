<script setup>
import { RouterView, useRoute } from 'vue-router'
import { computed } from 'vue'
import CommonHeader from '@/components/organisms/CommonHeader.vue'
import CommonFooter from '@/components/organisms/CommonFooter.vue'

const route = useRoute()

// IDE 화면에서는 푸터를 제외
const showFooter = computed(() => {
  return !route.path.startsWith('/ide/')
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
