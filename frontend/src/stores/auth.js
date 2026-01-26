// Pinia 스토어 정의: 인증 관련 상태 및 액션 관리
import { defineStore } from 'pinia'
// API 클라이언트: axios 인스턴스 (baseURL, 인터셉터 설정 포함)
import api from '@/api'

/**
 * 인증 스토어 (auth store)
 * 회원가입, 로그인 등 인증 관련 상태와 액션을 관리
 */
export const useAuthStore = defineStore('auth', {
    // 상태(state): 스토어에서 관리하는 반응형 데이터
    state: () => ({
        user: null,        // 현재 로그인한 사용자 정보
        token: null,      // JWT 토큰 (인증 토큰)
        isLoading: false  // API 요청 중 로딩 상태
    }),

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
})
