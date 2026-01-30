import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api'

export const useProfileStore = defineStore('profile', () => {
    //userdashboard
    const user = ref(null)

    //report
    const reports = ref([])

    const userinfo = async () => {
        try {   
            const res = await api.get('/users/profiles')
            user.value = res.data.data
        } catch (err) {
            console.warn('[profile.userinfo] failed:', err?.response?.status, err?.response?.data ?? err)
        }
    }

    // const reportList = async (params) => {
    //     try {
    //         const res = await api.get('/reports/me', { params })
    //         reports.value = res.data.data
    //         console.log(res.data.message)
    //     } catch (err) {
    //         console.warn('[profile.reportList] failed:', err?.response?.status, err?.response?.data ?? err)
    //     }
    // }

    return {
        user,
        // reports,
        userinfo,
        // reportList
    }
})