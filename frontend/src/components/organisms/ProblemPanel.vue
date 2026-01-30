<template>
  <div class="problem-panel">
    <!-- 탭: 문제 | 제출 내역 (프로그래머스 스타일) -->
    <div class="problem-tabs">
      <button
        type="button"
        class="problem-tab"
        :class="{ 'problem-tab-active': activeTab === 'problem' }"
        @click="activeTab = 'problem'"
      >
        <iconify-icon icon="mdi:book-open-variant" class="problem-tab-icon"></iconify-icon>
        {{ problem?.title || '문제' }}
      </button>
      <button
        type="button"
        class="problem-tab"
        :class="{ 'problem-tab-active': activeTab === 'results' }"
        @click="activeTab = 'results'; loadResults()"
      >
        <iconify-icon icon="mdi:format-list-bulleted" class="problem-tab-icon"></iconify-icon>
        제출 내역
      </button>
    </div>

    <!-- 문제 탭 -->
    <div v-show="activeTab === 'problem'" class="problem-content">
      <!-- 문제 번호 -->
      <div class="mb-4">
        <span class="text-farm-brown text-lg font-medium"># {{ problem?.problemId || '로딩 중...' }}</span>
      </div>

      <!-- 문제 제목 -->
      <h2 class="text-2xl font-bold text-farm-brown-dark mb-6">
        {{ problem?.title || '로딩 중...' }}
      </h2>

      <!-- 문제 정보 (점수, 시간 제한, 메모리 제한) -->
      <div class="space-y-3 mb-6">
        <div class="flex items-center space-x-2 text-farm-brown-dark">
          <iconify-icon icon="mdi:chart-line" class="text-xl text-farm-green"></iconify-icon>
          <span>획득 점수 {{ getDifficultyScore(problem?.difficulty) }}점</span>
        </div>
        <div class="flex items-center space-x-2 text-farm-brown-dark">
          <iconify-icon icon="mdi:clock-outline" class="text-xl text-farm-green"></iconify-icon>
          <span>실행 제한 시간 {{ problem?.timeLimit || 0 }}초</span>
        </div>
        <div class="flex items-center space-x-2 text-farm-brown-dark">
          <iconify-icon icon="mdi:harddisk" class="text-xl text-farm-green"></iconify-icon>
          <span>메모리 제한 {{ formatMemory(problem?.memoryLimit) }}</span>
        </div>
      </div>

      <!-- 문제 설명 -->
      <div class="mb-6">
        <div class="text-farm-brown-dark whitespace-pre-wrap leading-relaxed">
          {{ problem?.description || '문제 설명을 불러오는 중...' }}
        </div>
      </div>

      <!-- 예제 입출력 (있는 경우) -->
      <div v-if="problem?.exampleInput || problem?.exampleOutput" class="mb-6 space-y-4">
        <div>
          <h3 class="text-lg font-semibold text-farm-brown-dark mb-2">예제 입력</h3>
          <div class="bg-farm-cream p-4 rounded-lg font-mono text-sm text-farm-brown-dark">
            {{ problem.exampleInput }}
          </div>
        </div>
        <div>
          <h3 class="text-lg font-semibold text-farm-brown-dark mb-2">예제 출력</h3>
          <div class="bg-farm-cream p-4 rounded-lg font-mono text-sm text-farm-brown-dark">
            {{ problem.exampleOutput }}
          </div>
        </div>
      </div>

      <!-- AI 선생님 채팅창 (수동 힌트) -->
      <div class="problem-chat-section">
        <div class="problem-chat-messages">
          <div v-if="chatMessages.length === 0" class="flex items-start space-x-3 mb-4">
            <div class="w-10 h-10 bg-farm-yellow rounded-full flex items-center justify-center flex-shrink-0">
              <iconify-icon icon="mdi:robot" class="text-xl text-farm-brown-dark"></iconify-icon>
            </div>
            <div class="flex-1">
              <p class="text-farm-brown-dark text-sm">
                도움이 필요하신가요? 어떤 부분에서 어렵다고 느끼셨나요?
              </p>
            </div>
          </div>
          <!-- 채팅 메시지 (질문 + 힌트) -->
          <div v-for="(msg, idx) in chatMessages" :key="idx" class="problem-chat-msg" :class="msg.role === 'user' ? 'problem-chat-msg-user' : 'problem-chat-msg-assistant'">
            <span class="problem-chat-msg-label">{{ msg.role === 'user' ? '나' : '힌트' }}</span>
            <p class="problem-chat-msg-text">{{ msg.text }}</p>
          </div>
          <div v-if="hintLoading" class="problem-chat-msg problem-chat-msg-assistant">
            <span class="problem-chat-msg-label">힌트</span>
            <p class="problem-chat-msg-text">💡 힌트 생성 중...</p>
          </div>
        </div>
        <!-- 질문 입력 + 전송 -->
        <form class="problem-chat-form" @submit.prevent="sendHint">
          <textarea
            v-model="chatInput"
            placeholder="어떤 부분에서 어려움을 느꼈는지 적어주세요..."
            class="problem-chat-input"
            rows="3"
            :disabled="hintLoading || hintRemaining <= 0"
            @keydown.enter.exact="onHintEnter"
          ></textarea>
          <div class="flex items-center justify-between mt-2">
            <span class="text-sm text-farm-brown">당근 수: {{ hintRemaining }}/{{ hintMax }}</span>
            <button
              type="submit"
              class="problem-chat-send"
              :disabled="!chatInput.trim() || hintLoading || hintRemaining <= 0"
            >
              <iconify-icon icon="mdi:send" class="text-xl"></iconify-icon>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 제출 내역 탭 (라이트 테마) -->
    <div v-show="activeTab === 'results'" class="problem-results-wrap">
      <p class="problem-results-disclaimer">현재 표시되는 제출 내역은 임시 데이터이며, 차후 백엔드 API와 연동될 예정입니다.</p>
      <div class="problem-results-header">
        <span class="problem-results-count">{{ resultsList.length }}개의 제출</span>
        <button type="button" class="problem-results-refresh" @click="loadResults" :disabled="resultsLoading">
          <iconify-icon icon="mdi:refresh" class="problem-results-refresh-icon" :class="{ 'problem-results-refresh-spin': resultsLoading }"></iconify-icon>
          새로고침
        </button>
      </div>
      <div class="problem-results-table-wrap">
        <table class="problem-results-table">
          <thead>
            <tr>
              <th>제출일시</th>
              <th>언어</th>
              <th>채점 내역</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="(row, idx) in resultsList"
              :key="row.resultId ?? idx"
              class="problem-results-row"
              :class="{ 'problem-results-row-clickable': row.hasReport && row.resultId }"
              @click="row.hasReport && row.resultId ? emit('open-report', row.resultId) : null"
            >
              <td>
                <span class="problem-results-datetime">{{ formatResultDate(row.createdAt) }}</span>
                <iconify-icon v-if="row.hasReport && row.resultId" icon="mdi:chevron-right" class="problem-results-chevron"></iconify-icon>
              </td>
              <td>{{ formatLanguage(row.language) }}</td>
              <td>
                <span class="problem-results-badge" :class="resultTypeClass(row.resultType)">
                  <iconify-icon v-if="row.resultType === 'SUCCESS'" icon="mdi:check-circle" class="problem-results-badge-icon"></iconify-icon>
                  {{ resultTypeLabel(row.resultType) }} {{ row.accuracy }} / 100
                </span>
              </td>
            </tr>
            <tr v-if="resultsList.length === 0 && !resultsLoading">
              <td colspan="3" class="problem-results-empty">제출 내역이 없습니다.</td>
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
import * as hintApi from '@/api/hint'

const props = defineProps({
  hintRemaining: { type: Number, default: 3 },
  hintMax: { type: Number, default: 3 }
})
const emit = defineEmits(['open-report', 'hint-used'])
const route = useRoute()
const ideStore = useIdeStore()
const problem = ref(null)
const chatInput = ref('')
const chatMessages = ref([])
const hintLoading = ref(false)

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

// 제출 내역: 결과 타입 라벨
const resultTypeLabel = (resultType) => {
  const map = { SUCCESS: '정답', FAIL: '오답', GIVE_UP: '탈주' }
  return map[resultType] ?? resultType
}

// 제출 내역: 결과 타입별 CSS 클래스
const resultTypeClass = (resultType) => {
  const map = { SUCCESS: 'result-success', FAIL: 'result-fail', GIVE_UP: 'result-giveup' }
  return map[resultType] ?? ''
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

// 엔터 시 전송 가능하면 전송, 아니면 줄바꿈 유지
function onHintEnter(e) {
  if (chatInput.value?.trim() && !hintLoading.value && props.hintRemaining > 0) {
    e.preventDefault()
    sendHint()
  }
}

// 수동 힌트 전송 (채팅창에서 질문 입력 후 전송)
async function sendHint() {
  const q = chatInput.value?.trim()
  if (!q || hintLoading.value || props.hintRemaining <= 0) return
  chatMessages.value.push({ role: 'user', text: q, createdAt: new Date().toISOString() })
  chatInput.value = ''
  hintLoading.value = true
  try {
    const sid = ideStore.sessionId
    const code = ideStore.getCode(route.params.id)
    const res = await hintApi.requestManualHint(sid, { userQuestion: q, code })
    const d = res?.data
    if (d) {
      chatMessages.value.push({ role: 'assistant', text: d.content, createdAt: d.createdAt })
      emit('hint-used', { usedHint: d.usedHint ?? 0, maxHint: d.maxHint ?? 3 })
    } else {
      chatMessages.value.push({ role: 'assistant', text: '힌트를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', createdAt: new Date().toISOString() })
    }
  } catch (_) {
    chatMessages.value.push({ role: 'assistant', text: '힌트를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', createdAt: new Date().toISOString() })
  } finally {
    hintLoading.value = false
  }
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
.problem-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 탭 (프로그래머스 스타일) */
.problem-tabs {
  display: flex;
  border-bottom: 1px solid var(--color-farm-cream);
  background: var(--color-farm-paper);
  flex-shrink: 0;
}

.problem-tab {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-farm-brown);
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s;
}

.problem-tab:hover {
  color: var(--color-farm-brown-dark);
}

.problem-tab-active {
  color: var(--color-farm-green-dark);
  border-bottom-color: var(--color-farm-green);
}

.problem-tab-icon {
  font-size: 1.1rem;
}

.problem-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.problem-chat-section {
  border-top: 1px solid var(--color-farm-cream);
  padding: 0;
  background-color: var(--color-farm-paper);
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.problem-chat-messages {
  max-height: 280px;
  min-height: 120px;
  overflow-y: auto;
  margin-bottom: 0.5rem;
}
.problem-chat-msg {
  margin-bottom: 1rem;
  max-width: 90%;
}
.problem-chat-msg-user {
  margin-left: auto;
  text-align: right;
}
.problem-chat-msg-assistant {
  margin-right: auto;
  text-align: left;
}
.problem-chat-msg-label {
  font-size: 0.75rem;
  color: var(--color-farm-brown);
  display: block;
  margin-bottom: 0.25rem;
}
.problem-chat-msg-text {
  display: inline-block;
  padding: 0.5rem 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  margin: 0;
  text-align: left;
}
.problem-chat-msg-user .problem-chat-msg-text {
  background: var(--color-farm-green-light);
  color: var(--color-farm-brown-dark);
}
.problem-chat-msg-assistant .problem-chat-msg-text {
  background: var(--color-farm-cream);
  color: var(--color-farm-brown-dark);
}

.problem-chat-form {
  margin-top: 0.5rem;
}
.problem-chat-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-farm-cream);
  border-radius: 0.5rem;
  background: #fff;
  color: var(--color-farm-brown-dark);
  font-size: 0.9rem;
  resize: none;
  font-family: inherit;
}
.problem-chat-input:focus {
  outline: none;
  border-color: var(--color-farm-green);
}
.problem-chat-input:disabled {
  background: var(--color-farm-cream);
  cursor: not-allowed;
}
.problem-chat-send {
  padding: 0.5rem;
  background: var(--color-farm-green);
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}
.problem-chat-send:hover:not(:disabled) {
  background: var(--color-farm-green-dark);
}
.problem-chat-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 제출 내역 영역 (라이트 테마) */
.problem-results-wrap {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-farm-paper);
  color: var(--color-farm-brown-dark);
}

.problem-results-disclaimer {
  font-size: 0.75rem;
  color: var(--color-farm-brown);
  margin: 0 0 0.5rem 0;
  padding: 0.25rem 0;
  line-height: 1.4;
}

.problem-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0 0.75rem 0;
  border-bottom: 1px solid var(--color-farm-cream);
  flex-shrink: 0;
}

.problem-results-count {
  font-size: 0.9rem;
  color: var(--color-farm-brown);
}

.problem-results-refresh {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  color: var(--color-farm-brown);
  background: var(--color-farm-cream);
  border: 1px solid var(--color-farm-cream);
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s, border-color 0.2s, background 0.2s;
}

.problem-results-refresh:hover:not(:disabled) {
  color: var(--color-farm-brown-dark);
  border-color: var(--color-farm-green);
  background: rgba(126, 174, 95, 0.1);
}

.problem-results-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.problem-results-refresh-icon {
  font-size: 1rem;
}

.problem-results-refresh-spin {
  animation: problem-results-spin 0.8s linear infinite;
}

@keyframes problem-results-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.problem-results-table-wrap {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.problem-results-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.problem-results-table thead {
  position: sticky;
  top: 0;
  background: var(--color-farm-paper);
  z-index: 1;
}

.problem-results-table th {
  padding: 0.6rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--color-farm-brown);
  border-bottom: 1px solid var(--color-farm-cream);
}

.problem-results-table td {
  padding: 0.6rem 1rem;
  border-bottom: 1px solid var(--color-farm-cream);
  color: var(--color-farm-brown-dark);
}

.problem-results-row-clickable {
  cursor: pointer;
}

.problem-results-row-clickable:hover {
  background: var(--color-farm-cream);
}

.problem-results-datetime {
  margin-right: 0.25rem;
}

.problem-results-chevron {
  font-size: 0.9rem;
  color: var(--color-farm-brown);
  vertical-align: middle;
}

.problem-results-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.problem-results-badge-icon {
  font-size: 1rem;
}

.result-success {
  color: var(--color-farm-green-dark);
}

.result-fail {
  color: var(--color-farm-point);
}

.result-giveup {
  color: var(--color-farm-brown);
}

.problem-results-empty {
  text-align: center;
  color: var(--color-farm-brown);
  padding: 2rem !important;
}

/* 스크롤바 스타일링 */
.problem-content::-webkit-scrollbar,
.problem-results-table-wrap::-webkit-scrollbar {
  width: 8px;
}
.problem-chat-messages::-webkit-scrollbar {
  width: 6px;
}

.problem-content::-webkit-scrollbar-track,
.problem-results-table-wrap::-webkit-scrollbar-track {
  background: var(--color-farm-cream);
}
.problem-chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.problem-content::-webkit-scrollbar-thumb,
.problem-results-table-wrap::-webkit-scrollbar-thumb {
  background: var(--color-farm-green-light);
  border-radius: 4px;
}
.problem-chat-messages::-webkit-scrollbar-thumb {
  background: var(--color-farm-green-light);
  border-radius: 3px;
}

.problem-content::-webkit-scrollbar-thumb:hover,
.problem-results-table-wrap::-webkit-scrollbar-thumb:hover {
  background: var(--color-farm-green);
}
.problem-chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--color-farm-green);
}
</style>
