import api from './index'

/**
 * 문제 상세 조회
 * @param {number} problemId - 문제 ID
 * @returns {Promise} 문제 상세 정보
 */
export const getProblemDetail = async (problemId) => {
  const response = await api.get(`/problems/${problemId}`)
  // response.data = { message: "...", data: { problem, userStatus, statistics } }
  // data 객체만 반환하여 사용 편의성 향상
  return response.data.data
}
