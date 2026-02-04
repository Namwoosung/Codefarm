import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { login as apiLogin, logout as apiLogout, signup as apiSignup, checkEmailDuplicate as apiCheckEmailDuplicate, checkNicknameDuplicate as apiCheckNicknameDuplicate, getUserProfile as apiGetUserProfile, normalizeCodingLevel } from '@/api/auth'

/** localStorage의 토큰을 읽어, 만료되었으면 제거하고 null 반환 */
function getValidTokenFromStorage() {
  const raw = localStorage.getItem('token')
  if (!raw) return null
  try {
    const payload = raw.split('.')[1]
    if (!payload) return raw
    const decoded = JSON.parse(atob(payload.replace(/-/g, '+').replace(/_/g, '/')))
    if (decoded.exp != null && typeof decoded.exp === 'number') {
      const now = Math.floor(Date.now() / 1000)
      if (decoded.exp < now) {
        localStorage.removeItem('token')
        return null
      }
    }
    return raw
  } catch {
    return raw
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(getValidTokenFromStorage())
  const user = ref(null)

  // 새로고침 시에도 로그인 상태 유지를 위해 user 복원
  try {
    const savedUser = localStorage.getItem('user')
    user.value = savedUser ? JSON.parse(savedUser) : null
  } catch {
    user.value = null
    localStorage.removeItem('user')
  }

  // LoginView는 loading, SignupForm은 isLoading을 사용 중이라 둘 다 제공
  const loading = ref(false)
  const isLoading = computed(() => loading.value)

  const errCode = ref(null)
  const errorMessage = ref(null)
  const isLoggedIn = computed(() => !!token.value)

  const login = async (payload) => {
    loading.value = true
    errCode.value = null
    errorMessage.value = null

    try {
      const res = await apiLogin(payload)
      const data = res.data?.data ?? {}
      // 백엔드: LoginResponseDto { user, token: { accessToken, tokenType } }
      user.value = data.user ?? null
      token.value = data.token?.accessToken ?? data.accessToken ?? null
      if (token.value) localStorage.setItem('token', token.value)
      if (user.value) localStorage.setItem('user', JSON.stringify(user.value))
      return res.data
    } catch (err) {
      errCode.value = err?.response?.data?.errorCode ?? null
      errorMessage.value = err?.response?.data?.message ?? null
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    const hadToken = !!token.value
    try {
      // 토큰이 있을 때만 서버에 로그아웃 요청 (없으면 401 난 요청이 또 인터셉터에서 logout 호출 → 무한 반복 방지)
      if (hadToken) {
        await api.post('/users/logout')
      }
    } catch (_) {
      // 로그아웃 API 실패(401 등)여도 클라이언트 상태는 항상 비움
    } finally {
      token.value = null
      user.value = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  }

  const signup = async (signupData) => {
    loading.value = true
    errCode.value = null
    errorMessage.value = null

    try {
      const codingLevelNumber = normalizeCodingLevel(signupData.codingLevel)
      if (Number.isNaN(codingLevelNumber) || codingLevelNumber < 1 || codingLevelNumber > 5) {
        throw new Error(`유효하지 않은 코딩 레벨입니다: ${signupData.codingLevel}`)
      }

      const requestData = {
        email: signupData.email,
        password: signupData.password,
        name: signupData.name,
        nickname: signupData.nickname,
        age: signupData.age,
        codingLevel: codingLevelNumber
      }

      const response = await apiSignup(requestData)
      return response.data
    } catch (err) {
      errCode.value = err?.response?.data?.errorCode ?? null
      errorMessage.value = err?.response?.data?.message ?? err?.message ?? null
      throw err
    } finally {
      loading.value = false
    }
  }

  const checkEmailDuplicate = async (email) => {
    const response = await apiCheckEmailDuplicate(email)
    return response.data?.data?.isAvailable ?? false
  }

  const checkNicknameDuplicate = async (nickname) => {
    const response = await apiCheckNicknameDuplicate(nickname)
    return response.data?.data?.isAvailable ?? false
  }

  /** 토큰은 있는데 user가 비어 있을 때(새로고침 등) GET /users/profiles로 사용자 복구 */
  const fetchUserIfNeeded = async () => {
    if (!token.value || user.value != null) return
    try {
      const res = await apiGetUserProfile()
      user.value = res.data?.data ?? null
    } catch (_) {
      // 401 등이면 인터셉터에서 이미 logout 처리됨
      user.value = null
    }
  }

  return {
    token,
    user,
    loading,
    isLoading,
    errCode,
    errorMessage,
    isLoggedIn,
    login,
    logout,
    signup,
    fetchUserIfNeeded,
    checkEmailDuplicate,
    checkNicknameDuplicate
  }
})
