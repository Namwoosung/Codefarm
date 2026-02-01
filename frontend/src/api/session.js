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
 * 실행하기 (input 없으면 빈 문자열 전송, input() 시 stdin으로 사용)
 * @param {number} sessionId
 * @param {{ language: string, code: string, input?: string }} body
 */
export const runCode = (sessionId, { language, code, input }) => {
  const body = { language, code, input: input != null ? String(input) : '' }
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
 * 포기하기 (탈주)
 * @param {number} sessionId
 * @param {{ language: string, code: string }} body
 */
export const giveUp = (sessionId, { language, code }) => {
  return api.post(`/sessions/${sessionId}/give-up`, { language, code })
}

/**
 * 결과 목록 조회
 * GET /api/v1/sessions/{session_id}/results
 * @param {number} sessionId
 * @returns {Promise<{ data: { results: Array<{ resultId?: number|null, resultType: string, language: string, accuracy: number, solveTime: number, createdAt: string, hasReport: boolean }> } }>}
 */
export const getResults = (sessionId) => {
  return api.get(`/sessions/${sessionId}/results`)
}

/**
 * 결과 목록 조회 — 배열만 반환. 404(SESSION_NOT_FOUND)/403(ACCESS_DENIED) 시 빈 배열.
 * @param {number} sessionId
 * @returns {Promise<Array<{ resultId?: number|null, resultType: string, language: string, accuracy: number, solveTime: number, createdAt: string, hasReport: boolean }>>}
 */
export const getSessionResultsList = async (sessionId) => {
  if (sessionId == null) return []
  try {
    const { data: res } = await getResults(sessionId)
    return res?.data?.results ?? []
  } catch (err) {
    if (err.response?.status === 404 || err.response?.status === 403) return []
    throw err
  }
}

/**
 * 백엔드 미구현 시 제출 이력 UI용 목 데이터.
 * API 연동 후 제거하거나 fallback 전용으로만 사용.
 * @returns {Array<{ resultId?: number|null, resultType: string, language: string, accuracy: number, solveTime: number, createdAt: string, hasReport: boolean }>}
 */
export const getMockSessionResults = () => [
  {
    resultId: 602,
    resultType: 'GIVE_UP',
    language: 'PYTHON',
    accuracy: 0,
    solveTime: 538,
    createdAt: new Date(Date.now() - 86400000).toISOString(),
    hasReport: true
  },
  {
    resultId: 501,
    resultType: 'SUCCESS',
    language: 'PYTHON',
    accuracy: 100,
    solveTime: 742,
    createdAt: new Date(Date.now() - 3600000).toISOString(),
    hasReport: true
  },
  {
    resultId: null,
    resultType: 'FAIL',
    language: 'PYTHON',
    accuracy: 60,
    solveTime: 615,
    createdAt: new Date(Date.now() - 7200000).toISOString(),
    hasReport: false
  }
]
