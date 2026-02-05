<template>
  <Teleport to="body">
    <div v-if="show" class="modal modal-open" @click.self="requireGoToMain ? undefined : $emit('close', false)">
      <div class="modal-box max-w-2xl max-h-[90vh] overflow-y-auto p-0 bg-[var(--color-farm-paper)] border border-[var(--color-farm-cream)] shadow-xl">
        <!-- Header -->
        <div class="flex items-center justify-between sticky top-0 z-10 px-6 py-4 bg-[var(--color-farm-paper)] border-b border-[var(--color-farm-cream)]">
          <div class="flex items-center gap-3">
            <h2 class="text-xl font-bold text-[var(--color-farm-green-dark)]">📋 Report</h2>
            <span
              v-if="report?.result?.resultType"
              class="badge badge-lg font-semibold"
              :class="resultTypeBadgeClass(report.result.resultType)"
            >
              {{ resultTypeLabel(report.result.resultType) }}
            </span>
          </div>
          <button
            v-if="!requireGoToMain"
            type="button"
            class="btn btn-ghost btn-sm btn-square text-[var(--color-farm-brown)] hover:bg-[var(--color-farm-cream)] hover:text-[var(--color-farm-brown-dark)]"
            aria-label="모달 닫기"
            @click="$emit('close', false)"
          >
            <iconify-icon icon="mdi:close" class="text-xl"></iconify-icon>
          </button>
        </div>

        <div class="px-6 pb-6">
          <!-- Loading: 스켈레톤 + 리포트 생성중 문구 -->
          <div v-if="reportLoading" class="py-6">
            <p class="text-center text-[var(--color-farm-brown)] font-semibold mb-6">리포트 생성중...</p>
            <div class="report-modal-skeleton space-y-5">
              <div class="h-20 rounded-xl bg-[var(--color-farm-cream)]/50 animate-pulse" />
              <div class="h-4 w-3/4 rounded bg-[var(--color-farm-cream)]/50 animate-pulse" />
              <div class="h-4 w-1/2 rounded bg-[var(--color-farm-cream)]/50 animate-pulse" />
              <div class="h-24 rounded-lg bg-[var(--color-farm-cream)]/50 animate-pulse" />
              <div class="h-4 w-full rounded bg-[var(--color-farm-cream)]/50 animate-pulse" />
              <div class="h-4 w-5/6 rounded bg-[var(--color-farm-cream)]/50 animate-pulse" />
              <div class="h-16 rounded-lg bg-[var(--color-farm-cream)]/50 animate-pulse" />
            </div>
          </div>
          <div v-else-if="!report?.result" class="flex items-center justify-center py-12">
            <p class="text-[var(--color-farm-brown)]">불러오지 못했습니다.</p>
          </div>

          <template v-else>
            <!-- Feedback: 강조 카드 (가장 눈에 띄게) -->
            <div
              v-if="report?.result?.feedback"
              class="my-6 rounded-xl border-2 border-[var(--color-farm-green-light)] bg-[var(--color-farm-cream)]/60 p-5"
            >
              <div class="flex items-center gap-2 mb-3">
                <iconify-icon icon="mdi:message-text" class="text-2xl text-[var(--color-farm-green)]"></iconify-icon>
                <h3 class="text-base font-bold text-[var(--color-farm-green-dark)]">선생님 피드백</h3>
              </div>
              <p class="text-[var(--color-farm-brown-dark)] text-base leading-relaxed whitespace-pre-wrap break-words m-0">
                {{ report.result.feedback }}
              </p>
            </div>
            <div v-else-if="report?.result" class="mb-6 rounded-xl border border-[var(--color-farm-cream)] bg-[var(--color-farm-cream)]/40 p-4">
              <p class="text-[var(--color-farm-brown)] text-sm m-0">제출이 완료되었습니다.</p>
            </div>

            <!-- 문제 정보 -->
            <div v-if="report?.result?.problem" class="mb-5 p-4 rounded-lg bg-[var(--color-farm-cream)]/50 border border-[var(--color-farm-cream)]">
              <h4 class="text-sm font-bold text-[var(--color-farm-green-dark)] mb-2">문제 정보</h4>
              <p class="font-semibold text-[var(--color-farm-brown-dark)] text-base mb-1">{{ report.result.problem.title }}</p>
              <p v-if="report.result.problem.difficulty != null" class="text-sm text-[var(--color-farm-brown)] m-0">난이도 {{ formatDifficulty(report.result.problem.difficulty) }}</p>
              <p v-if="report.result.problem.algorithm" class="text-sm text-[var(--color-farm-brown)] mt-0.5">알고리즘 {{ formatAlgorithm(report.result.problem.algorithm) }}</p>
            </div>

            <!-- 학습 정보 -->
            <div v-if="report?.result?.learning && (report.result.learning.usedHintCount != null || report.result.learning.failCount != null)" class="mb-5">
              <h4 class="text-sm font-bold text-[var(--color-farm-green-dark)] mb-1.5">학습 정보</h4>
              <p v-if="report.result.learning.usedHintCount != null" class="text-sm text-[var(--color-farm-brown)] m-0">사용한 힌트 수: {{ report.result.learning.usedHintCount }}개</p>
              <p v-if="report.result.learning.failCount != null" class="text-sm text-[var(--color-farm-brown)] mt-0.5">실패 횟수: {{ report.result.learning.failCount }}회</p>
            </div>

            <!-- 힌트 -->
            <div v-if="report?.result && (report.result.hintCount != null || (Array.isArray(report.result.hintContents) && report.result.hintContents.length))" class="mb-5">
              <h4 class="text-sm font-bold text-[var(--color-farm-green-dark)] mb-1.5">힌트</h4>
              <p v-if="report.result.hintCount != null" class="text-sm text-[var(--color-farm-brown)] m-0">받은 힌트 수: {{ report.result.hintCount }}개</p>
              <div v-if="Array.isArray(report.result.hintContents) && report.result.hintContents.length" class="mt-2 space-y-1.5">
                <p v-for="(h, i) in report.result.hintContents" :key="i" class="text-sm text-[var(--color-farm-brown-dark)] pl-3 border-l-2 border-[var(--color-farm-green-light)] m-0">
                  {{ h }}
                </p>
              </div>
            </div>

            <!-- 메타: 풀이 시간, 날짜 -->
            <div v-if="report?.result" class="flex flex-wrap gap-x-3 gap-y-0.5 text-sm text-[var(--color-farm-brown)] mb-4">
              <span v-if="report.result.solveTime != null">풀이 시간 {{ formatSolveTime(report.result.solveTime) }}</span>
              <span v-if="report.result.createdAt">풀이 날짜 {{ formatDate(report.result.createdAt) }}</span>
            </div>

            <!-- 제출 코드 -->
            <div v-if="report?.result?.code != null && report.result.code !== ''" class="mb-5">
              <h4 class="text-sm font-bold text-[var(--color-farm-green-dark)] mb-2">제출 코드</h4>
              <pre class="p-4 rounded-lg bg-[var(--color-farm-cream)] border border-[var(--color-farm-cream)] text-xs font-mono text-[var(--color-farm-brown-dark)] overflow-x-auto m-0 whitespace-pre">{{ report.result.code }}</pre>
            </div>

            <!-- 실행/메모리/언어 -->
            <div v-if="report?.result" class="flex flex-wrap gap-x-3 gap-y-0.5 text-sm text-[var(--color-farm-brown)] mb-5">
              <span v-if="report.result.execTime != null">실행 {{ report.result.execTime }}ms</span>
              <span v-if="report.result.memory != null">메모리 {{ report.result.memory }}MB</span>
              <span v-if="report.result.language">사용 언어 {{ formatLanguage(report.result.language) }}</span>
            </div>

            <!-- 개선 방향 -->
            <div v-if="report?.result?.improvementDirection" class="mb-5 p-4 rounded-lg bg-[var(--color-farm-cream)]/50 border border-[var(--color-farm-cream)]">
              <h4 class="text-sm font-bold text-[var(--color-farm-green-dark)] mb-1.5">개선 방향</h4>
              <p class="text-sm text-[var(--color-farm-brown-dark)] leading-relaxed whitespace-pre-wrap m-0">{{ report.result.improvementDirection }}</p>
            </div>

            <!-- 채점·결과 -->
            <div v-if="report?.evaluationContext || report?.xp != null || report?.awardedPoints != null" class="mb-5 p-4 rounded-xl bg-[var(--color-farm-green)]/10 border border-[var(--color-farm-green)]/30">
              <h4 class="text-sm font-bold text-[var(--color-farm-green-dark)] mb-2">채점·결과</h4>
              <div v-if="report.evaluationContext" class="text-[var(--color-farm-brown-dark)]">
                <span class="font-semibold">{{ report.evaluationContext.passedCount ?? 0 }} / {{ report.evaluationContext.totalCount ?? 0 }}개 통과</span>
                <span v-if="report.evaluationContext.totalCount > 0" class="text-[var(--color-farm-brown)]"> ({{ passRate }}%)</span>
              </div>
              <p v-if="report.evaluationContext?.failReason" class="text-sm text-[var(--color-farm-point)] mt-2 m-0">{{ report.evaluationContext.failReason }}</p>
              <div v-if="report.evaluationContext?.failedLineNo != null" class="mt-2 p-3 rounded-lg bg-black/5 text-sm">
                <p class="m-0 text-[var(--color-farm-brown-dark)]">실패한 줄: {{ report.evaluationContext.failedLineNo }}</p>
                <p v-if="report.evaluationContext.expectedLine != null" class="mt-1 m-0 text-[var(--color-farm-brown)]">기대값: {{ report.evaluationContext.expectedLine }}</p>
                <p v-if="report.evaluationContext.actualLine != null" class="mt-0.5 m-0 text-[var(--color-farm-point)]">출력: {{ report.evaluationContext.actualLine }}</p>
              </div>
              <p v-if="report.awardedPoints != null" class="text-sm text-[var(--color-farm-brown-dark)] mt-3 m-0">
                획득 포인트:
                <strong class="text-[var(--color-farm-green-dark)]">{{ report.awardedPoints }}</strong>
              </p>
              <p v-if="report.xp != null" class="text-sm text-[var(--color-farm-brown-dark)] mt-3 m-0">획득 XP: <strong class="text-[var(--color-farm-green-dark)]">{{ report.xp }}</strong></p>
            </div>
            <p v-else-if="report?.result" class="text-sm text-[var(--color-farm-brown)] mb-5">채점 결과 없음</p>
          </template>

          <!-- 메인 버튼 -->
          <button
            type="button"
            class="btn w-full mt-2 text-white border-none rounded-xl font-semibold bg-[var(--color-farm-green)] hover:bg-[var(--color-farm-green-dark)]"
            @click="$emit('close', true)"
          >
            {{ backButtonText || '메인 화면으로' }}
          </button>
        </div>
      </div>
      <div class="modal-backdrop bg-black/50" @click="requireGoToMain ? undefined : $emit('close', false)"></div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  report: { type: Object, default: null },
  reportLoading: { type: Boolean, default: false },
  reportLoadFailed: { type: Boolean, default: false },
  backButtonText: { type: String, default: '' },
  /** true면 X 버튼 숨김, 백드롭 클릭 무시 → 반드시 '메인 화면으로'로만 닫기 */
  requireGoToMain: { type: Boolean, default: false }
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

function resultTypeLabel(type) {
  const map = { SUCCESS: '정답', FAIL: '오답', GIVE_UP: '탈주' }
  return map[type] ?? type ?? '-'
}

function resultTypeBadgeClass(type) {
  const map = { SUCCESS: 'badge-success text-white', FAIL: 'badge-error text-white', GIVE_UP: 'badge-ghost' }
  return map[type] ?? 'badge-ghost'
}

function formatDifficulty(d) {
  if (d == null) return '-'
  if (typeof d === 'number') return `LEVEL${d}`
  return String(d)
}

function formatAlgorithm(algo) {
  const map = { BRUTEFORCE: '브루트포스', GREEDY: '그리디', DP: '동적 프로그래밍', BFS: 'BFS', DFS: 'DFS', BINARY_SEARCH: '이진 탐색', TWO_POINTER: '투 포인터', SORT: '정렬', GRAPH: '그래프', STRING: '문자열', MATH: '수학', IMPLEMENTATION: '구현' }
  return map[algo] ?? algo ?? '-'
}
</script>
