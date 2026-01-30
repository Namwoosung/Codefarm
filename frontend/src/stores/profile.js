import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

export const useProfileStore = defineStore('profile', () => {
    //userdashboard
    const user = ref(null)

    //report
    const reports = ref([])

    const userinfo = async () => {
        try {   
            const res = await api.get('/users/profiles')
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

            const res = await api.patch('/users/profiles', requestBody)
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
    // const reportList = async (params) => {
    //     try {
    //         const res = await api.get('/reports/me', { params })
    //         reports.value = res.data.data
    //         console.log(res.data.message)
    //     } catch (err) {
    //         console.log(err.data.message)
    //     }
    // }

    return {
        user,
        // reports,
        userinfo,
        // reportList
        updateUser
    }
})