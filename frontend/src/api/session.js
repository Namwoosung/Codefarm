import api from './index'

/**
 * 세션 생성 (문제 풀이 시작)
 * @param {number} problemId
 * @returns {Promise<{ message: string, data: object }>}
 */
export const createSession = (problemId) => {
  return api.post('/sessions', { problemId })
}

/**
 * 세션 상세 조회
 * @param {number} sessionId
 */
export const getSessionDetail = (sessionId) => {
  return api.get(`/sessions/${sessionId}`)
}

/**
 * 활성 세션 조회
 * @returns {Promise<{ message: string, data: object }>}
 */
export const getActiveSession = () => {
  return api.get('/sessions/active')
}

/**
 * 세션 종료 (페이지 이탈 시 호출)
 * @param {number} sessionId
 */
export const closeSession = (sessionId) => {
  return api.patch(`/sessions/${sessionId}/close`)
}

/**
 * 코드 스냅샷 저장
 * @param {number} sessionId
 * @param {{ language: string, code: string }} body
 */
export const saveCodeSnapshot = (sessionId, { language, code }) => {
  return api.post(`/sessions/${sessionId}/codes`, { language, code })
}

/**
 * 최신 코드 조회
 * @param {number} sessionId
 */
export const getLatestCode = (sessionId) => {
  return api.get(`/sessions/${sessionId}/codes/latest`)
}

/**
 * 실행하기 (백엔드에서 input 필수)
 * @param {number} sessionId
 * @param {{ language: string, code: string, input?: string }} body
 */
export const runCode = (sessionId, { language, code, input = '\n' }) => {
  const body = { language, code, input: input ?? '\n' }
  return api.post(`/sessions/${sessionId}/run`, body)
}

/**
 * 제출하기 (전체 테스트)
 * @param {number} sessionId
 * @param {{ language: string, code: string }} body
 */
export const submitCode = (sessionId, { language, code }) => {
  return api.post(`/sessions/${sessionId}/submit`, { language, code })
}

/**
 * 포기하기
 * @param {number} sessionId
 */
export const giveUp = (sessionId) => {
  return api.post(`/sessions/${sessionId}/give-up`)
}

/**
 * 결과 목록 조회
 * @param {number} sessionId
 */
export const getResults = (sessionId) => {
  return api.get(`/sessions/${sessionId}/results`)
}
