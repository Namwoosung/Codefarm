import { ref, onUnmounted, watch } from 'vue'
import { createParser } from 'eventsource-parser'
import { useIdeStore } from '@/stores/ide'

/** SSE 재연결 설정 */
const RECONNECT_INTERVAL_MS = 3000
const MAX_RECONNECT_ATTEMPTS = 10

/** 치명적 오류: 재연결 중단 (401, 403, 404) */
const FATAL_STATUS_CODES = [401, 403, 404]

/**
 * HTTP 상태 코드별 에러 메시지
 */
function getErrorMessage(status) {
  switch (status) {
    case 401:
      return '세션이 만료되었습니다. 다시 로그인해주세요.'
    case 403:
      return '해당 세션에 대한 접근 권한이 없습니다.'
    case 404:
      return '존재하지 않는 세션입니다.'
    default:
      return '서버와 연결이 불안정합니다. 자동으로 재연결을 시도합니다.'
  }
}

/**
 * SSE 힌트 구독 훅 (Composable)
 * @param {import('vue').Ref<number|string|null>} sessionIdRef - 세션 ID (ref)
 * @param {object} options
 * @param {(message: string) => void} [options.onFatalError] - 치명적 오류 시 토스트용 콜백 (401, 403, 404)
 * @returns {{ reconnectCount: import('vue').Ref<number>, isConnecting: import('vue').Ref<boolean> }}
 */
export function useSSE(sessionIdRef, options = {}) {
  const { onFatalError } = options
  const ideStore = useIdeStore()

  const reconnectCount = ref(0)
  const isConnecting = ref(false)

  let ac = null
  let aborted = false
  let reconnectTimeoutId = null

  const stopReconnect = () => {
    if (reconnectTimeoutId != null) {
      clearTimeout(reconnectTimeoutId)
      reconnectTimeoutId = null
    }
  }

  const cleanup = () => {
    aborted = true
    stopReconnect()
    if (ac != null) {
      ac.abort()
      ac = null
    }
  }

  const connect = (sessionId) => {
    if (aborted || sessionId == null || sessionId === '') return

    ac = new AbortController()
    const baseURL = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')
    const url = `${baseURL}/sessions/${sessionId}/hints/subscribe`
    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('token') : null
    const headers = { Accept: 'text/event-stream' }
    if (token) headers.Authorization = `Bearer ${token}`

    if (reconnectCount.value > 0) {
      isConnecting.value = true
    }

    fetch(url, { signal: ac.signal, headers })
      .then((res) => {
        if (aborted) return
        isConnecting.value = false

        if (!res.ok) {
          const status = res.status
          if (FATAL_STATUS_CODES.includes(status)) {
            const msg = getErrorMessage(status)
            onFatalError?.(msg)
            return
          }
          // 5xx 또는 기타: 재연결 시도 (토스트 없이 isConnecting만 활용)
          scheduleReconnect(sessionId)
          return
        }

        reconnectCount.value = 0

        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        const parser = createParser({
          onEvent(ev) {
            if (aborted) return
            try {
              const data = ev.data ? JSON.parse(ev.data) : null
              if (ev.event === 'AUTO_HINT' && data) {
                ideStore.addHint(data)
              }
            } catch (_) {}
          }
        })

        const read = () => {
          reader
            .read()
            .then(({ done, value }) => {
              if (aborted) return
              if (done) {
                parser.reset?.({ consume: true })
                scheduleReconnect(sessionId)
                return
              }
              const chunk = decoder.decode(value, { stream: true })
              parser.feed(chunk)
              read()
            })
            .catch((e) => {
              if (aborted || ac?.signal?.aborted) return
              scheduleReconnect(sessionId)
            })
        }
        read()
      })
      .catch((e) => {
        if (aborted || ac?.signal?.aborted) return
        isConnecting.value = false
        scheduleReconnect(sessionId)
      })
  }

  const scheduleReconnect = (sessionId) => {
    if (aborted || sessionId == null) return
    if (reconnectCount.value >= MAX_RECONNECT_ATTEMPTS) {
      onFatalError?.('서버와 연결이 불안정합니다. 자동으로 재연결을 시도합니다.')
      return
    }
    reconnectCount.value += 1
    isConnecting.value = true
    reconnectTimeoutId = setTimeout(() => {
      reconnectTimeoutId = null
      connect(sessionId)
    }, RECONNECT_INTERVAL_MS)
  }

  watch(
    sessionIdRef,
    (sid) => {
      cleanup()
      if (sid != null && sid !== '') {
        aborted = false
        reconnectCount.value = 0
        isConnecting.value = false
        connect(sid)
      }
    },
    { immediate: true }
  )

  onUnmounted(() => {
    cleanup()
  })

  return {
    reconnectCount,
    isConnecting
  }
}
