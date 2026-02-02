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
    const { data } = await api.post(`/sessions/${sessionId}/hints/manual`, { userQuestion })
    return data
  } catch (err) {
    if (err.response?.status === 404 || err.response?.status === 400 || err.response?.status === 403 || err.response?.status === 500) {
      return getMockManualHintResponse(userQuestion)
    }
    return getMockManualHintResponse(userQuestion)
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
      content: '반복문의 종료 조건이 문제에서 요구하는 범위와 일치하는지 다시 확인해보세요. (목 데이터)',
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
