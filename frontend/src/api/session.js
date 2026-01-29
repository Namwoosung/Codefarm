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
 * 실행하기 (백엔드 @NotBlank: 공백만 있으면 400이므로 비공백 1글자 이상 필요)
 * @param {number} sessionId
 * @param {{ language: string, code: string, input?: string }} body
 */
const RUN_DEFAULT_INPUT = '.' // @NotBlank 통과용 최소 비공백
export const runCode = (sessionId, { language, code, input }) => {
  const body = { language, code, input: (input != null && input.trim()) ? input : RUN_DEFAULT_INPUT }
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
 * 현재 백엔드에 별도 give-up 엔드포인트가 없어,
 * 일단 일반 세션 종료(close)와 동일하게 처리한다.
 * @param {number} sessionId
 */
export const giveUp = (sessionId) => {
  return api.patch(`/sessions/${sessionId}/close`)
}

/**
 * 결과 목록 조회
 * @param {number} sessionId
 */
export const getResults = (sessionId) => {
  return api.get(`/sessions/${sessionId}/results`)
}
