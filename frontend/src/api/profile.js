import api from './index'

/**
 * 사용자 프로필 조회
 * GET /api/v1/users/profiles
 * @returns {Promise<{ data: object }>}
 */
export const getUserProfile = async () => {
  return api.get('/users/profiles')
}

/**
 * 사용자 프로필 수정
 * PATCH /api/v1/users/profiles
 * @param {{ age?: number, name?: string, codingLevel?: number, nickname?: string }} requestBody
 * @returns {Promise<{ data: object }>}
 */
export const updateUserProfile = async (requestBody) => {
  return api.patch('/users/profiles', requestBody)
}

/**
 * 내 리포트 목록 조회
 * GET /api/v1/reports/me
 * @param {object} [params] - 쿼리 파라미터
 * @returns {Promise<{ data: Array }>}
 */
export const getMyReports = async (params) => {
  return api.get('/reports/me', { params })
}

/**
 * 리포트 상세 조회 (profile store용)
 * GET /api/v1/reports/{reportId}
 * @param {number|string} reportId
 * @returns {Promise<{ data: { data: object } }>}
 */
export const getReportDetail = async (reportId) => {
  return api.get(`/reports/${reportId}`)
}
