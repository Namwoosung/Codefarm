import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useToastStore = defineStore('toast', () => {
  const message = ref('')
  let timer = null

  function clearToast() {
    message.value = ''
    if (timer) clearTimeout(timer)
    timer = null
  }

  function showToast(msg, { durationMs = 2600 } = {}) {
    message.value = String(msg ?? '')
    if (timer) clearTimeout(timer)
    timer = setTimeout(() => {
      message.value = ''
      timer = null
    }, durationMs)
  }

  return {
    message,
    showToast,
    clearToast,
  }
})

