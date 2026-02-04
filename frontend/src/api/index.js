import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

const api = axios.create({
  // Vite Proxy(/api)를 사용하므로 기본 경로를 /api로 설정
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
  headers: {
    // '타입/서브타입 (MIME type)'
    'Content-Type': 'application/json'
  }
})

// 인터셉터 설정 (필요 시 토큰 처리 에러 처리 등)
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

/** 401 시 로그아웃 처리 생략 옵션 (인증 불필요 요청: login, logout 등) */
export const SKIP_AUTH_ON_401 = 'skipAuthOn401'

// 401 시 토큰 제거 → 로그아웃 상태로 맞춤 (skipAuthOn401 요청은 제외)
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      const skipAuth = err.config?.[SKIP_AUTH_ON_401] === true
      if (!skipAuth) {
        try {
          useAuthStore().logout()
        } catch (_) {}
      }
    }
    return Promise.reject(err)
  }
)

export default api
