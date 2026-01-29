import { defineStore } from 'pinia'
import { ref } from 'vue'

/** 문제에 처음 들어갔을 때 보여줄 기본 코드 */
export const DEFAULT_CODE = 'print("코드팜에 어서오세요!")'

export const useIdeStore = defineStore('ide', () => {
  // 문제 ID별로 저장된 코드 { [problemId]: string }
  const codeByProblemId = ref({})

  // 현재 세션 ID (로그인 후 IDE 진입 시 생성/조회된 세션)
  const sessionId = ref(null)

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
    getCode,
    updateCode,
    setCodeToDefault,
    setSessionId,
    clearSession
  }
}, {
  persist: true // localStorage에 codeByProblemId 자동 저장
})
