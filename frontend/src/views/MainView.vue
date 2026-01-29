<template>
  <div class="min-h-screen p-10">
    <div class="max-w-7xl mx-auto">
      <!-- 간단한 헤더/배너 자리 -->
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-farm-brown-dark mb-2">CODE FARM 문제 목록 (테스트용)</h1>
        <p class="text-farm-brown">
          문제를 선택하면 IDE 화면으로 이동해 풀 수 있어요.
        </p>
      </div>

      <!-- 문제 카드 리스트 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <router-link
          v-for="problem in problems"
          :key="problem.id"
          :to="`/ide/${problem.id}`"
          class="block bg-farm-paper border-4 border-farm-brown rounded-2xl p-6 hover:shadow-lg transition-shadow"
        >
          <div class="mb-3 flex items-center justify-between text-sm text-farm-brown-dark">
            <span class="inline-flex items-center gap-1">
              <span class="px-3 py-1 bg-farm-cream rounded-full text-xs font-semibold">
                Lv.{{ problem.difficulty }}
              </span>
              <span class="font-medium">#{{ problem.algorithm }}</span>
            </span>
            <span class="text-xs text-farm-brown/70">ID: {{ problem.id }}</span>
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
import rawProblems from '@/mocks/sampled_30_clean.json'

// 라우트/백엔드와 맞추기 위해 실제 DB ID 사용 (1번 문제 = 21, 2번 = 22, ...)
const PROBLEM_ID_OFFSET = 21
const problems = rawProblems.map((problem, index) => ({
  id: PROBLEM_ID_OFFSET + index,
  ...problem,
}))
</script>

<style scoped>
</style>
