// TODO: 백엔드 API 연동이 완료되면 이 파일을 실제 호출로 교체합니다.
// import api from './index'
import mockProblems from '@/mocks/sampled_30_clean.json'

/**
 * 문제 상세 조회 (임시: 로컬 mock 데이터 사용)
 * @param {number|string} problemId - 문제 ID
 * @returns {Promise<{
 *   isLogined: boolean,
 *   problem: object,
 *   userStatus: object|null,
 *   statistics: { submissionCount: number, successCount: number }
 * }>}
 */
export const getProblemDetail = async (problemId) => {
  const id = Number(problemId)

  // sampled_30_clean.json 은 0-based 배열이므로, 임시로 (id - 1) 인덱스를 사용
  const raw = mockProblems[id - 1]

  if (!raw) {
    throw new Error(`Mock problem not found for id: ${id}`)
  }

  // difficulty 숫자를 LEVEL 문자열로 매핑
  const difficultyMap = {
    1: 'LEVEL1',
    2: 'LEVEL2',
    3: 'LEVEL3',
    4: 'LEVEL4',
    5: 'LEVEL5',
  }

  const problem = {
    problemId: id,
    title: raw.title,
    description: raw.description,
    difficulty: difficultyMap[raw.difficulty] || 'LEVEL1',
    algorithm: raw.algorithm,
    timeLimit: raw.time_limit ?? raw.timeLimit ?? 1,
    memoryLimit: raw.memory_limit ?? raw.memoryLimit ?? 256,
    exampleInput:
      raw.example_input ?? raw.exampleInput ?? (raw.exampleInput || ''),
    exampleOutput:
      raw.example_output ?? raw.exampleOutput ?? (raw.exampleOutput || ''),
    problemType: raw.problem_type ?? raw.problemType ?? 'NORMAL',
    createdAt: raw.createdAt ?? new Date().toISOString(),
  }

  // 실제 API 명세와 최대한 비슷한 형태로 반환
  return {
    isLogined: true,
    problem,
    // isLogined 가 false 인 경우 userStatus는 내려오지 않는 명세이므로,
    // 임시 mock에서는 로그인 된 상태로만 가정하고 userStatus는 null 로 둡니다.
    userStatus: null,
    statistics: {
      submissionCount: 0,
      successCount: 0,
    },
  }
}
