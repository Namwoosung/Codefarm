import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api' 

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token')||null);
  const user = ref(null);
  const loading = ref(false);
  const isLoggedIn = computed(() => !!token.value);
  const errCode = ref(null);
  const errorMessage = ref(null);

  const login = async (payload) => {
    loading.value = true;
    errCode.value = null;    
    errorMessage.value = null;
    try {
        const res = await api.post('/users/login', payload);
        user.value = res.data.data.user;
        token.value = res.data.data.token.accessToken;
        localStorage.setItem('token', token.value);
    } catch (err) {
        const code = err.response.data?.errorCode ?? null;
        const message = err.response.data?.message ?? null;
        errCode.value = code;
        errorMessage.value = message;
        throw err;
    } finally {
        loading.value = false;
    };
  }
  return { token, user, loading, errCode, errorMessage, isLoggedIn, login };
});