<template>
  <Teleport to="body">
    <div v-if="show" class="report-modal-overlay" @click.self="$emit('close')">
      <div class="report-modal-card">
        <h2 class="report-modal-title">Report</h2>
        <p v-if="report?.result" class="report-modal-id"># {{ report.result.resultId }}</p>
        <h3 v-if="report?.result?.problem" class="report-modal-problem-title">
          {{ report.result.problem.title }}
        </h3>
        <div v-if="report?.result?.feedback" class="report-modal-feedback">
          <p class="report-modal-feedback-text">{{ report.result.feedback }}</p>
        </div>
        <div v-else class="report-modal-feedback">
          <p class="report-modal-feedback-text">제출이 완료되었습니다.</p>
        </div>
        <div v-if="report?.result" class="report-modal-meta">
          <span v-if="report.result.solveTime != null">풀이 시간 {{ formatSolveTime(report.result.solveTime) }}</span>
          <span v-if="report.result.execTime != null"> · 실행 {{ report.result.execTime }}ms</span>
          <span v-if="report.result.memory != null"> · 메모리 {{ report.result.memory }}MB</span>
        </div>
        <button type="button" class="report-modal-button" @click="$emit('close')">
          메인 화면으로
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
defineProps({
  show: { type: Boolean, default: false },
  report: { type: Object, default: null }
})
defineEmits(['close'])

function formatSolveTime(seconds) {
  if (seconds == null) return ''
  if (seconds < 60) return `${seconds}초`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s ? `${m}분 ${s}초` : `${m}분`
}
</script>

<style scoped>
.report-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.report-modal-card {
  background: var(--color-farm-paper, #f5f2e8);
  border-radius: 1rem;
  padding: 2rem 2.5rem;
  max-width: 640px;
  width: 100%;
  max-height: 94vh;
  overflow-y: auto;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.report-modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-farm-green, #5e8d48);
  margin: 0 0 0.25rem 0;
}

.report-modal-id {
  font-size: 0.875rem;
  color: var(--color-farm-brown, #4e3b2a);
  margin: 0 0 0.5rem 0;
}

.report-modal-problem-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-farm-brown-dark, #2d2a26);
  margin: 0 0 1rem 0;
  line-height: 1.4;
}

.report-modal-feedback {
  margin-bottom: 1rem;
}

.report-modal-feedback-text {
  font-size: 0.95rem;
  color: var(--color-farm-brown-dark, #2d2a26);
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0;
}

.report-modal-meta {
  font-size: 0.8rem;
  color: var(--color-farm-brown, #4e3b2a);
  margin-bottom: 1.25rem;
}

.report-modal-button {
  display: block;
  width: 100%;
  padding: 0.75rem 1.25rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: #fff;
  background: var(--color-farm-green, #5e8d48);
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.report-modal-button:hover {
  background: var(--color-farm-green-dark, #4a7340);
}
</style>
