import api from './index'

/**
 * 리포트 상세 조회
 * GET /api/v1/reports/{report_id}
 * @param {number|string} reportId
 * @returns {Promise<{ result: object }|null>} data.result 또는 실패 시 null (호출부에서 목 데이터 사용)
 */
export const getReportDetail = async (reportId) => {
  if (reportId == null || reportId === '') return null
  try {
    const { data: res } = await api.get(`/reports/${reportId}`)
    return res?.data ?? null
  } catch (err) {
    if (err.response?.status === 404 || err.response?.status === 403) return null
    throw err
  }
}

/** 백엔드 미구현 시 사용할 목 데이터. API 연동 후 제거하거나 fallback 전용으로만 사용 */
export const getMockReportData = (problemTitle = '문제 풀이 결과') => ({
  result: {
    resultId: 0,
    resultType: 'SUCCESS',
    language: 'PYTHON',
    problem: {
      problemId: 0,
      title: problemTitle,
      difficulty: 'LEVEL1',
      algorithm: ''
    },
    code: '',
    solveTime: 0,
    execTime: 0,
    memory: 0,
    feedback: '제출이 완료되었습니다. 백엔드 API 연동 후 실제 피드백이 표시됩니다.',
    createdAt: new Date().toISOString()
  }
})
