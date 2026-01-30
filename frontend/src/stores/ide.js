import { defineStore } from 'pinia'
import { ref } from 'vue'

/** 문제에 처음 들어갔을 때 보여줄 기본 코드 (solution 함수 구조) */
export const DEFAULT_CODE = `print("코드팜에 어서오세요!")`

export const useIdeStore = defineStore('ide', () => {
  // 문제 ID별로 저장된 코드 { [problemId]: string }
  const codeByProblemId = ref({})

  // 현재 세션 ID (로그인 후 IDE 진입 시 생성/조회된 세션)
  const sessionId = ref(null)

  // 마지막 키보드 입력 시각 (10초 저장: 첫 입력 후 10초마다 저장, 30초 무입력 시 중단)
  const lastCodeInputAt = ref(null)

  /** 코드 입력 시 호출 (스냅샷 저장 타이밍용) */
  const touchCodeInput = () => {
    lastCodeInputAt.value = Date.now()
  }

  /** 해당 문제의 코드 반환 (없으면 기본 코드) */
  const getCode = (problemId) => {
    const key = problemId != null ? String(problemId) : ''
    return codeByProblemId.value[key] ?? DEFAULT_CODE
  }

  /** 해당 문제의 코드 업데이트 */
  const updateCode = (problemId, newCode) => {
    const key = problemId != null ? String(problemId) : ''
    codeByProblemId.value = { ...codeByProblemId.value, [key]: newCode }
  }

  /** 해당 문제 코드를 기본 코드로 초기화 */
  const setCodeToDefault = (problemId) => {
    updateCode(problemId, DEFAULT_CODE)
  }

  // 세션 설정 (진입 시 생성/활성 조회 후 저장)
  const setSessionId = (id) => {
    sessionId.value = id
  }

  // 세션 초기화 (이탈 시)
  const clearSession = () => {
    sessionId.value = null
  }

  return {
    codeByProblemId,
    sessionId,
    lastCodeInputAt,
    touchCodeInput,
    getCode,
    updateCode,
    setCodeToDefault,
    setSessionId,
    clearSession
  }
}, {
  persist: true // localStorage에 codeByProblemId 자동 저장
})
