import api from './index'

/**
 * 수동 힌트 요청
 * POST /api/v1/sessions/{session_id}/hints/manual
 * @param {number} sessionId
 * @param {{ userQuestion: string, code?: string }} body - code는 맥락 기반 힌트용(FR-CODE-010-3)
 * @returns {Promise<{ data: { hintId, hintType, userQuestion, content, usedHint, maxHint, isViewed, createdAt } }>}
 */
export const requestManualHint = async (sessionId, { userQuestion, code }) => {
  if (sessionId == null || sessionId === '') {
    return getMockManualHintResponse(userQuestion)
  }
  try {
    // AI 사용으로 전역 60초보다 길게 설정
    const { data } = await api.post(`/sessions/${sessionId}/hints/manual`, { userQuestion }, { timeout: 90 * 1000 })
    return data
  } catch (err) {
    const status = err.response?.status
    // 5xx 서버/게이트웨이 오류: 힌트 미수신 → 당근 차감 금지 (재throw)
    if (status >= 500 && status <= 504) throw err
    // 404/400/403: 백엔드 미구현 등 → 목 데이터 반환
    if (status === 404 || status === 400 || status === 403) {
      return getMockManualHintResponse(userQuestion)
    }
    // 네트워크 오류 등: 당근 차감 금지 (재throw)
    throw err
  }
}

/**
 * 힌트 목록 조회
 * GET /api/v1/sessions/{session_id}/hints
 */
export const getHintList = async (sessionId) => {
  try {
    const { data } = await api.get(`/sessions/${sessionId}/hints`)
    return data?.data?.hints ?? []
  } catch (err) {
    if (err.response?.status === 404 || err.response?.status === 403) return []
    throw err
  }
}

/**
 * 힌트 열람 처리
 * PATCH /api/v1/sessions/{session_id}/hints/{hint_id}/view
 */
export const markHintViewed = async (sessionId, hintId) => {
  try {
    const { data } = await api.patch(`/sessions/${sessionId}/hints/${hintId}/view`)
    return data?.data ?? null
  } catch (err) {
    if (err.response?.status === 404 || err.response?.status === 403) return null
    throw err
  }
}

/** 백엔드 미구현 시 수동 힌트 응답 목 데이터 */
let mockUsedHint = 0
const MOCK_MAX_HINT = 3

export function getMockManualHintResponse(userQuestion) {
  mockUsedHint = Math.min(mockUsedHint + 1, MOCK_MAX_HINT)
  return {
    message: '힌트 생성 성공',
    data: {
      hintId: 300 + mockUsedHint,
      hintType: 'MANUAL',
      userQuestion: userQuestion || '질문이 없습니다.',
      content: '백엔드와 연결되지 않아서 힌트를 제공할 수 없습니다. (목 데이터)',
      usedHint: mockUsedHint,
      maxHint: MOCK_MAX_HINT,
      isViewed: true,
      createdAt: new Date().toISOString()
    }
  }
}

/** 목 데이터 잔여 횟수 초기화 (세션/페이지 전환 시 호출 가능) */
export function resetMockHintQuota() {
  mockUsedHint = 0
}

import { createParser } from 'eventsource-parser'

/** SSE 재연결 설정 */
const RECONNECT_INTERVAL_MS = 3000
const MAX_RECONNECT_ATTEMPTS = 10
/** AI 사용 구독 연결 타임아웃 (ms) */
const HINT_SSE_TIMEOUT_MS = 30000

/** 400, 403, 404 등 재연결 중단 대상 */
const FATAL_STATUS_CODES = [400, 403, 404]

/**
 * 자동 힌트 구독 (SSE) — eventsource-parser + fetch 기반
 * GET /api/v1/sessions/{session_id}/hints/subscribe
 * 재연결: 3초 간격, 최대 10회. 400/403/404 시 즉시 중단 및 onError 호출.
 * @param {number} sessionId
 * @param {{ onConnected?: (data: object) => void, onAutoHint?: (data: object) => void, onError?: (options?: { status?: number, fatal?: boolean }) => void }} callbacks
 * @returns {() => void} 구독 해제 함수
 */
export function subscribeHintSSE(sessionId, callbacks = {}) {
  if (sessionId == null || sessionId === '') return () => {}

  const baseURL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
  const url = `${baseURL}/sessions/${sessionId}/hints/subscribe`
  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null
  const headers = { Accept: 'text/event-stream' }
  if (token) headers.Authorization = `Bearer ${token}`

  let ac = null
  let reconnectAttempts = 0
  let aborted = false
  let reconnectTimeoutId = null

  const stopReconnect = () => {
    if (reconnectTimeoutId) {
      clearTimeout(reconnectTimeoutId)
      reconnectTimeoutId = null
    }
  }

  const reportError = (options = {}) => {
    if (aborted) return
    stopReconnect()
    try { callbacks.onError?.(options) } catch (_) {}
  }

  const connect = () => {
    if (aborted) return
    ac = new AbortController()
    const timeoutId = setTimeout(() => {
      if (!ac.signal.aborted) ac.abort()
    }, HINT_SSE_TIMEOUT_MS)

    if (reconnectAttempts > 0) {
      console.log(`[SSE] 재연결 시도 (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS}) sessionId=${sessionId}`)
    } else {
      console.log(`[SSE] 연결 시작 sessionId=${sessionId}`)
    }

    fetch(url, { signal: ac.signal, headers })
      .then((res) => {
        clearTimeout(timeoutId)
        if (aborted) return
        if (!res.ok) {
          const status = res.status
          console.warn(`[SSE] HTTP ${status} sessionId=${sessionId}`)
          if (FATAL_STATUS_CODES.includes(status)) {
            reportError({ status, fatal: true })
            return
          }
          reportError({ status })
          return
        }
        console.log(`[SSE] 연결 성공 sessionId=${sessionId}`)
        reconnectAttempts = 0

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        const parser = createParser({
          onEvent(ev) {
            if (aborted) return
            try {
              const data = ev.data ? JSON.parse(ev.data) : null
              if (ev.event === 'CONNECTED' && callbacks.onConnected) {
                console.log('[SSE] CONNECTED 이벤트 수신', data)
                callbacks.onConnected(data)
              } else if (ev.event === 'AUTO_HINT' && callbacks.onAutoHint) {
                console.log('[SSE] AUTO_HINT 이벤트 수신', data)
                callbacks.onAutoHint(data)
              }
            } catch (e) {
              console.warn('[SSE] 이벤트 파싱 실패', e)
            }
          }
        })

        const read = () => {
          reader.read()
            .then(({ done, value }) => {
              if (aborted) return
              if (done) {
                parser.reset?.({ consume: true })
                console.log('[SSE] 스트림 종료, 재연결 대기 sessionId=', sessionId)
                scheduleReconnect()
                return
              }
              const chunk = decoder.decode(value, { stream: true })
              parser.feed(chunk)
              read()
            })
            .catch((e) => {
              if (aborted || ac?.signal?.aborted) return
              console.warn('[SSE] 스트림 읽기 오류', e?.message ?? e)
              scheduleReconnect()
            })
        }
        read()
      })
      .catch((e) => {
        clearTimeout(timeoutId)
        if (aborted || ac?.signal?.aborted) return
        console.warn('[SSE] fetch 오류', e?.message ?? e)
        scheduleReconnect()
      })
  }

  const scheduleReconnect = () => {
    if (aborted) return
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
      console.warn(`[SSE] 재연결 최대 횟수(${MAX_RECONNECT_ATTEMPTS}) 초과, 중단 sessionId=${sessionId}`)
      reportError({ fatal: true })
      return
    }
    reconnectAttempts++
    console.log(`[SSE] ${RECONNECT_INTERVAL_MS / 1000}초 후 재연결 예정 (${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`)
    reconnectTimeoutId = setTimeout(connect, RECONNECT_INTERVAL_MS)
  }

  connect()

  return () => {
    aborted = true
    stopReconnect()
    if (ac) ac.abort()
    console.log('[SSE] 구독 해제 sessionId=', sessionId)
  }
}
