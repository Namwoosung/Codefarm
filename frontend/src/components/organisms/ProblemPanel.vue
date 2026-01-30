<template>
  <div class="flex flex-col h-full min-h-0 bg-[#FFE082] rounded-xl overflow-hidden">
    <!-- 탭: DaisyUI join -->
    <div class="join join-horizontal w-full flex-shrink-0 border-b border-base-300 bg-[#FFE082]">
      <button
        type="button"
        class="join-item btn btn-sm flex-1 gap-1.5 rounded-none border-base-300 bg-transparent text-[var(--color-farm-brown)] hover:bg-base-200/50 font-medium"
        :class="{ 'btn-active border-b-2 border-[var(--color-farm-green)] text-[var(--color-farm-green-dark)]': activeTab === 'problem' }"
        @click="activeTab = 'problem'"
      >
        <iconify-icon icon="mdi:book-open-variant" class="text-lg"></iconify-icon>
        {{ problem?.title || '문제' }}
      </button>
      <button
        type="button"
        class="join-item btn btn-sm flex-1 gap-1.5 rounded-none border-base-300 bg-transparent text-[var(--color-farm-brown)] hover:bg-base-200/50 font-medium"
        :class="{ 'btn-active border-b-2 border-[var(--color-farm-green)] text-[var(--color-farm-green-dark)]': activeTab === 'results' }"
        @click="activeTab = 'results'; loadResults()"
      >
        <iconify-icon icon="mdi:format-list-bulleted" class="text-lg"></iconify-icon>
        제출 내역
      </button>
    </div>

    <!-- 문제 탭 -->
    <template v-if="activeTab === 'problem'">
      <div class="flex flex-col flex-1 min-h-0">
        <div class="flex-1 min-h-0 overflow-y-auto p-4 pl-5 bg-base-100 mx-2 mb-2 rounded-lg shadow-sm border border-[rgba(128,80,160,0.18)] text-sm font-normal text-[#1a1a1a]">
          <div class="mb-4">
            <span class="text-[0.875rem] font-normal text-[var(--color-farm-brown)]"># {{ problem?.problemId || '로딩 중...' }}</span>
          </div>
          <h2 class="text-xl font-bold text-[var(--color-farm-brown-dark)] mb-6">
            {{ problem?.title || '로딩 중...' }}
          </h2>
          <div class="space-y-3 mb-6">
            <div class="flex items-center gap-2 text-[var(--color-farm-brown-dark)] text-[0.875rem]">
              <iconify-icon icon="mdi:chart-line" class="text-xl text-[var(--color-farm-green)]"></iconify-icon>
              <span>획득 점수 <span class="font-semibold">{{ getDifficultyScore(problem?.difficulty) }}점</span></span>
            </div>
            <div class="flex items-center gap-2 text-[var(--color-farm-brown-dark)] text-[0.875rem]">
              <iconify-icon icon="mdi:clock-outline" class="text-xl text-[var(--color-farm-green)]"></iconify-icon>
              <span>실행 제한 시간 <span class="font-semibold">{{ problem?.timeLimit || 0 }}초</span></span>
            </div>
            <div class="flex items-center gap-2 text-[var(--color-farm-brown-dark)] text-[0.875rem]">
              <iconify-icon icon="mdi:harddisk" class="text-xl text-[var(--color-farm-green)]"></iconify-icon>
              <span>메모리 제한 <span class="font-semibold">{{ formatMemory(problem?.memoryLimit) }}</span></span>
            </div>
            <div v-if="problem?.algorithm" class="flex items-center gap-2 text-[var(--color-farm-brown-dark)] text-[0.875rem]">
              <iconify-icon icon="mdi:tag-multiple" class="text-xl text-[var(--color-farm-green)]"></iconify-icon>
              <span>알고리즘 <span class="font-semibold">{{ formatAlgorithm(problem.algorithm) }}</span></span>
            </div>
          </div>
          <div v-if="problem?.concept" class="mb-6">
            <h3 class="text-[0.9375rem] font-semibold text-[var(--color-farm-brown-dark)] mb-2">개념</h3>
            <div class="bg-base-200/60 p-4 rounded-lg text-[var(--color-farm-brown-dark)] whitespace-pre-wrap leading-relaxed text-[0.875rem]">
              {{ problem.concept }}
            </div>
          </div>
          <div class="mb-6">
            <div class="text-[var(--color-farm-brown-dark)] whitespace-pre-wrap leading-relaxed text-[0.875rem]">
              {{ problem?.description || '문제 설명을 불러오는 중...' }}
            </div>
          </div>
          <div v-if="problem?.inputDescription" class="mb-6">
            <h3 class="text-[0.9375rem] font-semibold text-[var(--color-farm-brown-dark)] mb-2">입력 설명</h3>
            <div class="bg-base-200/60 p-4 rounded-lg text-[var(--color-farm-brown-dark)] whitespace-pre-wrap leading-relaxed text-[0.875rem]">
              {{ problem.inputDescription }}
            </div>
          </div>
          <div v-if="problem?.outputDescription" class="mb-6">
            <h3 class="text-[0.9375rem] font-semibold text-[var(--color-farm-brown-dark)] mb-2">출력 설명</h3>
            <div class="bg-base-200/60 p-4 rounded-lg text-[var(--color-farm-brown-dark)] whitespace-pre-wrap leading-relaxed text-[0.875rem]">
              {{ problem.outputDescription }}
            </div>
          </div>
          <div v-if="problem?.exampleInput || problem?.exampleOutput" class="mb-6 space-y-4">
            <div>
              <h3 class="text-[0.9375rem] font-semibold text-[var(--color-farm-brown-dark)] mb-2">예제 입력</h3>
              <div class="bg-base-200 p-4 rounded-lg font-mono text-[0.8125rem] text-[var(--color-farm-brown-dark)] whitespace-pre-wrap">
                {{ problem.exampleInput }}
              </div>
            </div>
            <div>
              <h3 class="text-[0.9375rem] font-semibold text-[var(--color-farm-brown-dark)] mb-2">예제 출력</h3>
              <div class="bg-base-200 p-4 rounded-lg font-mono text-[0.8125rem] text-[var(--color-farm-brown-dark)] whitespace-pre-wrap">
                {{ problem.exampleOutput }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 제출 내역 탭 -->
    <div v-show="activeTab === 'results'" class="flex flex-col flex-1 min-h-0 bg-base-100 text-[var(--color-farm-brown-dark)] p-4">
      <p class="text-xs text-[var(--color-farm-brown)] mb-2 py-1">현재 표시되는 제출 내역은 임시 데이터이며, 차후 백엔드 API와 연동될 예정입니다.</p>
      <div class="flex items-center justify-between pb-3 border-b border-base-300 flex-shrink-0">
        <span class="text-sm text-[var(--color-farm-brown)]">{{ resultsList.length }}개의 제출</span>
        <button type="button" class="btn btn-ghost btn-sm gap-1.5 text-[var(--color-farm-brown)] hover:text-[var(--color-farm-brown-dark)] hover:bg-base-200" @click="loadResults" :disabled="resultsLoading">
          <iconify-icon icon="mdi:refresh" class="text-base" :class="{ 'animate-spin': resultsLoading }"></iconify-icon>
          새로고침
        </button>
      </div>
      <div class="flex-1 min-h-0 overflow-y-auto mt-2">
        <table class="table table-pin-rows table-xs">
          <thead>
            <tr class="bg-base-100 sticky top-0 z-10">
              <th class="text-left font-semibold text-[var(--color-farm-brown)]">제출일시</th>
              <th class="text-left font-semibold text-[var(--color-farm-brown)]">언어</th>
              <th class="text-left font-semibold text-[var(--color-farm-brown)]">채점 내역</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in resultsList"
              :key="row.resultId ?? idx"
              class="hover:bg-base-200/50"
              :class="{ 'cursor-pointer': row.hasReport && row.resultId }"
              @click="row.hasReport && row.resultId ? emit('open-report', row.resultId) : null"
            >
              <td class="py-2">
                <span class="mr-1">{{ formatResultDate(row.createdAt) }}</span>
                <iconify-icon v-if="row.hasReport && row.resultId" icon="mdi:chevron-right" class="inline-block align-middle text-[var(--color-farm-brown)]"></iconify-icon>
              </td>
              <td>{{ formatLanguage(row.language) }}</td>
              <td>
                <span class="inline-flex items-center gap-1 badge badge-sm" :class="resultTypeClass(row.resultType)">
                  <iconify-icon v-if="row.resultType === 'SUCCESS'" icon="mdi:check-circle" class="text-base"></iconify-icon>
                  {{ resultTypeLabel(row.resultType) }} {{ row.accuracy }} / 100
                </span>
              </td>
            </tr>
            <tr v-if="resultsList.length === 0 && !resultsLoading">
              <td colspan="3" class="text-center text-[var(--color-farm-brown)] py-8">제출 내역이 없습니다.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProblemDetail } from '@/api/problem'
import { useIdeStore } from '@/stores/ide'
import { getSessionResultsList, getMockSessionResults } from '@/api/session'

const emit = defineEmits(['open-report'])
const route = useRoute()
const ideStore = useIdeStore()
const problem = ref(null)

const activeTab = ref('problem')
const resultsList = ref([])
const resultsLoading = ref(false)

// 난이도에 따른 점수 계산 (임시)
const getDifficultyScore = (difficulty) => {
  const scoreMap = {
    'LEVEL1': 30,
    'LEVEL2': 50,
    'LEVEL3': 70,
    'LEVEL4': 100,
    'LEVEL5': 150
  }
  return scoreMap[difficulty] || 30
}

// 메모리 포맷팅
const formatMemory = (memoryMB) => {
  if (!memoryMB) return '0MiB'
  return `${memoryMB.toLocaleString()}MiB`
}

// 알고리즘 표시명 (예: BRUTEFORCE → 브루트포스)
const formatAlgorithm = (algorithm) => {
  const map = {
    BRUTEFORCE: '브루트포스',
    GREEDY: '그리디',
    DP: '동적 프로그래밍',
    BFS: 'BFS',
    DFS: 'DFS',
    BINARY_SEARCH: '이진 탐색',
    TWO_POINTER: '투 포인터',
    SORT: '정렬',
    GRAPH: '그래프',
    STRING: '문자열',
    MATH: '수학',
    IMPLEMENTATION: '구현'
  }
  return map[algorithm] ?? algorithm ?? '-'
}

// 제출 내역: 결과 타입 라벨
const resultTypeLabel = (resultType) => {
  const map = { SUCCESS: '정답', FAIL: '오답', GIVE_UP: '탈주' }
  return map[resultType] ?? resultType
}

// 제출 내역: 결과 타입별 badge 클래스 (DaisyUI)
const resultTypeClass = (resultType) => {
  const map = { SUCCESS: 'badge-success text-white', FAIL: 'badge-error text-white', GIVE_UP: 'badge-ghost text-base-content' }
  return map[resultType] ?? 'badge-ghost'
}

// 제출일시 포맷 (YYYY-MM-DD HH:mm:ss)
const formatResultDate = (iso) => {
  if (!iso) return '-'
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
}

// 언어 표시명
const formatLanguage = (lang) => {
  const map = { PYTHON: 'Python3', JAVA: 'Java', JAVASCRIPT: 'JavaScript', CPP: 'C++' }
  return map[lang] ?? lang ?? '-'
}

// 결과 목록 로드 (API 실패/빈 배열 시 목 데이터 사용)
const loadResults = async () => {
  const sid = ideStore.sessionId
  resultsLoading.value = true
  try {
    const list = await getSessionResultsList(sid)
    resultsList.value = list?.length ? list : getMockSessionResults()
  } catch (_) {
    resultsList.value = getMockSessionResults()
  } finally {
    resultsLoading.value = false
  }
}

// 문제 상세 정보 로드
const loadProblem = async () => {
  try {
    const problemId = route.params.id
    const data = await getProblemDetail(problemId)
    problem.value = data.problem
  } catch (error) {
    console.error('문제를 불러오는 중 오류가 발생했습니다:', error)
  }
}

onMounted(() => {
  loadProblem()
})
</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}
.overflow-y-auto::-webkit-scrollbar-track {
  background: var(--color-farm-cream);
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: var(--color-farm-green-light);
  border-radius: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: var(--color-farm-green);
}
</style>
