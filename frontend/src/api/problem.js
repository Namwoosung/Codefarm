import api from './index'

/**
 * 백엔드 문제 응답을 프론트 도메인 모델로 변환하는 어댑터.
 * - 백엔드 필드명이 바뀌더라도 이 함수 한 곳에서만 대응하도록 캡슐화한다.
 * - TODO: 백엔드 스펙이 완전히 통일되면 legacy 필드(p.time_limit 등)는 정리한다.
 * @param {object} raw
 * @param {number} fallbackId
 * @returns {{ problemId:number, title:string, description:string, concept:string, difficulty:string, algorithm:any, timeLimit:number, memoryLimit:number, exampleInput:string, exampleOutput:string, problemType:string, createdAt:string|null }}
 */
function normalizeProblem(raw, fallbackId) {
  const p = raw ?? {}
  const id = p.problemId ?? fallbackId

  const difficulty =
    typeof p.difficulty === 'number' ? `LEVEL${p.difficulty}` : (p.difficulty ?? 'LEVEL1')

  return {
    problemId: id,
    title: p.title ?? '',
    description: p.description ?? '',
    concept: p.concept ?? '',
    difficulty,
    algorithm: p.algorithm ?? [],
    // legacy 필드 이름은 여기에서만 한 번에 처리
    timeLimit: p.timeLimit ?? p.time_limit ?? 1,
    memoryLimit: p.memoryLimit ?? p.memory_limit ?? 256,
    inputDescription: p.inputDescription ?? p.input_description ?? '',
    outputDescription: p.outputDescription ?? p.output_description ?? '',
    exampleInput: p.exampleInput ?? p.example_input ?? '',
    exampleOutput: p.exampleOutput ?? p.example_output ?? '',
    problemType: p.problemType ?? p.problem_type ?? 'NORMAL',
    createdAt: p.createdAt ?? p.created_at ?? null
  }
}

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
  console.log(items)
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

  // 백엔드 응답을 프론트 도메인 모델로 통일
  const problem = normalizeProblem(raw?.problem ?? raw, id)

  return {
    isLogined: raw?.isLogined ?? res?.isLogined ?? true,
    problem,
    userStatus: raw?.userStatus ?? null,
    statistics: raw?.statistics ?? { submissionCount: 0, successCount: 0 }
  }
}
