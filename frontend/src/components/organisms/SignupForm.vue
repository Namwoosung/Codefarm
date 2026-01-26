<template>
  <div class="signup-form">
    <p class="text-center text-sm text-gray-600 mb-6">
      또는
      <router-link
        to="/login"
        class="font-medium text-blue-600 hover:text-blue-500"
      >
        로그인
      </router-link>
    </p>
    <!-- 기본 동작(로그인) 방지를 위해 prevent 추가 -->
    <!-- novalidate: 브라우저 기본 HTML5 검증 비활성화 (영어 메시지 방지) -->
    <form class="space-y-6" @submit.prevent="handleSubmit" novalidate>
      <div class="space-y-4">
        
        <!-- 이메일 -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">
            이메일
          </label>
          <!-- 
            id="email": HTML 요소의 고유 식별자, label과 연결하여 접근성 향상
            v-model="formData.email": Vue 양방향 데이터 바인딩, 입력값이 formData.email에 자동 반영
            type="email": 이메일 입력 필드로 지정, 브라우저 기본 이메일 형식 검증 제공
            required: 필수 입력 필드, 값이 없으면 브라우저 기본 검증 메시지 표시
            class: Tailwind CSS 클래스 (mt-1, appearance-none, relative, block, w-full, px-3, py-2, border, border-gray-300, placeholder-gray-500, text-gray-900, rounded-md, focus:outline-none, focus:ring-blue-500, focus:border-blue-500, focus:z-10, sm:text-sm) - 스타일링 및 레이아웃
            placeholder="example@email.com": 입력 전 보이는 힌트 텍스트, 사용자 가이드 제공
          -->
          <div class="relative">
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              @blur="checkEmail"
              @input="onEmailInput"
              :class="[
                'mt-1 appearance-none relative block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm placeholder-gray-500 text-gray-900',
                emailCheckStatus === 'duplicate' ? 'border-red-500' : 
                emailCheckStatus === 'available' ? 'border-green-500' : 
                'border-gray-300'
              ]"
              placeholder="example@email.com"
            />
            <span v-if="isCheckingEmail" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-400">
              확인 중...
            </span>
          </div>
          <p v-if="errors.email" class="mt-1 text-sm text-red-600">
            {{ errors.email }}
          </p>
          <p v-else-if="emailCheckStatus === 'available'" class="mt-1 text-sm text-green-600">
            ✓ 사용 가능한 이메일입니다.
          </p>
          <p v-else-if="emailCheckStatus === 'duplicate'" class="mt-1 text-sm text-red-600">
            ✗ 이미 사용 중인 이메일입니다.
          </p>
        </div>

        <!-- 비밀번호 -->
        <div>
          <label
            for="password"
            class="block text-sm font-medium text-gray-700"
          >
            비밀번호
          </label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            required
            minlength="8"
            maxlength="16"
            class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="영문, 숫자, 특수문자 포함 8자 이상 16자 이하"
          />
          <p v-if="errors.password" class="mt-1 text-sm text-red-600">
            {{ errors.password }}
          </p>
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label
            for="passwordConfirm"
            class="block text-sm font-medium text-gray-700"
          >
            비밀번호 확인
          </label>
          <input
            id="passwordConfirm"
            v-model="formData.passwordConfirm"
            type="password"
            required
            class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="비밀번호를 다시 입력해주세요"
          />
          <p
            v-if="errors.passwordConfirm"
            class="mt-1 text-sm text-red-600"
          >
            {{ errors.passwordConfirm }}
          </p>
        </div>

        <!-- 이름 -->
        <div>
          <label for="name" class="block text-sm font-medium text-gray-700">
            이름
          </label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            minlength="2"
            maxlength="50"
            class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="이름을 입력해주세요"
          />
          <p v-if="errors.name" class="mt-1 text-sm text-red-600">
            {{ errors.name }}
          </p>
        </div>

        <!-- 닉네임 -->
        <div>
          <label
            for="nickname"
            class="block text-sm font-medium text-gray-700"
          >
            닉네임
          </label>
          <div class="relative">
            <input
              id="nickname"
              v-model="formData.nickname"
              type="text"
              required
              minlength="2"
              maxlength="50"
              @blur="checkNickname"
              @input="onNicknameInput"
              :class="[
                'mt-1 appearance-none relative block w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm placeholder-gray-500 text-gray-900',
                nicknameCheckStatus === 'duplicate' ? 'border-red-500' : 
                nicknameCheckStatus === 'available' ? 'border-green-500' : 
                'border-gray-300'
              ]"
              placeholder="2자 이상 50자 이하"
            />
            <span v-if="isCheckingNickname" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-400">
              확인 중...
            </span>
          </div>
          <p v-if="errors.nickname" class="mt-1 text-sm text-red-600">
            {{ errors.nickname }}
          </p>
          <p v-else-if="nicknameCheckStatus === 'available'" class="mt-1 text-sm text-green-600">
            ✓ 사용 가능한 닉네임입니다.
          </p>
          <p v-else-if="nicknameCheckStatus === 'duplicate'" class="mt-1 text-sm text-red-600">
            ✗ 이미 사용 중인 닉네임입니다.
          </p>
        </div>

        <!-- 나이 -->
        <div>
          <label for="age" class="block text-sm font-medium text-gray-700">
            나이
          </label>
          <input
            id="age"
            v-model.number="formData.age"
            type="number"
            required
            min="1"
            max="150"
            class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm"
            placeholder="나이를 입력해주세요"
          />
          <p v-if="errors.age" class="mt-1 text-sm text-red-600">
            {{ errors.age }}
          </p>
        </div>

        <!-- 코딩 레벨 -->
        <div>
          <label
            for="codingLevel"
            class="block text-sm font-medium text-gray-700"
          >
            코딩 레벨
          </label>
          <select
            id="codingLevel"
            v-model.number="formData.codingLevel"
            required
            class="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option :value="null">선택해주세요</option>
            <option :value="1">LEVEL1</option>
            <option :value="2">LEVEL2</option>
            <option :value="3">LEVEL3</option>
            <option :value="4">LEVEL4</option>
            <option :value="5">LEVEL5</option>
          </select>
          <p v-if="errors.codingLevel" class="mt-1 text-sm text-red-600">
            {{ errors.codingLevel }}
          </p>
        </div>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="submitError" class="text-sm text-red-600 text-center">
        {{ submitError }}
      </div>

      <!-- 제출 버튼 -->
      <div>
        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!authStore.isLoading">회원가입</span>
          <span v-else>처리 중...</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
// Vue 3의 반응형 API: ref(단일 값), reactive(객체) - 데이터 변경 시 자동으로 UI 업데이트
import { ref, reactive } from 'vue'
// Vue Router의 라우터 훅: 페이지 이동 등 라우팅 기능 제공
import { useRouter } from 'vue-router'
// Pinia auth 스토어: 회원가입 등 인증 관련 상태 관리
import { useAuthStore } from '@/stores/auth'

// Vue Router 인스턴스: 페이지 이동 등 라우팅 기능 사용
const router = useRouter()
// Pinia auth 스토어 인스턴스: 회원가입 API 호출 및 로딩 상태 관리
const authStore = useAuthStore()

// 중복 확인 상태 관리
const emailCheckStatus = ref('') // '', 'checking', 'available', 'duplicate'
const nicknameCheckStatus = ref('') // '', 'checking', 'available', 'duplicate'
const isCheckingEmail = ref(false)
const isCheckingNickname = ref(false)

// Debounce를 위한 타이머
let emailCheckTimer = null
let nicknameCheckTimer = null  

/**
 * 폼 데이터 (반응형 객체)
 * reactive: Vue 3의 반응형 API로, 객체를 반응형으로 만듦
 * - 객체의 속성이 변경되면 자동으로 UI가 업데이트됨 (v-model과 연동)
 * - ref와 달리 객체 전체를 반응형으로 만들 때 사용
 */
const formData = reactive({
  email: '',              // 이메일
  password: '',           // 비밀번호
  passwordConfirm: '',    // 비밀번호 확인
  name: '',              // 이름
  nickname: '',          // 닉네임
  age: null,             // 나이 (number 타입)
  codingLevel: null     // 코딩 레벨 (1~5, number 타입)
})

/**
 * 필드별 에러 메시지 (반응형 객체)
 * 각 필드의 유효성 검사 실패 시 표시할 에러 메시지 저장
 */
const errors = reactive({
  email: '',
  password: '',
  passwordConfirm: '',
  name: '',
  nickname: '',
  age: '',
  codingLevel: ''
})

/**
 * 제출 시 발생하는 전체 에러 메시지 (예: API 에러)
 * ref: 단일 값을 반응형으로 만듦 (문자열, 숫자 등)
 */
const submitError = ref('')
// isLoading은 authStore에서 관리하므로 로컬 변수 제거

/**
 * 폼 유효성 검사 함수
 * 모든 필드의 입력값을 검증하고 에러 메시지를 설정
 * @returns {boolean} 모든 검증을 통과하면 true, 실패하면 false
 */
const validateForm = () => {
  // 에러 초기화: 이전 검증 결과 제거
  Object.keys(errors).forEach((key) => {
    errors[key] = ''
  })
  submitError.value = ''

  // 검증 결과 플래그: 하나라도 실패하면 false로 변경
  let isValid = true

  // 이메일 필수 검사
  if (!formData.email.trim()) {
    errors.email = '이메일을 입력해주세요'
    isValid = false
  } else {
    // 이메일 형식 검사: 정규식을 사용하여 올바른 이메일 형식인지 확인
    // 형식: 문자열@문자열.문자열 (예: user@example.com)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(formData.email)) {
      errors.email = '올바른 이메일 형식을 입력해주세요'
      isValid = false
    } else if (emailCheckStatus.value === 'duplicate') {
      // 중복 확인 결과가 중복인 경우
      errors.email = '이미 사용 중인 이메일입니다'
      isValid = false
    } else if (emailCheckStatus.value === '') {
      // 중복 확인을 아직 하지 않은 경우
      errors.email = '이메일 중복 확인을 해주세요'
      isValid = false
    }
  }

  // 비밀번호 필수 검사
  if (!formData.password) {
    errors.password = '비밀번호를 입력해주세요'
    isValid = false
  } else {
    // 비밀번호 길이 검사: 8자 이상 16자 이하
    if (formData.password.length < 8 || formData.password.length > 16) {
      errors.password = '비밀번호는 8자 이상 16자 이하여야 합니다'
      isValid = false
    } else {
      // 비밀번호 복잡도 검사: 영문, 숫자, 특수문자를 모두 포함해야 함
      // 정규식을 사용하여 각 조건 확인
      const hasLetter = /[a-zA-Z]/.test(formData.password)        // 영문자 포함 여부
      const hasNumber = /[0-9]/.test(formData.password)           // 숫자 포함 여부
      const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(formData.password)  // 특수문자 포함 여부

      // 하나라도 없으면 에러
      if (!hasLetter || !hasNumber || !hasSpecialChar) {
        errors.password = '비밀번호는 영문, 숫자, 특수문자를 모두 포함해야 합니다'
        isValid = false
      }
    }
  }

  // 비밀번호 확인 필수 검사
  if (!formData.passwordConfirm) {
    errors.passwordConfirm = '비밀번호 확인을 입력해주세요'
    isValid = false
  } else if (formData.password !== formData.passwordConfirm) {
    // 비밀번호 일치 검사: 비밀번호와 비밀번호 확인이 동일한지 확인
    errors.passwordConfirm = '비밀번호가 일치하지 않습니다'
    isValid = false
  }

  // 이름 필수 검사
  if (!formData.name.trim()) {
    errors.name = '이름을 입력해주세요'
    isValid = false
  } else if (formData.name.trim().length < 2 || formData.name.trim().length > 50) {
    // 이름 길이 검사: 공백 제거 후 2자 이상 50자 이하
    errors.name = '이름은 2자 이상 50자 이하여야 합니다'
    isValid = false
  }

  // 닉네임 필수 검사
  if (!formData.nickname.trim()) {
    errors.nickname = '닉네임을 입력해주세요'
    isValid = false
  } else if (formData.nickname.trim().length < 2 || formData.nickname.trim().length > 50) {
    // 닉네임 길이 검사: 공백 제거 후 2자 이상 50자 이하
    errors.nickname = '닉네임은 2자 이상 50자 이하여야 합니다'
    isValid = false
  } else if (nicknameCheckStatus.value === 'duplicate') {
    // 중복 확인 결과가 중복인 경우
    errors.nickname = '이미 사용 중인 닉네임입니다'
    isValid = false
  } else if (nicknameCheckStatus.value === '') {
    // 중복 확인을 아직 하지 않은 경우
    errors.nickname = '닉네임 중복 확인을 해주세요'
    isValid = false
  }

  // 나이 필수 검사
  // null, undefined, 빈 문자열 모두 체크 (number 타입이므로)
  if (formData.age === null || formData.age === undefined || formData.age === '') {
    errors.age = '나이를 입력해주세요'
    isValid = false
  } else if (formData.age < 1 || formData.age > 150) {
    // 나이 범위 검사: 1 이상 150 이하
    errors.age = '올바른 나이를 입력해주세요 (1-150)'
    isValid = false
  }

  // 코딩 레벨 선택 검사: null이 아니고 1~5 사이의 값인지 확인
  if (formData.codingLevel === null || formData.codingLevel === undefined) {
    errors.codingLevel = '코딩 레벨을 선택해주세요'
    isValid = false
  } else if (formData.codingLevel < 1 || formData.codingLevel > 5) {
    errors.codingLevel = '올바른 코딩 레벨을 선택해주세요'
    isValid = false
  }

  // 모든 검증 통과 여부 반환
  return isValid
}

/**
 * 폼 제출 핸들러
 * 유효성 검사 후 Pinia 스토어를 통해 회원가입 API 호출
 */
const handleSubmit = async () => {
  // 유효성 검사 실패 시 제출 중단
  if (!validateForm()) {
    return
  }

  // 이전 에러 메시지 초기화
  submitError.value = ''

  try {
    // Pinia 스토어의 signup 액션 호출
    // authStore.isLoading이 자동으로 true로 변경됨
    await authStore.signup({
      email: formData.email,
      password: formData.password,
      name: formData.name,
      nickname: formData.nickname,
      age: formData.age,
      codingLevel: formData.codingLevel
    })

    // 성공 시 로그인 페이지로 이동
    router.push('/login')
  } catch (error) {
    // API 에러 발생 시 에러 메시지 표시
    // error.response?.data?.message: 백엔드에서 전달한 에러 메시지
    // 없으면 기본 메시지 표시
    submitError.value =
      error.response?.data?.message || '회원가입에 실패했습니다. 다시 시도해주세요.'
  }
}

/**
 * 이메일 입력 핸들러 (debounce 적용)
 * 사용자가 입력을 멈춘 후 500ms 후에 중복 확인
 */
const onEmailInput = () => {
  // 이전 타이머 취소
  if (emailCheckTimer) {
    clearTimeout(emailCheckTimer)
  }
  
  // 상태 초기화
  emailCheckStatus.value = ''
  
  // 이메일 형식이 올바른 경우에만 debounce 후 확인
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (formData.email.trim() && emailRegex.test(formData.email.trim())) {
    emailCheckTimer = setTimeout(() => {
      checkEmail()
    }, 500) // 500ms 후 실행
  }
}

/**
 * 이메일 중복 확인 함수
 */
const checkEmail = async () => {
  const email = formData.email.trim()
  
  // 이메일이 비어있거나 형식이 올바르지 않으면 확인하지 않음
  if (!email) {
    emailCheckStatus.value = ''
    return
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    emailCheckStatus.value = ''
    return
  }
  
  try {
    isCheckingEmail.value = true
    emailCheckStatus.value = 'checking'
    
    const isAvailable = await authStore.checkEmailDuplicate(email)
    
    emailCheckStatus.value = isAvailable ? 'available' : 'duplicate'
  } catch (error) {
    console.error('이메일 중복 확인 실패:', error)
    emailCheckStatus.value = ''
    // 에러 발생 시 상태 초기화 (사용자가 다시 시도할 수 있도록)
  } finally {
    isCheckingEmail.value = false
  }
}

/**
 * 닉네임 입력 핸들러 (debounce 적용)
 * 사용자가 입력을 멈춘 후 500ms 후에 중복 확인
 */
const onNicknameInput = () => {
  // 이전 타이머 취소
  if (nicknameCheckTimer) {
    clearTimeout(nicknameCheckTimer)
  }
  
  // 상태 초기화
  nicknameCheckStatus.value = ''
  
  // 닉네임 길이가 유효한 경우에만 debounce 후 확인
  const trimmedNickname = formData.nickname.trim()
  if (trimmedNickname.length >= 2 && trimmedNickname.length <= 50) {
    nicknameCheckTimer = setTimeout(() => {
      checkNickname()
    }, 500) // 500ms 후 실행
  }
}

/**
 * 닉네임 중복 확인 함수
 */
const checkNickname = async () => {
  const nickname = formData.nickname.trim()
  
  // 닉네임이 비어있거나 길이가 유효하지 않으면 확인하지 않음
  if (!nickname || nickname.length < 2 || nickname.length > 50) {
    nicknameCheckStatus.value = ''
    return
  }
  
  try {
    isCheckingNickname.value = true
    nicknameCheckStatus.value = 'checking'
    
    const isAvailable = await authStore.checkNicknameDuplicate(nickname)
    
    nicknameCheckStatus.value = isAvailable ? 'available' : 'duplicate'
  } catch (error) {
    console.error('닉네임 중복 확인 실패:', error)
    nicknameCheckStatus.value = ''
    // 에러 발생 시 상태 초기화 (사용자가 다시 시도할 수 있도록)
  } finally {
    isCheckingNickname.value = false
  }
}
</script>

<style scoped>
.signup-form {
  width: 100%;
}
</style>
