import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getUserProfile, updateUserProfile, getMyReports, getReportDetail } from '@/api/profile'
import { useAuthStore } from '@/stores/auth'

export const useProfileStore = defineStore('profile', () => {
    //userdashboard
    const user = ref(null)

    //report
    const report = ref(null)
    const reports = ref([])
    // report list cache (마이페이지에서 최초 1회만 로드)
    const reportsFetched = ref(false)
    const lastReportListKey = ref('')

    const userinfo = async () => {
        try {   
            const res = await getUserProfile()
            user.value = res.data.data

            // auth/localStorage와 사용자 정보 일관성 유지
            try {
                const auth = useAuthStore()
                auth.user = user.value
                if (user.value) localStorage.setItem('user', JSON.stringify(user.value))
            } catch (_) {
                // noop
            }
        } catch (err) {
            console.log(err?.response?.data?.message ?? err?.message ?? err)
        }
    }
    const updateUser = async (payload) => {
        try {
            if (!payload || typeof payload !== 'object') {
                throw new Error('updateUser payload가 필요합니다.')
            }

            // 서버가 기대하는 키만 전송 (age, name, codingLevel, nickname)
            const requestBody = {
                age: payload.age,
                name: payload.name,
                codingLevel: payload.codingLevel,
                nickname: payload.nickname,
            }

            const res = await updateUserProfile(requestBody)
            user.value = res.data?.data ?? null

            // auth/localStorage와 사용자 정보 일관성 유지
            try {
                const auth = useAuthStore()
                auth.user = user.value
                if (user.value) localStorage.setItem('user', JSON.stringify(user.value))
            } catch (_) {
                // noop
            }

            console.log(res.data?.message)
            return res.data
        } catch (err) {
            console.log(err?.response?.data?.message ?? err?.message ?? err)
            throw err
        }
    }
    const reportList = async (params) => {
        try {
            const key = params ? JSON.stringify(params) : ''
            // 동일 params로 이미 로드했다면 재호출하지 않음
            if (reportsFetched.value && lastReportListKey.value === key) return

            const res = await getMyReports(params)
            reports.value = res.data.data
            reportsFetched.value = true
            lastReportListKey.value = key
            console.log(res.data.message)
            console.log(res.data.data)
        } catch (err) {
            console.log(err?.response?.data?.message ?? err?.message ?? err)
        }
    }

    // 다른 화면에서 리포트가 추가되는 케이스가 생기면 이걸 호출해서 다음 마이페이지 진입 시 재조회 가능
    const invalidateReportList = () => {
        reportsFetched.value = false
        lastReportListKey.value = ''
    }

    // 로그아웃/로그인 시 모든 상태 초기화 (회원 전환 시 이전 유저 정보 남는 문제 방지)
    const reset = () => {
        user.value = null
        report.value = null
        reports.value = []
        reportsFetched.value = false
        lastReportListKey.value = ''
    }

    const resportDetail = async (reportId) => {
        try {
            const res = await getReportDetail(reportId)
            report.value = res.data.data
            console.log(res.data.data)
        } catch (err) {
            console.log(err.data.message)
        }
    }
    return {
        user,
        report,
        reports,
        userinfo,
        reportList,
        invalidateReportList,
        resportDetail,
        updateUser,
        reset,
    }
})
