import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useIdeStore = defineStore('ide', () => {
  // 에디터에 입력된 코드
  const code = ref('')

  // 코드 업데이트 함수
  const updateCode = (newCode) => {
    code.value = newCode
  }

  // 코드 초기화 함수
  const resetCode = () => {
    code.value = ''
  }

  // 코드 가져오기 함수
  const getCode = () => {
    return code.value
  }

  return {
    code,
    updateCode,
    resetCode,
    getCode
  }
}, {
  persist: true // localStorage에 자동 저장
})
