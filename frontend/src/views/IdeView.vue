<template>
  <div class="ide-container">
    <!-- 기능 바: Navbar 밑 -->
    <div class="ide-toolbar">
      <!-- 왼쪽: 뒤로가기 -->
      <button class="ide-back-button" @click="handleBack">
        <i class="pi pi-arrow-left"></i>
        <span>뒤로가기</span>
      </button>

      <!-- 오른쪽: 당근 3개 + 종 아이콘 -->
      <div class="ide-toolbar-right">
        <!-- 당근 아이콘 3개 -->
        <button
          v-for="i in 3"
          :key="i"
          class="ide-carrot-button"
          aria-label="당근"
        >
          <CarrotIcon />
        </button>
        <!-- 종 아이콘 -->
        <button class="ide-bell-button" aria-label="알림">
          <BellIcon />
        </button>
      </div>
    </div>

    <!-- 좌우 분할 레이아웃 -->
    <div class="ide-layout">
      <!-- 왼쪽 패널: 문제 설명 영역 -->
      <aside class="ide-panel-left" :style="{ width: leftPanelWidth + '%' }">
        <div class="ide-panel-content">
          <ProblemPanel />
        </div>
      </aside>

      <!-- 리사이저 바 -->
      <div 
        class="ide-resizer"
        @mousedown="startResize"
      ></div>

      <!-- 오른쪽 패널: 에디터 + 터미널 영역 -->
      <main class="ide-panel-right" :style="{ width: (100 - leftPanelWidth) + '%' }">
        <div class="ide-right-wrapper" :class="{ 'is-locked': !isLoggedIn }">
          <div class="ide-editor-container">
            <MonacoEditor />
          </div>
          
          <!-- 실행/제출 버튼 영역 -->
          <div class="ide-action-buttons">
            <button class="ide-submit-button" @click="handleSubmit">
              <span class="play-icon">▷</span>
              <span>제출하기</span>
            </button>
            <button
              class="ide-run-button"
              :disabled="isRunLoading"
              @click="handleRun"
            >
              <span v-if="isRunLoading" class="play-icon">⏱️</span>
              <span v-else class="play-icon">▷</span>
              <span>{{ isRunLoading ? '실행 중...' : '실행하기' }}</span>
            </button>
            <button class="ide-escape-button" @click="handleEscape">
              <EscapeIcon :size="20" />
              <span>탈주하기</span>
            </button>
          </div>
          
          <TerminalPanel ref="terminalPanel" />

          <!-- 로그인 필요 안내 오버레이 -->
          <div v-if="!isLoggedIn" class="ide-lock-overlay">
            <div class="ide-lock-card">
              <p class="ide-lock-title">로그인이 필요해요</p>
              <p class="ide-lock-desc">
                문제를 풀고 제출 결과를 확인하려면 먼저 로그인해주세요.
              </p>
              <div class="ide-lock-actions">
                <router-link to="/login" class="ide-lock-primary">
                  로그인하러 가기
                </router-link>
                <router-link to="/signup" class="ide-lock-secondary">
                  회원가입
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
import MonacoEditor from '@/components/organisms/MonacoEditor.vue'
import ProblemPanel from '@/components/organisms/ProblemPanel.vue'
import TerminalPanel from '@/components/organisms/TerminalPanel.vue'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'
import BellIcon from '@/components/atoms/BellIcon.vue'
import EscapeIcon from '@/components/atoms/EscapeIcon.vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { useIdeStore } from '@/stores/ide'
import * as sessionApi from '@/api/session'

const router = useRouter()
const route = useRoute()
const terminalPanel = ref(null)
const authStore = useAuthStore()
const ideStore = useIdeStore()
const { isLoggedIn } = storeToRefs(authStore)

// 백엔드 언어 코드 (에디터는 python, API는 PYTHON)
const API_LANGUAGE = 'PYTHON'

// 패널 리사이저 관련
const leftPanelWidth = ref(50) // 기본 50%
const isResizing = ref(false)
const isRunLoading = ref(false) // FR-CODE-004-1: 실행 중 버튼 비활성화
let snapshotIntervalId = null

const startResize = (e) => {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  e.preventDefault()
}

const handleResize = (e) => {
  if (!isResizing.value) return
  const container = document.querySelector('.ide-layout')
  if (!container) return
  const containerRect = container.getBoundingClientRect()
  const newLeftWidth = ((e.clientX - containerRect.left) / containerRect.width) * 100
  if (newLeftWidth >= 20 && newLeftWidth <= 80) {
    leftPanelWidth.value = newLeftWidth
  }
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
}

/** 세션 초기화: 활성 세션 조회 또는 세션 생성 후 최신 코드 로드 (라우트 id = 백엔드 problemId) */
async function initSession() {
  if (!isLoggedIn) return
  const problemId = Number(route.params.id)
  if (!problemId) return

  try {
    const { data: res } = await sessionApi.getActiveSession()
    const session = res?.data
    if (session) {
      if (session.problemId !== problemId) {
        await router.replace(`/ide/${session.problemId}`)
        return
      }
      ideStore.setSessionId(session.sessionId)
      await loadLatestCode(problemId)
      return
    }
  } catch (err) {
    // 404 = 활성 세션 없음 → 정상 흐름, 아래에서 createSession 호출
    if (err.response?.status !== 404) {
      if (terminalPanel.value) {
        terminalPanel.value.write(`활성 세션 조회 실패: ${err.response?.data?.message || err.message}\r\n`)
      }
      return
    }
  }

  try {
    const { data: res } = await sessionApi.createSession(problemId)
    ideStore.setSessionId(res?.data?.sessionId ?? null)
    if (res?.data?.sessionId) {
      ideStore.setCodeToDefault(problemId)
      if (terminalPanel.value) terminalPanel.value.write('세션이 생성되었습니다.\r\n')
    }
  } catch (err) {
    if (err.response?.status === 409) {
      const { data: activeRes } = await sessionApi.getActiveSession().catch(() => ({}))
      const active = activeRes?.data
      if (active?.problemId != null) {
        await router.replace(`/ide/${active.problemId}`)
      }
      return
    }
    if (terminalPanel.value) {
      const msg = err.response?.data?.message || err.message
      if (err.response?.status === 404 && msg?.includes('문제')) {
        terminalPanel.value.write('해당 문제를 백엔드에서 찾을 수 없습니다. 문제 ID가 서버에 등록되어 있는지 확인해 주세요.\r\n')
      } else {
        terminalPanel.value.write(`세션 생성 실패: ${msg}\r\n`)
      }
    }
  }
}

/** 최신 코드 조회 후 에디터에 반영 (해당 문제 ID에 저장) */
async function loadLatestCode(problemId) {
  const sid = ideStore.sessionId
  if (!sid) return
  try {
    const { data: res } = await sessionApi.getLatestCode(sid)
    if (res?.data?.code != null) {
      ideStore.updateCode(problemId, res.data.code)
    }
  } catch (err) {
    if (err.response?.status === 404) {
      // 저장된 코드 없음 → 기본 코드로 표시
      ideStore.setCodeToDefault(problemId)
    } else if (terminalPanel.value) {
      terminalPanel.value.write(`최신 코드 로드 실패: ${err.response?.data?.message || err.message}\r\n`)
    }
  }
}

/** 10초마다 코드 스냅샷 저장 (현재는 비활성화 - 테스트용으로 주석 처리 상태) */
function startSnapshotInterval() {
  // if (snapshotIntervalId) return
  // snapshotIntervalId = setInterval(async () => {
  //   const sid = ideStore.sessionId
  //   if (!sid || !isLoggedIn) return
  //   const code = ideStore.getCode(route.params.id)
  //   if (code == null || code === '') return
  //   try {
  //     await sessionApi.saveCodeSnapshot(sid, { language: API_LANGUAGE, code })
  //   } catch (err) {
  //     if (err.response?.status === 400 || err.response?.status === 403 || err.response?.status === 404) {
  //       clearInterval(snapshotIntervalId)
  //       snapshotIntervalId = null
  //     }
  //   }
  // }, 10_000)
}

/** 페이지 이탈 시 세션 종료 */
async function closeSessionOnLeave() {
  const sid = ideStore.sessionId
  if (!sid) return
  try {
    await sessionApi.closeSession(sid)
  } catch (_) {
    // 이탈 중이므로 무시
  }
  ideStore.clearSession()
}

onMounted(async () => {
  await initSession()
  startSnapshotInterval()
})

// 같은 IDE 페이지에서 문제 ID만 바뀐 경우(예: 활성 세션이 다른 문제일 때 리다이렉트) 세션 재초기화
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    await initSession()
    if (!snapshotIntervalId) startSnapshotInterval()
  }
})

onBeforeRouteLeave(async (to, from, next) => {
  await closeSessionOnLeave()
  if (snapshotIntervalId) {
    clearInterval(snapshotIntervalId)
    snapshotIntervalId = null
  }
  next()
})

onUnmounted(() => {
  document.removeEventListener('mousemove', handleResize)
  document.removeEventListener('mouseup', stopResize)
  if (snapshotIntervalId) {
    clearInterval(snapshotIntervalId)
    snapshotIntervalId = null
  }
})

const handleBack = async () => {
  if (!confirm('진짜 이 페이지를 벗어나시겠습니까?')) return
  await closeSessionOnLeave()
  if (snapshotIntervalId) {
    clearInterval(snapshotIntervalId)
    snapshotIntervalId = null
  }
  router.push('/')
}

const handleSubmit = async () => {
  if (!isLoggedIn) return
  const sid = ideStore.sessionId
  if (!sid) {
    if (terminalPanel.value) terminalPanel.value.write('세션이 없습니다. 페이지를 새로고침해 주세요.\r\n')
    return
  }
  const code = ideStore.getCode(route.params.id)
  if (terminalPanel.value) terminalPanel.value.write('제출 중...\r\n')
  try {
    const { data: res } = await sessionApi.submitCode(sid, { language: API_LANGUAGE, code })
    if (terminalPanel.value) {
      terminalPanel.value.write(res?.message || '제출 완료\r\n')
      if (res?.data) terminalPanel.value.write(JSON.stringify(res.data, null, 2) + '\r\n')
    }
  } catch (err) {
    if (terminalPanel.value) {
      terminalPanel.value.write(`제출 실패: ${err.response?.data?.message || err.message}\r\n`)
    }
  }
}

const handleRun = async () => {
  if (!isLoggedIn) return
  const sid = ideStore.sessionId
  if (!sid) {
    if (terminalPanel.value) terminalPanel.value.write('세션이 없습니다. 페이지를 새로고침해 주세요.\r\n')
    return
  }
  isRunLoading.value = true
  const code = ideStore.getCode(route.params.id)
  if (terminalPanel.value) terminalPanel.value.clear()
  if (terminalPanel.value) terminalPanel.value.write('실행 중...\r\n')
  try {
    const { data: res } = await sessionApi.runCode(sid, { language: API_LANGUAGE, code, input: '\n' })
    const d = res?.data
    const execTimeMs = d?.execTime ?? 0
    const execTimeSec = (execTimeMs / 1000).toFixed(2)
    if (terminalPanel.value) {
      if (d?.stdout) terminalPanel.value.write(d.stdout)
      if (d?.stderr) terminalPanel.value.write(d.stderr)
      if (d?.isTimeout) terminalPanel.value.write('Time Limit Exceeded\r\n')
      if (d?.isOom) terminalPanel.value.write('Memory Limit Exceeded\r\n')
      // FR-CODE-005-2, 005-3: 실행 결과 요약
      if (d?.isTimeout) {
        terminalPanel.value.write(`\r\n⏱️ 실행 시간 초과 (제한: 10초)\r\n`)
      } else if (res?.message === '실행 완료') {
        terminalPanel.value.write(`\r\n✅ 실행 성공 (${execTimeSec}초)\r\n`)
      } else {
        terminalPanel.value.write(`\r\n❌ 실행 실패 (${execTimeSec}초)\r\n`)
      }
    }
  } catch (err) {
    if (terminalPanel.value) {
      terminalPanel.value.write(`실행 실패: ${err.response?.data?.message || err.message}\r\n`)
      terminalPanel.value.write('❌ 실행 실패\r\n')
    }
  } finally {
    isRunLoading.value = false
  }
}

const handleEscape = async () => {
  if (!confirm('정말 탈주하시겠습니까?')) return
  const sid = ideStore.sessionId
  if (sid && isLoggedIn) {
    try {
      await sessionApi.giveUp(sid)
    } catch (_) {}
    ideStore.clearSession()
  }
  if (snapshotIntervalId) {
    clearInterval(snapshotIntervalId)
    snapshotIntervalId = null
  }
  router.push('/')
}
</script>

<style scoped>
.ide-container {
  width: 100%;
  height: calc(100vh - 4rem); /* 헤더 높이 제외 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: var(--color-farm-paper);
}

/* 기능 바 스타일 */
.ide-toolbar {
  width: 100%;
  height: 3.5rem; /* 56px */
  background-color: var(--color-farm-paper);
  border-bottom: 1px solid var(--color-farm-cream);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  flex-shrink: 0;
}

.ide-back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: var(--color-farm-brown-dark);
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.ide-back-button:hover {
  color: var(--color-farm-green);
}

.ide-back-button i {
  font-size: 1rem;
}

.ide-toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ide-carrot-button,
.ide-bell-button {
  padding: 0.5rem;
  color: var(--color-farm-brown-dark);
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}


.ide-carrot-button:hover,
.ide-bell-button:hover {
  color: var(--color-farm-green);
  background-color: var(--color-farm-cream);
}

.ide-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex: 1;
  overflow: hidden;
}

/* 데스크톱: 좌우 분할 */
@media (min-width: 768px) {
  .ide-layout {
    flex-direction: row;
  }
}

.ide-panel-left {
  width: 100%;
  height: 50%;
  background-color: var(--color-farm-paper);
  border-right: 1px solid var(--color-farm-cream);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 데스크톱: 왼쪽 패널 너비 - 동적으로 조절 가능 */
@media (min-width: 768px) {
  .ide-panel-left {
    height: 100%;
    flex-shrink: 0;
  }
}

.ide-panel-content {
  width: 100%;
  height: 100%;
  padding: 1.5rem;
}

.ide-panel-right {
  width: 100%;
  height: 50%;
  background-color: var(--color-farm-paper);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.ide-right-wrapper {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.ide-right-wrapper.is-locked .ide-editor-container,
.ide-right-wrapper.is-locked .ide-action-buttons,
.ide-right-wrapper.is-locked .terminal-panel {
  filter: blur(4px);
  pointer-events: none;
}

/* 리사이저 바 */
.ide-resizer {
  width: 4px;
  background-color: var(--color-farm-cream);
  cursor: col-resize;
  flex-shrink: 0;
  transition: background-color 0.2s;
  position: relative;
}

.ide-resizer:hover {
  background-color: var(--color-farm-green-light);
}

.ide-resizer::before {
  content: '';
  position: absolute;
  left: -2px;
  right: -2px;
  top: 0;
  bottom: 0;
  cursor: col-resize;
}

/* 데스크톱: 오른쪽 패널 너비 - 동적으로 조절 가능 */
@media (min-width: 768px) {
  .ide-panel-right {
    height: 100%;
    flex-shrink: 0;
  }
  
  .ide-resizer {
    display: block;
  }
}

@media (max-width: 767px) {
  .ide-resizer {
    display: none;
  }
}

.ide-editor-container {
  width: 100%;
  flex: 1;
  position: relative;
  min-height: 0; /* flexbox에서 overflow를 위해 필요 */
}

/* 실행/제출 버튼 영역 */
.ide-action-buttons {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: var(--color-farm-paper);
  border-top: 1px solid var(--color-farm-cream);
  border-bottom: 1px solid var(--color-farm-cream);
  flex-shrink: 0;
  justify-content: flex-start; /* 왼쪽 정렬 */
}

.ide-submit-button {
  width: 119px; /* 디자인 목업 기준 */
  padding: 0.5rem 1.25rem;
  background: linear-gradient(90deg, #7A5C3E 0%, #CDFF86 100%);
  color: white;
  border: none;
  border-radius: 18px; /* 매우 둥근 모서리 */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 36px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.ide-submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.ide-submit-button .play-icon {
  font-size: 0.875rem;
  color: white;
  font-weight: bold;
  line-height: 1;
}

.ide-run-button {
  width: 119px; /* 제출하기와 동일한 크기 */
  padding: 0.5rem 1.25rem;
  background-color: white;
  color: var(--color-farm-brown-dark);
  border: 1px solid #E0E0E0;
  border-radius: 18px; /* 매우 둥근 모서리 */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 36px;
  flex-shrink: 0;
}

.ide-run-button:hover:not(:disabled) {
  background-color: #FAFAFA;
  border-color: var(--color-farm-green);
}

.ide-run-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.ide-run-button .play-icon {
  font-size: 0.875rem;
  color: var(--color-farm-brown-dark);
  font-weight: bold;
  line-height: 1;
}

.ide-escape-button {
  width: auto;
  min-width: 100px;
  padding: 0.5rem 1rem;
  background-color: white;
  color: var(--color-farm-brown-dark);
  border: 1px solid #E0E0E0;
  border-radius: 18px; /* 매우 둥근 모서리 */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 36px;
  flex-shrink: 0;
}

.ide-escape-button:hover {
  background-color: #FAFAFA;
  border-color: var(--color-farm-point);
  color: var(--color-farm-point);
}

/* 탈주 아이콘 크기 조정 */
.ide-escape-button .escape-icon {
  font-size: 1.1rem;
}

/* 로그인 필요 오버레이 */
.ide-lock-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(245, 242, 232, 0.8);
  z-index: 10;
}

.ide-lock-card {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  max-width: 360px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.ide-lock-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--color-farm-brown-dark);
  margin-bottom: 0.5rem;
}

.ide-lock-desc {
  font-size: 0.9rem;
  color: #7a6a4a;
  margin-bottom: 1.25rem;
}

.ide-lock-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.ide-lock-primary,
.ide-lock-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  text-decoration: none;
}

.ide-lock-primary {
  background-color: var(--color-farm-green);
  color: #fff;
}

.ide-lock-primary:hover {
  background-color: var(--color-farm-green-dark);
}

.ide-lock-secondary {
  background-color: #fff;
  color: var(--color-farm-brown-dark);
  border: 1px solid #e0e0e0;
}

.ide-lock-secondary:hover {
  background-color: #fafafa;
}


/* 스크롤바 스타일링 */
.ide-panel-content::-webkit-scrollbar {
  width: 8px;
}

.ide-panel-content::-webkit-scrollbar-track {
  background: var(--color-farm-cream);
}

.ide-panel-content::-webkit-scrollbar-thumb {
  background: var(--color-farm-green-light);
  border-radius: 4px;
}

.ide-panel-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-farm-green);
}
</style>
