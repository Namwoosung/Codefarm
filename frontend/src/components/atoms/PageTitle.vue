<template>
  <div class="mb-6">
    <h1 class="text-2xl font-bold text-farm-brown-dark mb-2">{{ title }}</h1>
    <div class="h-1 bg-[#5E8D48] w-12"></div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  }
})
</script>

<style scoped>
</style>
