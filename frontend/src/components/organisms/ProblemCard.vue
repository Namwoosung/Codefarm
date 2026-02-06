<template>
  <div
    role="button"
    tabindex="0"
    class="problem-card group relative overflow-hidden rounded-2xl bg-white border border-farm-brown/20 shadow-sm transition-all duration-300 hover:shadow-lg hover:border-farm-brown/40 hover:-translate-y-1 cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-olive/50 focus-visible:ring-offset-2"
    :class="cardStatusClass"
    @click="$emit('click', problem)"
    @keydown.enter="$emit('click', problem)"
  >
    <!-- 상단 장식 바 -->
    <div class="h-1.5 w-full" :class="statusBarClass"></div>
    
    <!-- 카드 내용 -->
    <div class="p-5">
      <!-- 상단: 레벨 + 상태 뱃지 -->
      <div class="flex items-center justify-between mb-3">
        <!-- 레벨 뱃지 -->
        <span 
          class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold"
          :class="levelBadgeClass"
        >
          Lv.{{ displayLevel }}
        </span>
        
        <!-- 상태 뱃지 -->
        <span 
          v-if="statusBadge"
          class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-semibold"
          :class="statusBadge.class"
        >
          <span class="w-1.5 h-1.5 rounded-full" :class="statusBadge.dotClass"></span>
          {{ statusBadge.label }}
        </span>
      </div>

      <!-- 문제 번호 + 제목 -->
      <div class="mb-3">
        <p class="text-xs text-farm-brown/60 mb-1">No.{{ problem?.problemId ?? '-' }}</p>
        <h3 class="text-base font-bold text-farm-brown-dark truncate leading-snug group-hover:text-farm-olive transition-colors">
          {{ problem?.title ?? '제목 없음' }}
        </h3>
      </div>

      <!-- 구분선 -->
      <div class="w-full h-px bg-gradient-to-r from-transparent via-farm-brown/15 to-transparent mb-3"></div>

      <!-- 하단: 알고리즘 태그 -->
      <div class="flex items-center gap-2">
        <span 
          class="inline-flex items-center px-2 py-1 bg-farm-cream rounded-md text-xs font-medium text-farm-brown-dark/80"
        >
          <iconify-icon icon="mdi:tag-outline" class="mr-1 text-farm-olive"></iconify-icon>
          {{ displayAlgorithm }}
        </span>
      </div>
    </div>

    <!-- 호버 시 우측 하단 화살표 -->
    <div class="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
      <iconify-icon icon="mdi:arrow-right" class="text-farm-olive text-lg"></iconify-icon>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  problem: {
    type: Object,
    default: () => ({}),
  },
})
defineEmits(['click'])

// 난이도 표시
const displayLevel = computed(() => {
  const diff = props.problem?.difficulty
  if (typeof diff === 'number') return diff
  if (typeof diff === 'string') {
    const match = diff.match(/\d+/)
    return match ? match[0] : '?'
  }
  return '?'
})

// 알고리즘 표시
const displayAlgorithm = computed(() => {
  const algo = props.problem?.algorithm
  if (Array.isArray(algo)) return algo[0] || '미분류'
  return algo || '미분류'
})

// 상태 확인
const isSolved = computed(() => props.problem?.userStatus?.isSolved)
const isTried = computed(() => props.problem?.userStatus?.isTried)

// 상태별 카드 클래스
const cardStatusClass = computed(() => {
  if (isSolved.value) return 'ring-1 ring-farm-green/30'
  if (isTried.value) return 'ring-1 ring-farm-yellow/40'
  return ''
})

// 상태 바 색상
const statusBarClass = computed(() => {
  if (isSolved.value) return 'bg-gradient-to-r from-farm-green/80 to-farm-green'
  if (isTried.value) return 'bg-gradient-to-r from-farm-yellow/80 to-farm-yellow'
  return 'bg-gradient-to-r from-farm-brown/30 to-farm-brown/50'
})

// 레벨 뱃지 색상
const levelBadgeClass = computed(() => {
  const level = Number(displayLevel.value)
  if (level <= 1) return 'bg-emerald-100 text-emerald-700'
  if (level <= 2) return 'bg-sky-100 text-sky-700'
  if (level <= 3) return 'bg-amber-100 text-amber-700'
  if (level <= 4) return 'bg-orange-100 text-orange-700'
  return 'bg-rose-100 text-rose-700'
})

// 상태 뱃지
const statusBadge = computed(() => {
  if (isSolved.value) {
    return {
      label: '해결',
      class: 'bg-farm-green/10 text-farm-green',
      dotClass: 'bg-farm-green'
    }
  }
  if (isTried.value) {
    return {
      label: '도전중',
      class: 'bg-farm-yellow/20 text-amber-700',
      dotClass: 'bg-farm-yellow'
    }
  }
  return null
})
</script>

<style scoped>
.problem-card {
  background: linear-gradient(135deg, #ffffff 0%, #fdfcfa 100%);
}
</style>
