/**
 * 문제 유형(알고리즘) API 값 → 한글 표시명 매핑
 * 필터/카드/상세 등 모든 화면에서 동일하게 사용
 */
export const ALGORITHM_LABELS = {
  BRUTEFORCE: '완전탐색',
  QUEUE: '큐',
  STACK: '스택',
  GREEDY: '그리디',
  DP: '동적 프로그래밍',
  BFS: 'BFS',
  DFS: 'DFS',
  BINARY_SEARCH: '이진 탐색',
  TWO_POINTER: '투 포인터',
  SORT: '정렬',
  GRAPH: '그래프',
  STRING: '문자열',
  MATH: '수학',
  IMPLEMENTATION: '구현'
}

/**
 * @param {string} algorithm - API 값 (예: BRUTEFORCE, QUEUE)
 * @returns {string} 한글 표시명
 */
export function formatAlgorithmLabel(algorithm) {
  if (algorithm == null || algorithm === '') return '-'
  const upper = String(algorithm).toUpperCase()
  return ALGORITHM_LABELS[upper] ?? algorithm ?? '-'
}
