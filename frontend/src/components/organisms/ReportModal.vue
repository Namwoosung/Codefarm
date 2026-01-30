<template>
  <Teleport to="body">
    <div v-if="show" class="report-modal-overlay" @click.self="$emit('close')">
      <div class="report-modal-card">
        <h2 class="report-modal-title">Report</h2>
        <p v-if="report?.result" class="report-modal-id"># {{ report.result.resultId }}</p>
        <!-- FR-CODE-009: 문제 정보 -->
        <div v-if="report?.result?.problem" class="report-modal-section">
          <h4 class="report-modal-section-title">문제 정보</h4>
          <p class="report-modal-problem-title">{{ report.result.problem.title }}</p>
          <p v-if="report.result.problem.problemId != null" class="report-modal-meta-text">문제 번호 {{ report.result.problem.problemId }}</p>
          <p v-if="report.result.problem.difficulty" class="report-modal-meta-text">난이도 {{ report.result.problem.difficulty }}</p>
        </div>
        <!-- FR-CODE-009: 받은 힌트 수, 힌트 내용 -->
        <div v-if="report?.result && (report.result.hintCount != null || (Array.isArray(report.result.hintContents) && report.result.hintContents.length))" class="report-modal-section">
          <h4 class="report-modal-section-title">힌트</h4>
          <p v-if="report.result.hintCount != null" class="report-modal-meta-text">받은 힌트 수: {{ report.result.hintCount }}개</p>
          <div v-if="Array.isArray(report.result.hintContents) && report.result.hintContents.length" class="report-modal-hint-contents">
            <p v-for="(h, i) in report.result.hintContents" :key="i" class="report-modal-hint-item">{{ h }}</p>
          </div>
        </div>
        <!-- FR-CODE-009: 풀이 시간, 풀이 날짜 -->
        <div v-if="report?.result" class="report-modal-section report-modal-meta">
          <span v-if="report.result.solveTime != null">풀이 시간 {{ formatSolveTime(report.result.solveTime) }}</span>
          <span v-if="report.result.createdAt"> · 풀이 날짜 {{ formatDate(report.result.createdAt) }}</span>
        </div>
        <!-- FR-CODE-009: 제출 코드 -->
        <div v-if="report?.result?.code != null && report.result.code !== ''" class="report-modal-section">
          <h4 class="report-modal-section-title">제출 코드</h4>
          <pre class="report-modal-code">{{ report.result.code }}</pre>
        </div>
        <!-- FR-CODE-009: 실행 시간, 메모리, 사용 언어 -->
        <div v-if="report?.result" class="report-modal-section report-modal-meta">
          <span v-if="report.result.execTime != null">실행 {{ report.result.execTime }}ms</span>
          <span v-if="report.result.memory != null"> · 메모리 {{ report.result.memory }}MB</span>
          <span v-if="report.result.language"> · 사용 언어 {{ formatLanguage(report.result.language) }}</span>
        </div>
        <div v-if="report?.result?.feedback" class="report-modal-feedback">
          <p class="report-modal-feedback-text">{{ report.result.feedback }}</p>
        </div>
        <div v-else-if="report?.result" class="report-modal-feedback">
          <p class="report-modal-feedback-text">제출이 완료되었습니다.</p>
        </div>
        <!-- FR-CODE-009: 개선 방향 -->
        <div v-if="report?.result?.improvementDirection" class="report-modal-section">
          <h4 class="report-modal-section-title">개선 방향</h4>
          <p class="report-modal-feedback-text">{{ report.result.improvementDirection }}</p>
        </div>
        <!-- 채점·결과 -->
        <div v-if="report?.evaluationContext || report?.xp != null" class="report-modal-grading">
          <h4 class="report-modal-grading-title">채점·결과</h4>
          <div v-if="report.evaluationContext" class="report-modal-grading-summary">
            <span class="report-modal-pass-count">
              {{ report.evaluationContext.passedCount ?? 0 }} / {{ report.evaluationContext.totalCount ?? 0 }}개 통과
            </span>
            <span v-if="report.evaluationContext.totalCount > 0" class="report-modal-pass-rate">
              ({{ passRate }}%)
            </span>
          </div>
          <div v-if="report.evaluationContext?.failReason" class="report-modal-fail-reason">
            {{ report.evaluationContext.failReason }}
          </div>
          <div v-if="report.evaluationContext?.failedLineNo != null" class="report-modal-diff">
            <p class="report-modal-diff-line">실패한 줄: {{ report.evaluationContext.failedLineNo }}</p>
            <p v-if="report.evaluationContext.expectedLine != null" class="report-modal-diff-expected">
              기대값: {{ report.evaluationContext.expectedLine }}
            </p>
            <p v-if="report.evaluationContext.actualLine != null" class="report-modal-diff-actual">
              출력: {{ report.evaluationContext.actualLine }}
            </p>
          </div>
          <div v-if="report.xp != null" class="report-modal-xp">
            획득 XP: <strong>{{ report.xp }}</strong>
          </div>
        </div>
        <div v-else-if="report?.result" class="report-modal-no-grading">
          채점 결과 없음
        </div>
        <button type="button" class="report-modal-button" @click="$emit('close')">
          메인 화면으로
        </button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  report: { type: Object, default: null }
})
defineEmits(['close'])

const passRate = computed(() => {
  const ec = props.report?.evaluationContext
  if (!ec?.totalCount || ec.totalCount === 0) return 0
  const p = ec.passedCount ?? 0
  return Math.round((p / ec.totalCount) * 100)
})

function formatSolveTime(seconds) {
  if (seconds == null) return ''
  if (seconds < 60) return `${seconds}초`
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return s ? `${m}분 ${s}초` : `${m}분`
}

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function formatLanguage(lang) {
  const map = { PYTHON: 'Python3', JAVA: 'Java', JAVASCRIPT: 'JavaScript', CPP: 'C++' }
  return map[lang] ?? lang ?? '-'
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

.report-modal-section {
  margin-bottom: 1rem;
}

.report-modal-section-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-farm-green, #5e8d48);
  margin: 0 0 0.5rem 0;
}

.report-modal-problem-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-farm-brown-dark, #2d2a26);
  margin: 0 0 0.25rem 0;
  line-height: 1.4;
}

.report-modal-meta-text {
  font-size: 0.85rem;
  color: var(--color-farm-brown, #4e3b2a);
  margin: 0.15rem 0 0 0;
}

.report-modal-hint-contents {
  margin-top: 0.5rem;
}

.report-modal-hint-item {
  font-size: 0.9rem;
  color: var(--color-farm-brown-dark, #2d2a26);
  margin: 0.25rem 0 0 0;
  padding-left: 0.5rem;
  border-left: 2px solid var(--color-farm-green-light);
}

.report-modal-code {
  font-size: 0.8rem;
  font-family: ui-monospace, monospace;
  background: var(--color-farm-cream);
  padding: 0.75rem;
  border-radius: 0.5rem;
  overflow-x: auto;
  margin: 0;
  white-space: pre;
  color: var(--color-farm-brown-dark);
}

.report-modal-meta {
  font-size: 0.8rem;
  color: var(--color-farm-brown, #4e3b2a);
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

.report-modal-grading {
  margin-bottom: 1.25rem;
  padding: 1rem;
  background: rgba(94, 141, 72, 0.08);
  border-radius: 0.75rem;
  border: 1px solid rgba(94, 141, 72, 0.2);
}

.report-modal-grading-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--color-farm-green, #5e8d48);
  margin: 0 0 0.5rem 0;
}

.report-modal-grading-summary {
  font-size: 0.95rem;
  color: var(--color-farm-brown-dark, #2d2a26);
  margin-bottom: 0.25rem;
}

.report-modal-pass-count {
  font-weight: 600;
}

.report-modal-pass-rate {
  color: var(--color-farm-brown, #4e3b2a);
}

.report-modal-fail-reason {
  font-size: 0.9rem;
  color: #c0392b;
  margin-top: 0.5rem;
}

.report-modal-diff {
  font-size: 0.85rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(0, 0, 0, 0.04);
  border-radius: 0.5rem;
}

.report-modal-diff-line,
.report-modal-diff-expected,
.report-modal-diff-actual {
  margin: 0.25rem 0 0 0;
  color: var(--color-farm-brown-dark, #2d2a26);
}

.report-modal-diff-actual {
  color: #c0392b;
}

.report-modal-xp {
  font-size: 0.95rem;
  color: var(--color-farm-brown-dark, #2d2a26);
  margin-top: 0.75rem;
}

.report-modal-xp strong {
  color: var(--color-farm-green, #5e8d48);
}

.report-modal-no-grading {
  font-size: 0.875rem;
  color: var(--color-farm-brown, #4e3b2a);
  margin-bottom: 1rem;
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
