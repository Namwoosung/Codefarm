<template>
  <!-- 외부 박스 -->
  <div
    role="button"
    tabindex="0"
    class="problem-card-outer rounded-xl border-5 border-farm-brown shadow-md transition-all duration-200 hover:shadow-xl cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown-dark/40 focus-visible:ring-offset-2 max-w-sm w-full"
    @click="$emit('click', problem)"
    @keydown.enter="$emit('click', problem)"
  >
    <!-- 내부 박스 -->
    <div class="problem-card flex flex-col rounded-4xl bg-farm-paper p-6 text-center mx-5 border-2 border-farm-paper">
      <!-- 레벨 뱃지 -->
      <span class="problem-card__level self-start relative inline-block">
        <span class="relative z-10 text-xs font-dnf text-farm-brown-dark/90">Lv.{{ problem?.difficulty ?? '-' }}</span>
      </span>

      <!-- 카테고리  -->
      <p class="problem-card__category mt-3 text-sm font-medium text-farm-brown-dark/90">
        #{{ problem?.algorithm ?? '-' }}
      </p>

      <!-- 문제 title -->
      <h2 class="problem-card__title mt-2 text-xl font-bold text-farm-brown-dark leading-snug">
        {{ problem?.title ?? '-' }}
      </h2>
      <!-- 타이틀 밑 얇은 선 -->
      <span class="problem-card__title-line mt-4 mx-auto block w-12 h-1 bg-farm-yellow"></span>

      <!-- ID: 보조 정보, 작게 우측 하단 -->
      <span class="problem-card__id mt-4 block text-right text-[11px] text-farm-brown/60">
        ID: {{ problem?.problemId ?? problem?.id ?? '-' }}
      </span>
    </div>
  </div>
</template>

<script setup>
defineProps({
  problem: {
    type: Object,
    default: () => ({}),
  },
})
defineEmits(['click'])
</script>

<style scoped>
/* 겉 박스: 테두리와 그림자 */
.problem-card-outer {
  padding: 4px; /* 테두리와 안 박스 사이 간격 */
  background-color: var(--color-farm-brown);
  
  /* 테두리 비스듬한 느낌(깊이감) - 이미지의 bevel 효과 */
  box-shadow:
    0 4px 6px -1px rgba(78, 59, 42, 0.08),
    0 2px 4px -2px rgba(78, 59, 42, 0.06);
}
.problem-card-outer:hover {
  box-shadow:
    0 10px 15px -3px rgba(78, 59, 42, 0.1),
    0 4px 6px -4px rgba(78, 59, 42, 0.08);
}

/* 안 박스: 컨텐츠와 텍스처 */
.problem-card {
  /* texture */
  background-color: var(--color-farm-paper);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4' viewBox='0 0 4 4'%3E%3Cpath fill='rgba(122,92,62,0.08)' d='M1 3h1v1H1V3zm2-2h1v1H3V1z'/%3E%3C/svg%3E");
  background-size: 4px 4px;
}

/* 레벨 뒤 형광펜 작대기 (아래 2/3만 걸치게) */
.problem-card__level::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 45%; /* 레벨 높이의 2/3 */
  background: var(--color-farm-yellow);
  opacity: 0.7;
  z-index: 0;
  border-radius: 0.5px;
}

</style>
