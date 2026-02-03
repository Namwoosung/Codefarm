import api from './index'

/**
 * 코딩 레벨 정규화 함수
 * @param {string|number} codingLevel
 * @returns {number}
 */
export const normalizeCodingLevel = (codingLevel) => {
  if (typeof codingLevel === 'number') return codingLevel
  if (typeof codingLevel === 'string') {
    if (codingLevel.startsWith('LEVEL')) {
      return parseInt(codingLevel.replace('LEVEL', ''), 10)
    }
    return parseInt(codingLevel, 10)
  }
  return NaN
}

/**
 * 로그인
 * POST /api/v1/users/login
 * @param {{ email: string, password: string }} payload
 * @returns {Promise<{ data: { user: object, token: { accessToken: string, tokenType: string } } }>}
 */
export const login = async (payload) => {
  return api.post('/users/login', payload)
}

/**
 * 로그아웃
 * POST /api/v1/users/logout
 * @returns {Promise}
 */
export const logout = async () => {
  return api.post('/users/logout')
}

/**
 * 회원가입
 * POST /api/v1/users/signup
 * @param {{ email: string, password: string, name: string, nickname: string, age: number, codingLevel: number }} requestData
 * @returns {Promise}
 */
export const signup = async (requestData) => {
  return api.post('/users/signup', requestData)
}

/**
 * 이메일 중복 확인
 * POST /api/v1/users/check/emails
 * @param {string} email
 * @returns {Promise<{ data: { isAvailable: boolean } }>}
 */
export const checkEmailDuplicate = async (email) => {
  return api.post('/users/check/emails', { email })
}

/**
 * 닉네임 중복 확인
 * POST /api/v1/users/check/nicknames
 * @param {string} nickname
 * @returns {Promise<{ data: { isAvailable: boolean } }>}
 */
export const checkNicknameDuplicate = async (nickname) => {
  return api.post('/users/check/nicknames', { nickname })
}

/**
 * 사용자 프로필 조회
 * GET /api/v1/users/profiles
 * @returns {Promise<{ data: object }>}
 */
export const getUserProfile = async () => {
  return api.get('/users/profiles')
}
