import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 전역 UI 상태
 * - 라우트 전환 중(새 화면 "완성본" 준비 전) 빈 프레임/깜빡임 방지 오버레이
 */
export const useUiStore = defineStore('ui', () => {
  const routeChanging = ref(false)

  let safetyTimer = null
  const SAFETY_MAX_MS = 4000

  const startRouteChange = () => {
    routeChanging.value = true
    if (safetyTimer) clearTimeout(safetyTimer)
    safetyTimer = setTimeout(() => {
      // 어떤 이유로 ready 신호가 안 와도 화면이 영원히 막히지 않도록
      routeChanging.value = false
      safetyTimer = null
    }, SAFETY_MAX_MS)
  }

  const endRouteChange = () => {
    routeChanging.value = false
    if (safetyTimer) {
      clearTimeout(safetyTimer)
      safetyTimer = null
    }
  }

  return {
    routeChanging,
    startRouteChange,
    endRouteChange,
  }
})

