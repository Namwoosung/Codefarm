import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/api'

const normalizeCodingLevel = (codingLevel) => {
  if (typeof codingLevel === 'number') return codingLevel

  if (typeof codingLevel === 'string') {
    if (codingLevel.startsWith('LEVEL')) {
      return parseInt(codingLevel.replace('LEVEL', ''), 10)
    }
    return parseInt(codingLevel, 10)
  }

  return NaN
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(null)

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
      const res = await api.post('/users/login', payload)
      user.value = res.data?.data?.user ?? null
      token.value = res.data?.data?.token?.accessToken ?? null
      if (token.value) localStorage.setItem('token', token.value)
      return res.data
    } catch (err) {
      errCode.value = err?.response?.data?.errorCode ?? null
      errorMessage.value = err?.response?.data?.message ?? null
      throw err
    } finally {
      loading.value = false
    }
  }

  const logout = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
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

      const response = await api.post('/users/signup', requestData)
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
    const response = await api.post('/users/check/emails', { email })
    return response.data?.data?.isAvailable ?? false
  }

  const checkNicknameDuplicate = async (nickname) => {
    const response = await api.post('/users/check/nicknames', { nickname })
    return response.data?.data?.isAvailable ?? false
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
    checkEmailDuplicate,
    checkNicknameDuplicate
  }
})
