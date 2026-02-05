<template>
  <!-- 외부 박스 -->
  <div
    role="button"
    tabindex="0"
    class="problem-card-outer min-w-0 rounded-xl border-5 border-farm-brown shadow-md transition-all duration-200 hover:shadow-xl cursor-pointer focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown-dark/40 focus-visible:ring-offset-2 max-w-sm w-full"
    @click="$emit('click', problem)"
    @keydown.enter="$emit('click', problem)"
  >
    <!-- 내부 박스 -->
    <div class="problem-card flex min-w-0 flex-col rounded-4xl bg-farm-paper p-7 text-center mx-5 border-2 border-farm-paper">
      <!-- 레벨 뱃지 -->
      <span class="problem-card__level self-start relative inline-block shrink-0">
        <span class="relative z-10 text-xs font-dnf text-farm-brown-dark/90">Lv.{{ problem?.difficulty ?? '-' }}</span>
      </span>

      <!-- 카테고리  -->
      <p class="problem-card__category min-w-0 truncate text-sm font-medium text-farm-brown-dark/90">
        #{{ problem?.algorithm ?? '-' }}
      </p>

      <!-- 문제 title -->
      <h2 class="problem-card__title mt-2 min-w-0 truncate text-xl font-bold text-farm-brown-dark">
        {{ problem?.title ?? '-' }}
      </h2>
      <!-- 타이틀 밑 얇은 선 -->
      <span class="problem-card__title-line my-3 mx-auto block w-12 h-1 bg-farm-yellow"></span>
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
.problem-card-outer {
  padding: 4px;
  background-color: var(--color-farm-brown);
  box-shadow:
    0 4px 6px -1px rgba(78, 59, 42, 0.08),
    0 2px 4px -2px rgba(78, 59, 42, 0.06);
}
.problem-card-outer:hover {
  box-shadow:
    0 10px 15px -3px rgba(78, 59, 42, 0.1),
    0 4px 6px -4px rgba(78, 59, 42, 0.08);
}
.problem-card {
  background-color: var(--color-farm-paper);
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='4' height='4' viewBox='0 0 4 4'%3E%3Cpath fill='rgba(122,92,62,0.08)' d='M1 3h1v1H1V3zm2-2h1v1H3V1z'/%3E%3C/svg%3E");
  background-size: 4px 4px;
}
.problem-card__level::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 45%;
  background: var(--color-farm-yellow);
  opacity: 0.7;
  z-index: 0;
  border-radius: 0.5px;
}

</style>
