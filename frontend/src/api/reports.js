import api from './index'

/**
 * 리포트 상세 조회
 * GET /api/v1/reports/{report_id}
 * @param {number|string} reportId
 * @returns {Promise<object|null>} API data(ReportDetailResponseDto) 또는 실패 시 null
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

/**
 * 제출 API 응답으로 리포트 객체 구성 (채점·결과용 evaluationContext 포함)
 * 백엔드 SubmitSessionResponseDto: resultType, evaluationContext, submissionContext, feedback, awardedPoints
 * submissionContext: resultId, solveTime, execTime, memory, submittedAt
 * @param {{ data?: { resultType?, evaluationContext?, submissionContext?, feedback?, awardedPoints? } }} res - submit 응답 (res.data = DTO)
 * @param {string} [problemTitle] - 문제 제목
 * @returns {{ result: object, evaluationContext?: object, xp?: number }}
 */
export const buildReportFromSubmitResponse = (res, problemTitle = '문제 풀이 결과') => {
  const d = res?.data ?? {}
  const sub = d.submissionContext ?? {}
  const evalCtx = d.evaluationContext ?? null
  const result = {
    resultId: sub.resultId ?? d.resultId ?? null,
    resultType: d.resultType ?? 'SUCCESS',
    language: d.language ?? 'PYTHON',
    problem: { problemId: 0, title: problemTitle, difficulty: 'LEVEL1', algorithm: '' },
    code: '',
    solveTime: sub.solveTime ?? d.solveTime ?? 0,
    execTime: sub.execTime ?? d.execTime ?? 0,
    memory: sub.memory ?? d.memory ?? 0,
    feedback: d.feedback ?? '제출이 완료되었습니다.',
    createdAt: sub.submittedAt ?? d.submittedAt ?? new Date().toISOString(),
    hintCount: null,
    hintContents: [],
    improvementDirection: null
  }
  const report = {
    result,
    evaluationContext: evalCtx,
    // API에서 내려주는 실제 획득 포인트 (없으면 null)
    awardedPoints: d.awardedPoints ?? null
  }
  // 성공 시: xp = awardedPoints (없으면 기존 로직 사용)
  if (d.resultType === 'SUCCESS') {
    if (d.awardedPoints != null) {
      report.xp = d.awardedPoints
    } else {
      report.xp = 100
    }
  } else if (
    d.resultType !== 'GIVE_UP' &&
    evalCtx &&
    evalCtx.totalCount != null &&
    evalCtx.totalCount > 0 &&
    evalCtx.passedCount != null
  ) {
    // 실패(오답 등) 시: 통과율 기반 xp, 탈주(GIVE_UP)는 xp 없음
    report.xp = Math.round((evalCtx.passedCount / evalCtx.totalCount) * 100)
  }
  return report
}

/** 백엔드 미구현 시 사용할 목 데이터. API 연동 후 제거하거나 fallback 전용으로만 사용 */
export const getMockReportData = (problemTitle = '문제 풀이 결과', options = {}) => {
  const { withGrading = true } = options
  const report = {
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
      code: 'print("Hello, World!")',
      solveTime: 0,
      execTime: 0,
      memory: 0,
      feedback: '제출이 완료되었습니다. 백엔드 API 연동 후 실제 피드백이 표시됩니다.',
      createdAt: new Date().toISOString(),
      hintCount: 0,
      hintContents: [],
      improvementDirection: '코드 가독성 개선 및 예외 처리를 고려해 보세요.'
    }
  }
  if (withGrading) {
    report.evaluationContext = {
      passedCount: 5,
      totalCount: 5,
      failReason: null,
      isTimeout: false,
      isOom: false,
      failedLineNo: null,
      expectedLine: null,
      actualLine: null
    }
    report.xp = 100
  }
  return report
}
