<template>
  <div class="min-h-screen p-10">
    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-farm-brown-dark mb-2">CODE FARM 문제 목록</h1>
        <p class="text-farm-brown">
          문제를 선택하면 IDE 화면으로 이동해 풀 수 있어요.
        </p>
      </div>

      <!-- 로딩 / 에러 -->
      <div v-if="loading" class="text-center py-12 text-farm-brown">문제 목록을 불러오는 중...</div>
      <div v-else-if="error" class="text-center py-12 text-red-600">{{ error }}</div>

      <!-- 문제 카드 리스트 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link
          v-for="problem in problems"
          :key="problem.problemId ?? problem.id"
          :to="`/ide/${problem.problemId ?? problem.id}`"
          class="block bg-farm-paper border-4 border-farm-brown rounded-2xl p-6 hover:shadow-lg transition-shadow"
        >
          <div class="mb-3 flex items-center justify-between text-sm text-farm-brown-dark">
            <span class="inline-flex items-center gap-1">
              <span class="px-3 py-1 bg-farm-cream rounded-full text-xs font-semibold">
                Lv.{{ problem.difficulty }}
              </span>
              <span class="font-medium">#{{ problem.algorithm }}</span>
            </span>
            <span class="text-xs text-farm-brown/70">ID: {{ problem.problemId ?? problem.id }}</span>
          </div>
          <h2 class="text-xl font-bold text-farm-brown-dark">
            {{ problem.title }}
          </h2>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProblemList } from '@/api/problem'

const problems = ref([])
const loading = ref(true)
const error = ref(null)

onMounted(async () => {
  try {
    loading.value = true
    error.value = null
    const { data } = await getProblemList()
    problems.value = data ?? []
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '문제 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})
</script>
