<template>
  <div class="flex flex-col w-full h-[calc(100vh-4rem)] max-h-[calc(100vh-4rem)] min-h-0 overflow-hidden bg-[var(--color-farm-paper)]">
    <!-- 로딩 모달 -->
    <div v-if="isInitializing" class="fixed inset-0 flex items-center justify-center bg-[rgba(245,242,232,0.9)] z-[100]">
      <div class="card bg-base-100 shadow-lg rounded-2xl p-6">
        <p class="text-base font-semibold text-[var(--color-farm-brown-dark)]">로딩중...</p>
      </div>
    </div>

    <!-- 툴바 -->
    <div class="flex items-center justify-between w-full h-14 px-6 flex-shrink-0 bg-[var(--color-farm-paper)] border-b border-[var(--color-farm-cream)]">
      <div class="flex items-center gap-4">
        <button type="button" class="btn btn-ghost btn-sm gap-2 text-[var(--color-farm-brown-dark)] hover:text-[var(--color-farm-green)]" @click="handleBack">
          <i class="pi pi-arrow-left"></i>
          <span>뒤로가기</span>
        </button>
        <span v-if="!isInitializing && (problemStartTime > 0 || timerStoppedAt != null)" class="text-sm font-medium text-[var(--color-farm-brown-dark)]">⏱️ {{ elapsedDisplay }}</span>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-0.5" aria-label="힌트 잔여 횟수">
          <span v-for="i in 3" :key="i" class="inline-flex transition-all duration-200" :class="{ 'grayscale opacity-55': hintUsed >= i }">
            <CarrotIcon />
          </span>
        </div>
        <button type="button" class="btn btn-ghost btn-sm btn-square" aria-label="알림">
          <BellIcon />
        </button>
      </div>
    </div>

    <!-- 레이아웃: [힌트 토글 | 힌트 패널? | 문제 | 리사이저 | 에디터+터미널] -->
    <div class="flex flex-row flex-1 min-h-0 overflow-hidden w-full">
      <!-- 힌트 패널 접기/펼치기 버튼 (접혀 있을 때만 보이는 펼치기 버튼) -->
      <div v-if="!hintPanelOpen" class="flex flex-shrink-0 items-stretch bg-[#FFE082] border-r border-base-300">
        <button
          type="button"
          class="btn btn-ghost btn-sm btn-square rounded-none h-full min-w-10 text-[var(--color-farm-brown-dark)] hover:bg-[rgba(0,0,0,0.06)]"
          title="힌트 패널 펼치기"
          @click="hintPanelOpen = true"
        >
          <iconify-icon icon="mdi:chevron-right" class="text-xl"></iconify-icon>
        </button>
      </div>

      <!-- 힌트 패널 (펼쳤을 때) -->
      <Transition name="hint-panel">
        <div v-show="hintPanelOpen" class="flex flex-shrink-0 w-[300px] min-w-[280px] max-w-[320px] h-full min-h-0 overflow-hidden">
          <HintPanel
            :hint-remaining="hintRemaining"
            :hint-max="hintMax"
            @hint-used="onHintUsedFromPanel"
            @close="hintPanelOpen = false"
          />
        </div>
      </Transition>

      <!-- 문제 + 에디터 영역 -->
      <div class="flex flex-1 min-w-0 min-h-0 overflow-hidden flex-row ide-main-wrap">
        <aside class="flex flex-col min-h-0 overflow-hidden border-r border-[var(--color-farm-cream)] flex-shrink-0" :style="{ width: leftPanelWidth + '%' }">
          <div class="w-full h-full min-h-0 overflow-hidden flex flex-col">
            <div class="join join-horizontal w-full h-10 min-h-10 flex flex-shrink-0 items-stretch bg-[#FFE082]">
              <button
                type="button"
                class="join-item btn btn-sm flex-1 gap-1.5 rounded-none border-base-300 bg-transparent text-[var(--color-farm-brown)] hover:bg-base-200/50 font-medium h-full"
                :class="{ 'btn-active border-b-2 border-[var(--color-farm-green)] text-[var(--color-farm-green-dark)]': problemPanelActiveTab === 'problem' }"
                @click="problemPanelActiveTab = 'problem'"
              >
                <iconify-icon icon="mdi:book-open-variant" class="text-lg"></iconify-icon>
                {{ problemTitle }}
              </button>
              <button
                type="button"
                class="join-item btn btn-sm flex-1 gap-1.5 rounded-none border-base-300 bg-transparent text-[var(--color-farm-brown)] hover:bg-base-200/50 font-medium h-full"
                :class="{ 'btn-active border-b-2 border-[var(--color-farm-green)] text-[var(--color-farm-green-dark)]': problemPanelActiveTab === 'results' }"
                @click="problemPanelActiveTab = 'results'"
              >
                <iconify-icon icon="mdi:format-list-bulleted" class="text-lg"></iconify-icon>
                제출 내역
              </button>
            </div>
            <ProblemPanel :active-tab="problemPanelActiveTab" @open-report="handleOpenReport" @problem-loaded="problemTitle = $event?.title ?? '문제'" />
          </div>
        </aside>

        <div class="w-1 flex-shrink-0 bg-[var(--color-farm-cream)] hover:bg-[var(--color-farm-green-light)] cursor-col-resize transition-colors ide-resizer-hit" @mousedown="startResize"></div>

        <main class="flex flex-col flex-1 min-w-0 min-h-0 overflow-hidden bg-[var(--color-farm-paper)] ide-panel-right" :style="{ width: (100 - leftPanelWidth) + '%' }">
          <div class="relative flex flex-col flex-1 min-h-0" :class="{ 'pointer-events-none': !isLoggedIn }">
            <div class="h-10 min-h-10 flex-shrink-0 flex items-center px-3 border-b border-[var(--color-farm-cream)] bg-[var(--color-farm-paper)]">
              <span class="text-sm font-medium text-[var(--color-farm-brown)]">코드</span>
            </div>
            <div class="flex-1 min-h-0 relative ide-editor-container" :class="{ 'blur-sm': !isLoggedIn }">
              <MonacoEditor />
            </div>
            <div v-if="isLoggedIn" class="absolute bottom-2 right-3 text-xs text-[var(--color-farm-brown)] text-right pointer-events-none">
              <div>{{ saveStatusText }}</div>
              <div v-if="recentlySentText" class="text-[0.7rem]">{{ recentlySentText }}</div>
              <div v-if="snapshotStoppedByIdle" class="text-[0.7rem] text-[var(--color-farm-point)]">코드 전송이 멈춘 상태입니다</div>
            </div>

            <div class="flex gap-3 px-4 py-2 flex-shrink-0 bg-[var(--color-farm-paper)] border-t border-b border-[var(--color-farm-cream)]">
              <button type="button" class="btn btn-sm h-9 min-w-[119px] bg-gradient-to-r from-[#7A5C3E] to-[#CDFF86] text-white border-none rounded-2xl shadow hover:shadow-md transition-all" @click="handleSubmit">
                <span class="font-bold">▷</span>
                <span>제출하기</span>
              </button>
              <button
                type="button"
                class="btn btn-sm btn-outline h-9 min-w-[119px] rounded-2xl border-neutral-300 text-[var(--color-farm-brown-dark)] hover:border-[var(--color-farm-green)]"
                :disabled="isRunLoading"
                @click="openRunInputModal"
              >
                <span v-if="isRunLoading" class="font-bold">⏱️</span>
                <span v-else class="font-bold">▷</span>
                <span>{{ isRunLoading ? '실행 중...' : '실행하기' }}</span>
              </button>
              <button type="button" class="btn btn-sm btn-outline h-9 min-w-[100px] rounded-2xl border-neutral-300 text-[var(--color-farm-brown-dark)] hover:border-[var(--color-farm-point)] hover:text-[var(--color-farm-point)]" @click="handleEscape">
                <EscapeIcon :size="20" />
                <span>탈주하기</span>
              </button>
            </div>

            <div class="h-1 flex-shrink-0 bg-[var(--color-farm-cream)] hover:bg-[var(--color-farm-green-light)] cursor-row-resize transition-colors" @mousedown="startResizeVertical"></div>
            <div class="flex-shrink-0 overflow-hidden bg-[var(--color-farm-paper)]" :style="{ height: terminalHeight + 'px' }">
              <TerminalPanel ref="terminalPanel" />
            </div>

            <div v-if="!isLoggedIn" class="absolute inset-0 flex items-center justify-center bg-[rgba(245,242,232,0.8)] z-10">
              <div class="card bg-base-100 shadow-xl rounded-2xl p-8 max-w-md text-center">
                <p class="text-lg font-bold text-[var(--color-farm-brown-dark)] mb-2">로그인이 필요해요</p>
                <p class="text-sm text-[#7a6a4a] mb-5">문제를 풀고 제출 결과를 확인하려면 먼저 로그인해주세요.</p>
                <div class="flex gap-3 justify-center">
                  <router-link to="/login" class="btn btn-sm rounded-full bg-[var(--color-farm-green)] text-white border-none hover:bg-[var(--color-farm-green-dark)]">로그인하러 가기</router-link>
                  <router-link to="/signup" class="btn btn-sm btn-outline rounded-full">회원가입</router-link>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>

    <ReportModal :show="showReportModal" :report="reportData" @close="onReportModalClose" />

    <!-- stdin 입력 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showRunInputModal" class="fixed inset-0 flex items-center justify-center bg-black/40 z-[9999]" @click.self="showRunInputModal = false">
          <div class="card bg-base-100 shadow-2xl rounded-xl p-6 min-w-[360px] max-w-[90vw] max-h-[85vh] flex flex-col border border-base-300">
            <h3 class="text-lg font-semibold text-[var(--color-farm-brown-dark)] mb-1">stdin 입력</h3>
            <p class="text-sm text-[#7a6a4a] mb-3">코드에서 input()으로 읽을 값을 입력하세요. 여러 줄 입력 가능.</p>
            <textarea
              v-model="runInputContent"
              class="textarea textarea-bordered w-full min-h-[120px] font-mono text-sm resize-y"
              placeholder="예: 4&#10;1 2 3 4&#10;5"
              rows="8"
            ></textarea>
            <div class="flex justify-end gap-3 mt-4">
              <button type="button" class="btn btn-ghost btn-sm" @click="showRunInputModal = false">취소</button>
              <button type="button" class="btn btn-sm bg-[var(--color-farm-green)] text-white border-none hover:bg-[var(--color-farm-green-dark)]" @click="confirmRunWithInput">실행</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 확인 모달 (탈주/페이지 이탈 등) -->
    <ConfirmModal
      :show="confirmState.show"
      :title="confirmState.title"
      :message="confirmState.message"
      :variant="confirmState.variant"
      :confirm-text="confirmState.confirmText"
      :cancel-text="confirmState.cancelText"
      @confirm="onConfirmModalConfirm"
      @cancel="onConfirmModalCancel"
    />

    <!-- 힌트 차감 토스트 -->
    <Transition name="toast">
      <div v-if="toastMessage" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[1100] w-[min(520px,calc(100vw-2rem))]">
        <div role="alert" class="alert alert-info alert-soft shadow-lg">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="h-6 w-6 shrink-0 stroke-current">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <span class="text-sm font-semibold">{{ toastMessage }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, watch } from 'vue'
import { useRouter, useRoute, onBeforeRouteLeave } from 'vue-router'
import MonacoEditor from '@/components/organisms/MonacoEditor.vue'
import HintPanel from '@/components/organisms/HintPanel.vue'
import ProblemPanel from '@/components/organisms/ProblemPanel.vue'
import TerminalPanel from '@/components/organisms/TerminalPanel.vue'
import ReportModal from '@/components/organisms/ReportModal.vue'
import HintModal from '@/components/organisms/HintModal.vue'
import ConfirmModal from '@/components/organisms/ConfirmModal.vue'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'
import BellIcon from '@/components/atoms/BellIcon.vue'
import EscapeIcon from '@/components/atoms/EscapeIcon.vue'
import { useAuthStore } from '@/stores/auth'
import { useIdeStore } from '@/stores/ide'
import * as sessionApi from '@/api/session'
import { getReportDetail, getMockReportData, buildReportFromSubmitResponse } from '@/api/reports'

const router = useRouter()
const route = useRoute()
const terminalPanel = ref(null)
const authStore = useAuthStore()
const ideStore = useIdeStore()
// 스토어 로그인 상태를 computed로 참조해 로그아웃 시에도 블러/오버레이 즉시 반영
const isLoggedIn = computed(() => !!authStore.token)

// 백엔드 언어 코드 (에디터는 python, API는 PYTHON)
const API_LANGUAGE = 'PYTHON'

// 패널 리사이저 관련
const leftPanelWidth = ref(50) // 기본 50%
const isResizing = ref(false)
const terminalHeight = ref(210) // 터미널 영역 높이 (px)
const isResizingVertical = ref(false)
const isRunLoading = ref(false) // FR-CODE-004-1: 실행 중 버튼 비활성화
const isInitializing = ref(true) // 메인→IDE 진입 시 세션/문제 로드 중
const showReportModal = ref(false)
const reportData = ref(null)
/** 제출 내역에서 열었을 때 true → 닫을 때 메인으로 이동하지 않음 */
const reportModalFromHistory = ref(false)
/** 리포트 '메인 화면으로' 클릭 시 true → 이탈 확인 창 건너뜀 (세션 이미 종료됨) */
const skipLeaveConfirm = ref(false)
/** 실행 시 stdin 입력 모달 */
const showRunInputModal = ref(false)
const runInputContent = ref('')
const hintUsed = ref(0)
const hintMax = ref(3)
const hintRemaining = computed(() => Math.max(0, hintMax.value - hintUsed.value))
/** 힌트(채팅) 패널 접기/펼치기 */
const hintPanelOpen = ref(true)
/** 문제 패널 탭 (problem | results) - 툴바에 표시 */
const problemPanelActiveTab = ref('problem')
const problemTitle = ref('문제')
/** 이번 진입에서 방금 생성한 세션 ID (getLatestCode 호출 생략용) */
const justCreatedSessionId = ref(null)
/** 힌트 차감 토스트 (FR-CODE-010-1) */
const toastMessage = ref('')
let toastTimer = null
/** confirm 대체 모달 (탈주/이탈) */
const confirmState = reactive({
  show: false,
  title: '',
  message: '',
  variant: 'warning', // 'info' | 'success' | 'warning' | 'error'
  confirmText: '확인',
  cancelText: '취소',
})
let confirmResolver = null

function requestConfirm({ title, message, variant = 'warning', confirmText = '확인', cancelText = '취소' } = {}) {
  confirmState.title = title ?? ''
  confirmState.message = message ?? ''
  confirmState.variant = variant
  confirmState.confirmText = confirmText
  confirmState.cancelText = cancelText
  confirmState.show = true

  return new Promise((resolve) => {
    confirmResolver = resolve
  })
}

function closeConfirm(result) {
  confirmState.show = false
  const r = confirmResolver
  confirmResolver = null
  if (typeof r === 'function') r(!!result)
}

function onConfirmModalConfirm() {
  closeConfirm(true)
}
function onConfirmModalCancel() {
  closeConfirm(false)
}
// FR-CODE-002-1: 저장 상태 표시
const lastSavedAt = ref(null)
const isSaveInProgress = ref(false)
const saveFailed = ref(false)
const isOnline = ref(typeof navigator !== 'undefined' ? navigator.onLine : true)
const lastStatusTick = ref(Date.now()) // "N초 전" 갱신용
/** FR-CODE-011: 문제 풀이 시작 시각 (타이머 표시용) */
const problemStartTime = ref(0)
/** 제출 성공 시 타이머 멈춘 시점의 경과 ms (null이면 타이머 동작 중) */
const timerStoppedAt = ref(null)
const snapshotStoppedByIdle = ref(false) // 10초 무입력으로 전송 중단 시 true (테스트 확인용)
let snapshotIntervalId = null
let statusTickIntervalId = null
const onOnline = () => { isOnline.value = true }
const onOffline = () => { isOnline.value = false }

// 제출 성공 여부 판별 유틸 (백엔드 스키마 확정 전, 대표 필드들만 체크)
const isSubmitSuccess = (res) => {
  const d = res?.data
  if (!d) return false
  if (typeof d.isSuccess === 'boolean') return d.isSuccess
  if (typeof d.allPassed === 'boolean') return d.allPassed
  if (typeof d.isAllSuccess === 'boolean') return d.isAllSuccess
  if (d.resultType === 'SUCCESS') return true
  return false
}

const startResize = (e) => {
  isResizing.value = true
  document.addEventListener('mousemove', handleResize)
  document.addEventListener('mouseup', stopResize)
  e.preventDefault()
}

const handleResize = (e) => {
  if (!isResizing.value) return
  const container = document.querySelector('.ide-main-wrap')
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

// 에디터-터미널 세로 리사이저
const TERMINAL_MIN_HEIGHT = 150
const TERMINAL_MAX_HEIGHT = 600
const startResizeVertical = (e) => {
  isResizingVertical.value = true
  document.addEventListener('mousemove', handleResizeVertical)
  document.addEventListener('mouseup', stopResizeVertical)
  e.preventDefault()
}
const handleResizeVertical = (e) => {
  if (!isResizingVertical.value) return
  const rightPanel = document.querySelector('.ide-panel-right')
  if (!rightPanel) return
  const rect = rightPanel.getBoundingClientRect()
  const newHeight = rect.bottom - e.clientY
  if (newHeight >= TERMINAL_MIN_HEIGHT && newHeight <= TERMINAL_MAX_HEIGHT) {
    terminalHeight.value = newHeight
  }
}
const stopResizeVertical = () => {
  isResizingVertical.value = false
  document.removeEventListener('mousemove', handleResizeVertical)
  document.removeEventListener('mouseup', stopResizeVertical)
}

// FR-CODE-002-1: "💾 저장됨 (3초 전)", "💾 저장 중...", "⚠️ 연결 끊김"
const saveStatusText = computed(() => {
  if (!isOnline.value) return '⚠️ 연결 끊김'
  if (isSaveInProgress.value) return '💾 저장 중...'
  if (saveFailed.value) return '⚠️ 연결 끊김'
  if (!lastSavedAt.value) return '💾 대기 중'
  const sec = Math.floor((lastStatusTick.value - lastSavedAt.value) / 1000)
  if (sec < 60) return `💾 저장됨 (${sec}초 전)`
  const min = Math.floor(sec / 60)
  return `💾 저장됨 (${min}분 전)`
})

// 테스트용: 방금 전송 완료 시 "코드가 전송되었습니다" (5초간 표시)
const recentlySentText = computed(() => {
  if (!lastSavedAt.value) return ''
  const elapsed = lastStatusTick.value - lastSavedAt.value
  if (elapsed < 5000) return '코드가 전송되었습니다'
  return ''
})

/** FR-CODE-011: 경과 시간 "⏱️ MM:SS" 또는 "⏱️ H:MM:SS" (제출 성공 시 멈춘 값 사용) */
const elapsedDisplay = computed(() => {
  const stopped = timerStoppedAt.value
  if (stopped != null) {
    const sec = Math.max(0, Math.floor(stopped / 1000))
    const m = Math.floor(sec / 60)
    const s = sec % 60
    const pad = (n) => String(n).padStart(2, '0')
    if (sec < 3600) return `${m}:${pad(s)}`
    const h = Math.floor(sec / 3600)
    return `${h}:${pad(m)}:${pad(s)}`
  }
  const start = problemStartTime.value
  if (!start) return '0:00'
  const sec = Math.max(0, Math.floor((lastStatusTick.value - start) / 1000))
  const m = Math.floor(sec / 60)
  const s = sec % 60
  const pad = (n) => String(n).padStart(2, '0')
  if (sec < 3600) return `${m}:${pad(s)}`
  const h = Math.floor(sec / 3600)
  return `${h}:${pad(m)}:${pad(s)}`
})

/** 세션 초기화: 활성 세션 조회 또는 세션 생성 후 최신 코드 로드 (라우트 id = 백엔드 problemId) */
async function initSession() {
  if (!isLoggedIn.value) return
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
      // 방금 이번 진입에서 생성한 세션이면 저장된 코드가 없으므로 latest 호출 생략
      if (session.sessionId === justCreatedSessionId.value) {
        ideStore.setCodeToDefault(problemId)
        justCreatedSessionId.value = null
      } else {
        await loadLatestCode(problemId)
      }
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
    const newSessionId = res?.data?.sessionId ?? null
    ideStore.setSessionId(newSessionId)
    if (newSessionId) {
      justCreatedSessionId.value = newSessionId
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

/** 페이지 이탈 전 한 번 더 코드 스냅샷 저장 (가능한 경우만) */
async function saveLatestSnapshotOnce() {
  const sid = ideStore.sessionId
  if (!sid || !isLoggedIn.value) return
  const code = ideStore.getCode(route.params.id)
  if (!code) return
  isSaveInProgress.value = true
  saveFailed.value = false
  try {
    await sessionApi.saveCodeSnapshot(sid, { language: API_LANGUAGE, code })
    lastSavedAt.value = Date.now()
    saveFailed.value = false
  } catch (_) {
    // 이탈 중이므로 실패해도 추가 처리는 하지 않음
    saveFailed.value = true
  } finally {
    isSaveInProgress.value = false
  }
}

const IDLE_STOP_MS = 10_000   // 10초 무입력 시 스냅샷 전송 중단
const SNAPSHOT_INTERVAL_MS = 10_000 // 10초마다 저장

/** FR-CODE-002: 첫 입력 후 10초마다 저장, 10초 무입력 시 중단 → 재입력 시 다시 시작 */
function startSnapshotInterval() {
  if (snapshotIntervalId) return
  snapshotStoppedByIdle.value = false
  snapshotIntervalId = setInterval(async () => {
    const sid = ideStore.sessionId
    if (!sid || !isLoggedIn.value) return
    const lastAt = ideStore.lastCodeInputAt
    if (!lastAt) return
    if (Date.now() - lastAt > IDLE_STOP_MS) {
      clearInterval(snapshotIntervalId)
      snapshotIntervalId = null
      snapshotStoppedByIdle.value = true
      return
    }
    const code = ideStore.getCode(route.params.id)
    if (code == null || code === '') return
    isSaveInProgress.value = true
    saveFailed.value = false
    try {
      await sessionApi.saveCodeSnapshot(sid, { language: API_LANGUAGE, code })
      lastSavedAt.value = Date.now()
      saveFailed.value = false
    } catch (err) {
      saveFailed.value = true
      if (err.response?.status === 400 || err.response?.status === 403 || err.response?.status === 404) {
        clearInterval(snapshotIntervalId)
        snapshotIntervalId = null
      }
    } finally {
      isSaveInProgress.value = false
    }
  }, SNAPSHOT_INTERVAL_MS)
}

/** 페이지 이탈 시 세션 종료 */
async function closeSessionOnLeave() {
  const sid = ideStore.sessionId
  justCreatedSessionId.value = null
  if (!sid) return
  try {
    await sessionApi.closeSession(sid)
  } catch (_) {
    // 이탈 중이므로 무시
  }
  ideStore.clearSession()
}

/** FR-CODE-010: 브라우저 닫기/새로고침 시 작성 중인 코드 있으면 확인 (beforeunload) */
function onBeforeUnload(e) {
  const code = ideStore.getCode(route.params.id)
  if (code != null && String(code).trim() !== '') {
    e.preventDefault()
    e.returnValue = ''
  }
}

onMounted(async () => {
  isInitializing.value = true
  try {
    await initSession()
    problemStartTime.value = Date.now()
    timerStoppedAt.value = null
  } finally {
    isInitializing.value = false
    ideStore.ideRouteLoading = false
  }
  // 10초 저장은 첫 입력 후에만 시작 (startSnapshotInterval은 lastCodeInputAt 변경 시 watch에서 호출)
  // "N초 전" 1초마다 갱신 (FR-CODE-011 타이머도 동일 간격으로 갱신)
  statusTickIntervalId = setInterval(() => {
    lastStatusTick.value = Date.now()
  }, 1000)
  window.addEventListener('online', onOnline)
  window.addEventListener('offline', onOffline)
  window.addEventListener('beforeunload', onBeforeUnload)
})

// 첫 입력(또는 30초 idle 후 재입력) 시 10초 스냅샷 interval 시작
watch(() => ideStore.lastCodeInputAt, () => {
  if (ideStore.lastCodeInputAt && !snapshotIntervalId) startSnapshotInterval()
}, { deep: true })

// 같은 IDE 페이지에서 문제 ID만 바뀐 경우 세션 재초기화 (interval은 입력 시 다시 시작)
watch(() => route.params.id, async (newId, oldId) => {
  if (newId && newId !== oldId) {
    isInitializing.value = true
    try {
      await initSession()
      problemStartTime.value = Date.now()
      timerStoppedAt.value = null
    } finally {
      isInitializing.value = false
    }
  }
})

/** FR-CODE-010: 코드 작성 중 나가기 시 확인 메시지 (뒤로가기/라우트 이탈). 리포트에서 '메인 화면으로' 클릭 시에는 세션이 이미 종료되어 있으므로 확인 생략 */
onBeforeRouteLeave(async (to, from, next) => {
  if (skipLeaveConfirm.value) {
    skipLeaveConfirm.value = false
    await closeSessionOnLeave()
    if (snapshotIntervalId) {
      clearInterval(snapshotIntervalId)
      snapshotIntervalId = null
    }
    next()
    return
  }
  const code = ideStore.getCode(route.params.id)
  const hasCode = code != null && String(code).trim() !== ''
  const message = hasCode
    ? '작성 중인 코드가 있습니다. 정말 나가시겠습니까?'
    : '진행 상황은 저장되지 않습니다. 정말 페이지를 벗어나시겠습니까?'
  const ok = await requestConfirm({
    title: '페이지 나가기',
    message,
    variant: hasCode ? 'warning' : 'info',
    confirmText: '나가기',
    cancelText: '취소',
  })
  if (!ok) {
    next(false)
    return
  }
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
  document.removeEventListener('mousemove', handleResizeVertical)
  document.removeEventListener('mouseup', stopResizeVertical)
  if (snapshotIntervalId) {
    clearInterval(snapshotIntervalId)
    snapshotIntervalId = null
  }
  if (statusTickIntervalId) {
    clearInterval(statusTickIntervalId)
    statusTickIntervalId = null
  }
  window.removeEventListener('online', onOnline)
  window.removeEventListener('offline', onOffline)
  window.removeEventListener('beforeunload', onBeforeUnload)

  // confirm 대기 중이면 안전하게 취소 처리
  if (confirmResolver) closeConfirm(false)
})

const handleBack = async () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push('/')
  }
}

const handleSubmit = async () => {
  if (!isLoggedIn.value) return
  const sid = ideStore.sessionId
  if (!sid) {
    if (terminalPanel.value) terminalPanel.value.write('세션이 없습니다. 페이지를 새로고침해 주세요.\r\n')
    return
  }
  const code = ideStore.getCode(route.params.id)
  if (terminalPanel.value) {
    terminalPanel.value.clear()
    terminalPanel.value.write('제출 중...\r\n')
    terminalPanel.value.write('채점 중... \r\n')
  }
  try {
    const { data: res } = await sessionApi.submitCode(sid, { language: API_LANGUAGE, code })
    const success = isSubmitSuccess(res)
    if (terminalPanel.value) {
      const ec = res?.data?.evaluationContext
      if (success) {
        // 성공 시: evaluationContext 없음
        terminalPanel.value.write('📊 모든 테스트 통과 (100%)\r\n')
        terminalPanel.value.write('✅ 모든 테스트를 통과했습니다. 세션을 종료합니다.\r\n')
        if (res?.data?.execTime) terminalPanel.value.write(`⏱️ 실행 시간: ${res.data.execTime}ms\r\n`)
        if (res?.data?.memory) terminalPanel.value.write(`💾 메모리: ${(res.data.memory / 1024).toFixed(2)}KB\r\n`)
      } else if (ec) {
        // 실패 시: evaluationContext 있음
        const passed = ec.passedCount ?? 0
        const total = ec.totalCount
        const pct = total > 0 ? Math.round((passed / total) * 100) : 0
        terminalPanel.value.write('\r\n│ 📊 채점 결과: ' + `${passed} / ${total}개 테스트 통과 (${pct}%)` + '\r\n')
        if (ec.failReason) terminalPanel.value.write('│ ❌ 사유: ' + ec.failReason + '\r\n')
        if (ec.isTimeout) terminalPanel.value.write('│ ⏱️ 시간 초과\r\n')
        if (ec.isOom) terminalPanel.value.write('│ 💾 메모리 초과\r\n')
        terminalPanel.value.write('\r\n❌ 일부 테스트를 통과하지 못했습니다. 세션은 유지됩니다.\r\n')
      } else {
        terminalPanel.value.write(res?.message || '제출 완료\r\n')
        terminalPanel.value.write('❌ 일부 테스트를 통과하지 못했습니다. 세션은 유지됩니다.\r\n')
      }
    }
    // 1) 제출 성공 시: 세션 닫기 후 리포트 모달 표시 (채점·결과는 submit 응답으로 구성)
    if (success) {
      timerStoppedAt.value = lastStatusTick.value - problemStartTime.value
      problemStartTime.value = 0
      await closeSessionOnLeave()
      if (snapshotIntervalId) {
        clearInterval(snapshotIntervalId)
        snapshotIntervalId = null
      }
      const problemTitle = `문제 #${route.params.id}`
      reportData.value = buildReportFromSubmitResponse(res, problemTitle)
      const reportId = res?.data?.submissionContext?.resultId ?? res?.data?.resultId ?? res?.data?.reportId
      try {
        const fetched = reportId != null ? await getReportDetail(reportId) : null
        if (fetched?.result) {
          reportData.value.result = { ...reportData.value.result, ...fetched.result }
        }
      } catch (_) {}
      reportModalFromHistory.value = false
      showReportModal.value = true
    }
  } catch (err) {
    if (terminalPanel.value) {
      const msg = err.response?.data?.message || err.message
      terminalPanel.value.write(`제출 실패: ${msg}\r\n`)
      const data = err.response?.data
      if (data && typeof data === 'object' && Object.keys(data).length > 0) {
        try {
          terminalPanel.value.write('\r\n' + JSON.stringify(data, null, 2) + '\r\n')
        } catch (_) {}
      }
      terminalPanel.value.write('❌ 제출 실패\r\n')
    }
  }
}

/** 코드에 input() 호출이 있는지 휴리스틱 검사 (Python 기준) */
const codeNeedsStdin = (code) => {
  if (!code || typeof code !== 'string') return false
  return code.includes('input(')
}

/** 실행하기 클릭: input()이 있으면 stdin 모달, 없으면 바로 실행 */
const openRunInputModal = () => {
  if (!isLoggedIn.value) return
  const sid = ideStore.sessionId
  if (!sid) {
    if (terminalPanel.value) terminalPanel.value.write('세션이 없습니다. 페이지를 새로고침해 주세요.\r\n')
    return
  }
  const code = ideStore.getCode(route.params.id)
  if (codeNeedsStdin(code)) {
    runInputContent.value = terminalPanel.value?.getFullInput?.() ?? ''
    showRunInputModal.value = true
  } else {
    doRunWithInput('')
  }
}

/** 모달에서 실행 버튼 클릭: 입력창 내용을 input으로 API 호출 */
const confirmRunWithInput = () => {
  showRunInputModal.value = false
  doRunWithInput(runInputContent.value ?? '')
}

/** 실제 실행 API 호출 (input: stdin 전체 문자열) */
const doRunWithInput = async (input) => {
  if (!isLoggedIn.value) return
  const sid = ideStore.sessionId
  if (!sid) {
    if (terminalPanel.value) terminalPanel.value.write('세션이 없습니다. 페이지를 새로고침해 주세요.\r\n')
    return
  }
  isRunLoading.value = true
  const code = ideStore.getCode(route.params.id)
  if (terminalPanel.value) {
    terminalPanel.value.clear()
    terminalPanel.value.setRunning(true)
    terminalPanel.value.write('\x1b[33m[Running...]\x1b[0m\r\n')
  }
  try {
    const { data: res } = await sessionApi.runCode(sid, { language: API_LANGUAGE, code, input: input ?? '' })
    const d = res?.data
    const execTimeMs = d?.execTime ?? 0
    const execTimeSec = (execTimeMs / 1000).toFixed(2)
    if (terminalPanel.value) {
      // FR-CODE-005-1: stdout 기본색, stderr 빨간색 / FR-CODE-005-4: 1000줄 초과 시 생략
      const stdout = d?.stdout ?? ''
      const stderr = d?.stderr ?? ''
      const combined = stdout + (stderr ? (stdout ? '\n' : '') + stderr : '')
      const lines = combined.split(/\r?\n/)
      const MAX_LINES = 1000
      if (lines.length > MAX_LINES) {
        const truncated = lines.slice(0, MAX_LINES).join('\r\n') + '\r\n... (출력 생략)\r\n'
        terminalPanel.value.write(truncated)
      } else {
        if (stdout) terminalPanel.value.write(stdout)
        if (stderr) terminalPanel.value.writeStderr(stderr)
      }
      if (d?.isTimeout) terminalPanel.value.writeStderr('Time Limit Exceeded\r\n')
      if (d?.isOom) terminalPanel.value.writeStderr('Memory Limit Exceeded\r\n')
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
    if (terminalPanel.value) {
      terminalPanel.value.clearInputAndShowPrompt()
      terminalPanel.value.setRunning(false)
    }
    isRunLoading.value = false
  }
}

const handleEscape = async () => {
  const ok = await requestConfirm({
    title: '탈주하기',
    message: '정말 탈주하시겠습니까?',
    variant: 'warning',
    confirmText: '탈주',
    cancelText: '취소',
  })
  if (!ok) return
  const sid = ideStore.sessionId
  justCreatedSessionId.value = null
  if (sid && isLoggedIn.value) {
    const code = ideStore.getCode(route.params.id)
    try {
      // 1. give-up API 호출 (language, code 필요). 404 등 실패 시에도 close는 호출
      await sessionApi.giveUp(sid, { language: API_LANGUAGE, code })
    } catch (_) {
      // give-up 미구현(404) 등 실패해도 무시
    }
    try {
      // 2. 세션 종료는 항상 호출 (give-up 실패해도 세션이 닫혀야 다음 진입 시 새 세션 생성)
      await sessionApi.closeSession(sid)
    } catch (_) {}
    ideStore.clearSession()
  }
  if (snapshotIntervalId) {
    clearInterval(snapshotIntervalId)
    snapshotIntervalId = null
  }
  reportData.value = getMockReportData('문제 풀이 결과', { withGrading: false })
  reportModalFromHistory.value = false
  showReportModal.value = true
}

/** 제출 내역 탭에서 특정 결과의 리포트 보기 */
const handleOpenReport = async (resultId) => {
  reportModalFromHistory.value = true
  try {
    reportData.value = await getReportDetail(resultId)
    if (!reportData.value) reportData.value = getMockReportData(`문제 #${route.params.id}`)
  } catch (_) {
    reportData.value = getMockReportData(`문제 #${route.params.id}`)
  }
  showReportModal.value = true
}

const onReportModalClose = () => {
  showReportModal.value = false
  reportData.value = null
  if (!reportModalFromHistory.value) {
    skipLeaveConfirm.value = true
    router.push('/')
  }
  reportModalFromHistory.value = false
}

/** 문제 패널 채팅에서 힌트 사용 시 툴바 당근·잔여 횟수 동기화 */
function onHintUsedFromPanel({ usedHint, maxHint }) {
  hintUsed.value = usedHint ?? hintUsed.value
  hintMax.value = maxHint ?? hintMax.value
  showToast(`힌트가 차감되었습니다. (잔여: ${(maxHint ?? 3) - (usedHint ?? 0)}/${maxHint ?? 3})`)
}

function showToast(msg) {
  toastMessage.value = msg
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
    toastTimer = null
  }, 3000)
}
</script>

<style scoped>
.ide-resizer-hit {
  position: relative;
}
.ide-resizer-hit::before {
  content: '';
  position: absolute;
  left: -4px;
  right: -4px;
  top: 0;
  bottom: 0;
  cursor: col-resize;
}
.ide-editor-container {
  min-height: 200px;
}
/* 힌트 패널 접기/펼치기 트랜지션 */
.hint-panel-enter-active,
.hint-panel-leave-active {
  transition: width 0.2s ease, min-width 0.2s ease, opacity 0.2s ease;
}
.hint-panel-enter-from,
.hint-panel-leave-to {
  width: 0;
  min-width: 0;
  opacity: 0;
  overflow: hidden;
}
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* FR-CODE-002-1: 에디터 우측 하단 저장 상태 */
.ide-save-status {
  position: absolute;
  bottom: 8px;
  right: 12px;
  font-size: 0.75rem;
  color: var(--color-farm-brown);
  pointer-events: none;
  white-space: nowrap;
  text-align: right;
}
.ide-save-status-sub {
  margin-top: 2px;
  font-size: 0.7rem;
  color: var(--color-farm-brown);
}
.ide-save-status-stopped {
  color: var(--color-farm-point, #e07c4a);
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

/* 메인→IDE 진입 시 로딩 모달 */
.ide-loading-overlay {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(245, 242, 232, 0.9);
  z-index: 100;
}
.ide-loading-card {
  background: #fff;
  border-radius: 1rem;
  padding: 1.5rem 2rem;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
}
.ide-loading-text {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-farm-brown-dark);
}
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s, transform 0.25s;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(0.5rem);
}
@media (max-width: 767px) {
  .ide-resizer-hit {
    display: none;
  }
}
</style>
