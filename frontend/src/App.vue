<script setup>
import { RouterView } from 'vue-router'
import CommonHeader from '@/components/organisms/CommonHeader.vue'
</script>

<template>
  <div class="min-h-screen bg-farm-cream">
    <CommonHeader />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
</style>
