import api from './index'

/**
 * 문제 목록 조회 (동적 쿼리)
 * @param {object} [queryParams] - 쿼리 파라미터 (page, size, difficulty 등)
 * @returns {Promise<{ data: array, total?: number }>}
 */
export const getProblemList = async (queryParams = {}) => {
  const { data: res } = await api.get('/problems/lists', { params: queryParams })
  const inner = res?.data ?? res
  const rawList = inner?.problemList ?? inner?.content ?? (Array.isArray(inner) ? inner : [])
  const items = rawList.map((item) => {
    const p = item?.problem ?? item
    return { ...p, userStatus: item?.userStatus, statistics: item?.statistics }
  })
  const total = inner?.page?.totalElements ?? inner?.totalElements ?? inner?.total ?? items.length
  return { data: items, total }
}

/**
 * 문제 상세 조회 (백엔드 API만 사용)
 * @param {number|string} problemId - 백엔드 DB 문제 ID
 * @returns {Promise<{ isLogined: boolean, problem: object, userStatus: object|null, statistics: object }>}
 */
export const getProblemDetail = async (problemId) => {
  const id = Number(problemId)
  if (!id) {
    throw new Error(`유효하지 않은 문제 ID입니다: ${problemId}`)
  }

  const { data: res } = await api.get(`/problems/${id}`)
  const raw = res?.data ?? res
  if (!raw) {
    throw new Error(`문제를 찾을 수 없습니다: ${problemId}`)
  }

  const p = raw?.problem ?? raw
  const difficulty =
    typeof p.difficulty === 'number' ? `LEVEL${p.difficulty}` : (p.difficulty ?? 'LEVEL1')
  const problem = {
    problemId: p.problemId ?? id,
    title: p.title ?? '',
    description: p.description ?? '',
    difficulty,
    algorithm: p.algorithm ?? [],
    timeLimit: p.timeLimit ?? p.time_limit ?? 1,
    memoryLimit: p.memoryLimit ?? p.memory_limit ?? 256,
    exampleInput: p.exampleInput ?? p.example_input ?? '',
    exampleOutput: p.exampleOutput ?? p.example_output ?? '',
    problemType: p.problemType ?? p.problem_type ?? 'NORMAL',
    createdAt: p.createdAt ?? p.created_at ?? null
  }

  return {
    isLogined: raw?.isLogined ?? res?.isLogined ?? true,
    problem,
    userStatus: raw?.userStatus ?? null,
    statistics: raw?.statistics ?? { submissionCount: 0, successCount: 0 }
  }
}
