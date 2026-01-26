import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '@/api'

const normalizeCodingLevel = (codingLevel) => {
  if (typeof codingLevel === 'number') return codingLevel

    // 액션(actions): 상태를 변경하거나 비동기 작업을 수행하는 메서드
    actions: {
        /**
         * 회원가입 액션
         * @param {Object} signupData - 회원가입 폼 데이터
         * @param {string} signupData.email - 이메일
         * @param {string} signupData.password - 비밀번호
         * @param {string} signupData.name - 이름
         * @param {string} signupData.nickname - 닉네임
         * @param {number} signupData.age - 나이
         * @param {number} signupData.codingLevel - 코딩 레벨 (1~5)
         * @returns {Promise} API 응답 데이터
         * @throws {Error} API 요청 실패 시 에러 발생
         */
        async signup(signupData) {
            // 로딩 상태 시작
            this.isLoading = true
            try {
                // codingLevel은 이미 숫자 타입으로 전달됨 (프론트엔드에서 v-model.number 사용)
                // 유효성 검사만 수행
                if (typeof signupData.codingLevel !== 'number' || 
                    signupData.codingLevel < 1 || 
                    signupData.codingLevel > 5) {
                    throw new Error(`유효하지 않은 코딩 레벨입니다: ${signupData.codingLevel}`)
                }
                
                // POST /api/v1/users/signup 엔드포인트로 회원가입 요청
                const requestData = {
                    email: signupData.email,
                    password: signupData.password,
                    name: signupData.name,
                    nickname: signupData.nickname,
                    age: signupData.age,
                    codingLevel: signupData.codingLevel
                }
                
                const response = await api.post('/users/signup', requestData)
                // 성공 시 응답 데이터 반환
                return response.data
            } catch (error) {
                // 에러 발생 시 상위로 전파 (컴포넌트에서 처리)
                throw error
            } finally {
                // 성공/실패 여부와 관계없이 로딩 상태 종료
                this.isLoading = false
            }
        },

        /**
         * 이메일 중복 확인 액션
         * @param {string} email - 확인할 이메일
         * @returns {Promise<boolean>} 사용 가능하면 true, 중복이면 false
         * @throws {Error} API 요청 실패 시 에러 발생
         */
        async checkEmailDuplicate(email) {
            try {
                const response = await api.post('/users/check/emails', { email })
                // response.data.data.isAvailable: 백엔드 응답 구조에 따라 조정
                return response.data?.data?.isAvailable ?? false
            } catch (error) {
                // 에러 발생 시 상위로 전파 (컴포넌트에서 처리)
                throw error
            }
        },

        /**
         * 닉네임 중복 확인 액션
         * @param {string} nickname - 확인할 닉네임
         * @returns {Promise<boolean>} 사용 가능하면 true, 중복이면 false
         * @throws {Error} API 요청 실패 시 에러 발생
         */
        async checkNicknameDuplicate(nickname) {
            try {
                const response = await api.post('/users/check/nicknames', { nickname })
                // response.data.data.isAvailable: 백엔드 응답 구조에 따라 조정
                return response.data?.data?.isAvailable ?? false
            } catch (error) {
                // 에러 발생 시 상위로 전파 (컴포넌트에서 처리)
                throw error
            }
        }
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
