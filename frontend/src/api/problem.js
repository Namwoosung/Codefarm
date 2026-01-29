import api from './index'
import mockProblems from '@/mocks/sampled_30_clean.json'

const MOCK_ID_OFFSET = 21 // 백엔드 ID 21 = mock index 0

/**
 * mock 데이터로 문제 상세 반환 (API 404 시 폴백)
 */
function getProblemDetailFromMock(problemId) {
  const id = Number(problemId)
  const mockIndex = id - MOCK_ID_OFFSET
  const raw = mockProblems[mockIndex]
  if (!raw) return null

  const difficultyMap = { 1: 'LEVEL1', 2: 'LEVEL2', 3: 'LEVEL3', 4: 'LEVEL4', 5: 'LEVEL5' }
  const problem = {
    problemId: id,
    title: raw.title ?? '',
    description: raw.description ?? '',
    difficulty: difficultyMap[raw.difficulty] ?? 'LEVEL1',
    algorithm: raw.algorithm ?? [],
    timeLimit: raw.time_limit ?? raw.timeLimit ?? 1,
    memoryLimit: raw.memory_limit ?? raw.memoryLimit ?? 256,
    exampleInput: raw.example_input ?? raw.exampleInput ?? '',
    exampleOutput: raw.example_output ?? raw.exampleOutput ?? '',
    problemType: raw.problem_type ?? raw.problemType ?? 'NORMAL',
    createdAt: raw.createdAt ?? null
  }
  return {
    isLogined: true,
    problem,
    userStatus: null,
    statistics: { submissionCount: 0, successCount: 0 }
  }
}

/**
 * 문제 상세 조회 (백엔드 API 연동, 404 시 mock 폴백)
 * - 라우트 id = 백엔드 problemId (21, 22, 23...)
 * @param {number|string} problemId - 백엔드 DB 문제 ID (21, 22, 23...)
 * @returns {Promise<{ isLogined: boolean, problem: object, userStatus: object|null, statistics: object }>}
 */
export const getProblemDetail = async (problemId) => {
  const id = Number(problemId)
  if (!id) {
    throw new Error(`유효하지 않은 문제 ID입니다: ${problemId}`)
  }

  try {
    const { data: res } = await api.get(`/problems/${id}`)
    const raw = res?.data ?? res
    if (!raw) throw new Error('문제를 찾을 수 없습니다.')

    const problem = {
      problemId: raw.problemId ?? id,
      title: raw.title ?? '',
      description: raw.description ?? '',
      difficulty: raw.difficulty ?? 'LEVEL1',
      algorithm: raw.algorithm ?? [],
      timeLimit: raw.timeLimit ?? raw.time_limit ?? 1,
      memoryLimit: raw.memoryLimit ?? raw.memory_limit ?? 256,
      exampleInput: raw.exampleInput ?? raw.example_input ?? '',
      exampleOutput: raw.exampleOutput ?? raw.example_output ?? '',
      problemType: raw.problemType ?? raw.problem_type ?? 'NORMAL',
      createdAt: raw.createdAt ?? raw.created_at ?? null
    }
    return {
      isLogined: res?.isLogined ?? true,
      problem,
      userStatus: res?.userStatus ?? raw.userStatus ?? null,
      statistics: res?.statistics ?? raw.statistics ?? { submissionCount: 0, successCount: 0 }
    }
  } catch (err) {
    if (err.response?.status === 404) {
      const fallback = getProblemDetailFromMock(id)
      if (fallback) return fallback
    }
    throw err
  }
}
