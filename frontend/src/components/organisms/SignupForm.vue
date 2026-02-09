<template>
  <div class="signup-form">
    <p v-if="!embedded" class="text-center text-sm text-farm-brown/70 mb-6">
      또는
      <router-link to="/login" class="font-medium text-farm-point hover:underline">
        로그인
      </router-link>
    </p>
    <form class="space-y-6" @submit.prevent="handleSubmit" novalidate>
      <div class="space-y-3">
        
        <!-- 이메일 -->
        <div>
          <label for="email" class="block text-sm font-medium text-farm-brown-dark">
            이메일
          </label>
          <p class="mt-0.5 text-xs text-farm-brown/60">정상적인 이메일 형식만 가입 가능합니다 (예: example@gmail.com)</p>
          <div class="relative">
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              autocomplete="email"
              @blur="onEmailBlur"
              @input="onEmailInput"
              :class="[
                'signup-input mt-2 block w-full px-4 py-2.5 rounded-xl border bg-farm-paper text-farm-brown-dark placeholder:text-farm-brown/40 focus:outline-none focus:ring-2 focus:z-10 sm:text-sm',
                emailFormatInvalid || emailCheckStatus === 'duplicate' ? 'border-farm-point focus:border-farm-point focus:ring-farm-point/20' :
                emailCheckStatus === 'available' ? 'border-farm-green focus:border-farm-green focus:ring-farm-green/20' :
                'border-farm-brown/20 focus:border-farm-point focus:ring-farm-point/20'
              ]"
              placeholder="example@email.com"
            />
            <span v-if="isCheckingEmail" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-farm-brown/50">
              확인 중...
            </span>
          </div>
          <p v-if="errors.email || emailFormatInvalid" class="mt-1 text-sm text-farm-point">
            {{ emailFormatInvalid ? '정상적인 이메일 형식이 아닙니다. (예: example@gmail.com, user@naver.co.kr)' : errors.email }}
          </p>
          <p v-else-if="emailCheckStatus === 'available'" class="mt-1 text-sm text-farm-green-dark">
            ✓ 사용 가능한 이메일입니다.
          </p>
          <p v-else-if="emailCheckStatus === 'duplicate'" class="mt-1 text-sm text-farm-point">
            ✗ 이미 사용 중인 이메일입니다.
          </p>
        </div>

        <!-- 비밀번호 -->
        <div>
          <label
            for="password"
            class="block text-sm font-medium text-farm-brown-dark"
          >
            비밀번호
          </label>
          <p class="mt-0.5 text-xs text-farm-brown/60">영문, 숫자, 특수문자 포함 8자 이상 16자 이하</p>
          <div class="relative mt-1">
            <input
              id="password"
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              required
              minlength="8"
              maxlength="16"
              autocomplete="new-password"
              :class="[
                'signup-input block w-full px-4 py-2.5 pr-10 rounded-xl border bg-farm-paper text-farm-brown-dark placeholder:text-farm-brown/40 focus:outline-none focus:ring-2 focus:z-10 sm:text-sm',
                formData.password && passwordValidation.status === 'invalid' ? 'border-farm-point focus:border-farm-point focus:ring-farm-point/20' :
                formData.password && passwordValidation.status === 'valid' ? 'border-farm-green focus:border-farm-green focus:ring-farm-green/20' : 'border-farm-brown/20 focus:border-farm-point focus:ring-farm-point/20'
              ]"
              placeholder="비밀번호 입력"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 flex items-center justify-center w-10 text-farm-brown/50 hover:text-farm-brown-dark focus:outline-none"
              :aria-label="showPassword ? '비밀번호 숨기기' : '비밀번호 보기'"
              @click="showPassword = !showPassword"
            >
              <iconify-icon :icon="showPassword ? 'mdi:eye-off' : 'mdi:eye'" class="text-xl"></iconify-icon>
            </button>
          </div>
          <p v-if="errors.password" class="mt-1 text-sm text-farm-point">
            {{ errors.password }}
          </p>
          <p v-else-if="passwordValidation.message" class="mt-1 text-sm" :class="passwordValidation.status === 'valid' ? 'text-farm-green-dark' : 'text-farm-point'">
            {{ passwordValidation.message }}
          </p>
        </div>

        <!-- 비밀번호 확인 -->
        <div>
          <label
            for="passwordConfirm"
            class="block text-sm font-medium text-farm-brown-dark"
          >
            비밀번호 확인
          </label>
          <div class="relative mt-2">
            <input
              id="passwordConfirm"
              v-model="formData.passwordConfirm"
              :type="showPasswordConfirm ? 'text' : 'password'"
              required
              autocomplete="new-password"
              class="signup-input block w-full px-4 py-2.5 pr-10 rounded-xl border border-farm-brown/20 bg-farm-paper text-farm-brown-dark placeholder:text-farm-brown/40 focus:outline-none focus:ring-2 focus:border-farm-point focus:ring-farm-point/20 focus:z-10 sm:text-sm"
              placeholder="비밀번호를 다시 입력해주세요"
            />
            <button
              type="button"
              class="absolute inset-y-0 right-0 flex items-center justify-center w-10 text-farm-brown/50 hover:text-farm-brown-dark focus:outline-none"
              :aria-label="showPasswordConfirm ? '비밀번호 숨기기' : '비밀번호 보기'"
              @click="showPasswordConfirm = !showPasswordConfirm"
            >
              <iconify-icon :icon="showPasswordConfirm ? 'mdi:eye-off' : 'mdi:eye'" class="text-xl"></iconify-icon>
            </button>
          </div>
          <p
            v-if="errors.passwordConfirm"
            class="mt-1 text-sm text-farm-point"
          >
            {{ errors.passwordConfirm }}
          </p>
        </div>

        <!-- 이름 -->
        <div>
          <label for="name" class="block text-sm font-medium text-farm-brown-dark">
            이름
          </label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            minlength="2"
            maxlength="20"
            @blur="onNameBlur"
            @input="onNameInput"
            :class="[
              'signup-input mt-2 block w-full px-4 py-2.5 rounded-xl border bg-farm-paper text-farm-brown-dark placeholder:text-farm-brown/40 focus:outline-none focus:ring-2 focus:z-10 sm:text-sm',
              nameShouldShowValidation && nameValidation.status === 'invalid' ? 'border-farm-point focus:ring-farm-point/20' :
              nameShouldShowValidation && nameValidation.status === 'valid' ? 'border-farm-green focus:ring-farm-green/20' :
              'border-farm-brown/20 focus:border-farm-point focus:ring-farm-point/20'
            ]"
            placeholder="이름을 입력해주세요"
          />
          <p v-if="errors.name" class="mt-1 text-sm text-farm-point">
            {{ errors.name }}
          </p>
          <p v-else-if="nameShouldShowValidation && nameValidation.message" class="mt-1 text-sm" :class="nameValidation.status === 'valid' ? 'text-farm-green-dark' : 'text-farm-point'">
            {{ nameValidation.message }}
          </p>
        </div>

        <!-- 닉네임 -->
        <div>
          <label
            for="nickname"
            class="block text-sm font-medium text-farm-brown-dark"
          >
            닉네임
          </label>
          <p class="mt-0.5 text-xs text-farm-brown/60">한글, 영문, 숫자, _, - 만 사용 가능 (2~20자, 특수문자 금지)</p>
          <div class="relative">
            <input
              id="nickname"
              v-model="formData.nickname"
              type="text"
              required
              minlength="2"
              maxlength="20"
              @blur="checkNickname"
              @input="onNicknameInput"
              :class="[
                'signup-input mt-2 block w-full px-4 py-2.5 rounded-xl border bg-farm-paper text-farm-brown-dark placeholder:text-farm-brown/40 focus:outline-none focus:ring-2 focus:z-10 sm:text-sm',
                nicknameFormatInvalid || nicknameCheckStatus === 'duplicate' ? 'border-farm-point focus:ring-farm-point/20' :
                nicknameCheckStatus === 'available' ? 'border-farm-green focus:ring-farm-green/20' :
                'border-farm-brown/20 focus:border-farm-point focus:ring-farm-point/20'
              ]"
              placeholder="2~20자, 한글/영문/숫자/_, - 만 가능"
            />
            <span v-if="isCheckingNickname" class="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-farm-brown/50">
              확인 중...
            </span>
          </div>
          <p v-if="errors.nickname" class="mt-1 text-sm text-farm-point">
            {{ errors.nickname }}
          </p>
          <p v-else-if="nicknameFormatInvalid" class="mt-1 text-sm text-farm-point">
            닉네임은 한글, 영문, 숫자, _, - 만 사용 가능하며 2~20자로 입력해주세요.
          </p>
          <p v-else-if="nicknameCheckStatus === 'available'" class="mt-1 text-sm text-farm-green-dark">
            ✓ 사용 가능한 닉네임입니다.
          </p>
          <p v-else-if="nicknameCheckStatus === 'duplicate'" class="mt-1 text-sm text-farm-point">
            ✗ 이미 사용 중인 닉네임입니다.
          </p>
        </div>

        <!-- 나이 -->
        <div>
          <label for="age" class="block text-sm font-medium text-farm-brown-dark">
            나이
          </label>
          <input
            id="age"
            v-model.number="formData.age"
            type="number"
            required
            min="1"
            max="150"
            class="signup-input mt-2 block w-full px-4 py-2.5 rounded-xl border border-farm-brown/20 bg-farm-paper text-farm-brown-dark placeholder:text-farm-brown/40 focus:outline-none focus:ring-2 focus:border-farm-point focus:ring-farm-point/20 focus:z-10 sm:text-sm"
            placeholder="나이를 입력해주세요"
          />
          <p v-if="errors.age" class="mt-1 text-sm text-farm-point">
            {{ errors.age }}
          </p>
        </div>

        <!-- 코딩 레벨 -->
        <div>
          <label
            for="codingLevel"
            class="block text-sm font-medium text-farm-brown-dark"
          >
            코딩 레벨
          </label>
          <select
            id="codingLevel"
            v-model.number="formData.codingLevel"
            required
            class="signup-input mt-2 block w-full px-4 py-2.5 rounded-xl border border-farm-brown/20 bg-farm-paper text-farm-brown-dark focus:outline-none focus:ring-2 focus:border-farm-point focus:ring-farm-point/20 sm:text-sm"
          >
            <option :value="null">선택해주세요</option>
            <option :value="1">LEVEL1</option>
            <option :value="2">LEVEL2</option>
            <option :value="3">LEVEL3</option>
            <option :value="4">LEVEL4</option>
            <option :value="5">LEVEL5</option>
          </select>
          <p v-if="errors.codingLevel" class="mt-1 text-sm text-farm-point">
            {{ errors.codingLevel }}
          </p>
        </div>
      </div>

      <!-- 에러 메시지 -->
      <div v-if="submitError" class="text-sm text-farm-point text-center">
        {{ submitError }}
      </div>

      <!-- 제출 버튼 -->
      <div>
        <button
          type="submit"
          :disabled="authStore.isLoading"
          class="w-full flex justify-center py-3 px-4 text-sm font-medium rounded-xl text-farm-paper bg-farm-point hover:bg-farm-point/90 active:scale-[0.99] transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-farm-point/40 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="!authStore.isLoading">회원가입</span>
          <span v-else>처리 중...</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// 비밀번호: 영문, 숫자, 특수문자 포함 8~16자
const PASSWORD_MIN = 8
const PASSWORD_MAX = 16
const PASSWORD_HAS_LETTER = /[a-zA-Z]/
const PASSWORD_HAS_NUMBER = /[0-9]/
const PASSWORD_HAS_SPECIAL = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/

// 이름: 한글, 영문, 띄어쓰기 가능, 2~20자 (숫자/특수문자 불가)
const NAME_REGEX = /^[가-힣a-zA-Z\s]{2,20}$/

// 닉네임: 한글, 영문, 숫자, _, - 만 가능, 2~20자
const NICKNAME_REGEX = /^[가-힣a-zA-Z0-9_-]{2,20}$/

// 이메일: 일반적인 TLD만 허용 (정상적인 이메일 형식)
const VALID_TLDS = new Set([
  'com', 'net', 'org', 'edu', 'gov', 'info', 'biz', 'co', 'io', 'me', 'kr', 'jp', 'cn', 'uk', 'us', 'de', 'fr', 'au', 'ca', 'ru', 'br', 'in', 'it', 'es', 'nl', 'tv', 'cc', 'ac', 'go', 'ne', 'or', 're', 'mil'
])
const VALID_TLD_PAIRS = new Set(['co.kr', 'go.kr', 'ne.kr', 'or.kr', 're.kr', 'ac.kr', 'com.au', 'co.jp', 'ne.jp', 'co.uk', 'ac.uk', 'com.cn'])

function isValidEmailFormat(email) {
  const trimmed = (email || '').trim()
  if (!trimmed) return false
  const at = trimmed.indexOf('@')
  if (at <= 0 || at === trimmed.length - 1) return false
  const local = trimmed.slice(0, at)
  const domain = trimmed.slice(at + 1)
  if (!/^[a-zA-Z0-9._%+-]+$/.test(local)) return false
  const parts = domain.split('.').map(p => p.toLowerCase())
  if (parts.length < 2) return false
  const tldPair = parts.length >= 2 ? `${parts[parts.length - 2]}.${parts[parts.length - 1]}` : ''
  const tld = parts[parts.length - 1]
  const validTld = VALID_TLDS.has(tld) || VALID_TLD_PAIRS.has(tldPair)
  if (!validTld) return false
  if (parts.some(p => !p)) return false
  if (parts[parts.length - 1].length < 2) return false
  if (parts[0].length < 2) return false
  return true
}

const props = defineProps({
  /** 로그인/회원가입 스왑 화면에 포함될 때 true */
  embedded: { type: Boolean, default: false }
})

const emit = defineEmits(['signed-up'])
const router = useRouter()
const authStore = useAuthStore()

// 중복 확인 상태 관리
const emailCheckStatus = ref('')
const nicknameCheckStatus = ref('') 
const isCheckingEmail = ref(false)
const isCheckingNickname = ref(false)

// Debounce를 위한 타이머
let emailCheckTimer = null
let nicknameCheckTimer = null
let nameDebounceTimer = null

// 이름 검증 표시 시점: blur 또는 500ms 입력 대기 후
const nameHasBeenBlurred = ref(false)
const nameDebounceFired = ref(false)
const nameShouldShowValidation = computed(() => nameHasBeenBlurred.value || nameDebounceFired.value)

// 입력 단 실시간 형식 검증용 (표시만, 제출 시 validateForm에서도 검사)
const emailFormatInvalid = computed(() => {
  const trimmed = (formData.email || '').trim()
  return trimmed.length > 0 && !isValidEmailFormat(formData.email)
})
const nicknameFormatInvalid = computed(() => {
  const trimmed = (formData.nickname || '').trim()
  return trimmed.length > 0 && !NICKNAME_REGEX.test(trimmed)
})

// 이름 실시간 검증 (2~20자, 한글/영문/띄어쓰기만 허용)
const nameValidation = computed(() => {
  const trimmed = (formData.name || '').trim()
  if (!trimmed) return { status: '', message: '' }

  if (trimmed.length < 2 || trimmed.length > 20) {
    return { status: 'invalid', message: '이름은 2자 이상 20자 이하여야 합니다.' }
  }

  if (!NAME_REGEX.test(trimmed)) {
    return { status: 'invalid', message: '이름에는 한글, 영문, 띄어쓰기만 사용할 수 있습니다.' }
  }

  return { status: 'valid', message: '✓ 사용 가능한 이름입니다.' }
})

// 비밀번호 보기/숨기기 토글
const showPassword = ref(false)
const showPasswordConfirm = ref(false)

// 비밀번호 실시간 검증 (영문, 숫자, 특수문자 포함 8~16자)
const passwordValidation = computed(() => {
  const p = formData.password
  if (!p) return { status: '', message: '' }
  if (p.length < PASSWORD_MIN || p.length > PASSWORD_MAX) {
    return { status: 'invalid', message: `8자 이상 16자 이하여야 합니다. (현재 ${p.length}자)` }
  }
  if (!PASSWORD_HAS_LETTER.test(p)) return { status: 'invalid', message: '영문자를 포함해주세요.' }
  if (!PASSWORD_HAS_NUMBER.test(p)) return { status: 'invalid', message: '숫자를 포함해주세요.' }
  if (!PASSWORD_HAS_SPECIAL.test(p)) return { status: 'invalid', message: '특수문자를 포함해주세요.' }
  return { status: 'valid', message: '✓ 영문, 숫자, 특수문자 포함 8~16자 조건을 만족합니다.' }
})

/* 폼 데이터 */
const formData = reactive({
  email: '',         
  password: '',          
  passwordConfirm: '',    
  name: '',            
  nickname: '',         
  age: null,             
  codingLevel: null    
})

/**
 * 필드별 에러 메시지 
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
 */
const submitError = ref('')

/**
 * 폼 유효성 검사 함수
 * @returns {boolean} 모든 검증을 통과하면 true, 실패하면 false
 */
const validateForm = () => {
  Object.keys(errors).forEach((key) => {
    errors[key] = ''
  })
  submitError.value = ''

  // 검증 결과 플래그: 하나라도 실패하면 false로 변경
  let isValid = true

  // 이메일 필수 및 형식 검사 (정상적인 이메일만 허용)
  if (!formData.email.trim()) {
    errors.email = '이메일을 입력해주세요'
    isValid = false
  } else if (!isValidEmailFormat(formData.email)) {
    errors.email = '정상적인 이메일 형식이 아닙니다. (예: example@gmail.com, user@naver.co.kr)'
    isValid = false
  } else if (emailCheckStatus.value === 'duplicate') {
    errors.email = '이미 사용 중인 이메일입니다'
    isValid = false
  } else if (emailCheckStatus.value === '') {
    errors.email = '이메일 중복 확인을 해주세요'
    isValid = false
  }

  // 비밀번호: 영문, 숫자, 특수문자 포함 8자 이상 16자 이하
  if (!formData.password) {
    errors.password = '비밀번호를 입력해주세요'
    isValid = false
  } else if (formData.password.length < PASSWORD_MIN || formData.password.length > PASSWORD_MAX) {
    errors.password = `비밀번호는 ${PASSWORD_MIN}자 이상 ${PASSWORD_MAX}자 이하여야 합니다`
    isValid = false
  } else if (!PASSWORD_HAS_LETTER.test(formData.password) || !PASSWORD_HAS_NUMBER.test(formData.password) || !PASSWORD_HAS_SPECIAL.test(formData.password)) {
    errors.password = '비밀번호는 영문, 숫자, 특수문자를 모두 포함해야 합니다'
    isValid = false
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

  // 이름: 2~20자, 숫자/특수문자 불가
  const trimmedName = formData.name.trim()
  if (!trimmedName) {
    errors.name = '이름을 입력해주세요'
    isValid = false
  } else if (trimmedName.length < 2 || trimmedName.length > 20) {
    errors.name = '이름은 2자 이상 20자 이하여야 합니다'
    isValid = false
  } else if (!NAME_REGEX.test(trimmedName)) {
    errors.name = '이름에는 한글, 영문, 띄어쓰기만 사용할 수 있습니다'
    isValid = false
  }

  // 닉네임: 한글, 영문, 숫자, _, - 만 가능, 2~20자
  const trimmedNickname = formData.nickname.trim()
  if (!trimmedNickname) {
    errors.nickname = '닉네임을 입력해주세요'
    isValid = false
  } else if (!NICKNAME_REGEX.test(trimmedNickname)) {
    errors.nickname = '닉네임은 한글, 영문, 숫자, _, - 만 사용 가능하며 2~20자로 입력해주세요'
    isValid = false
  } else if (nicknameCheckStatus.value === 'duplicate') {
    errors.nickname = '이미 사용 중인 닉네임입니다'
    isValid = false
  } else if (nicknameCheckStatus.value === '') {
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
  submitError.value = ''

  try {
    await authStore.signup({
      email: formData.email,
      password: formData.password,
      name: formData.name,
      nickname: formData.nickname,
      age: formData.age,
      codingLevel: formData.codingLevel
    })

    // 성공 시: 임베드 모드면 이벤트로 알리고 화면 전환은 부모가 처리
    if (props.embedded) {
      emit('signed-up', { email: formData.email })
      // 입력값 일부 초기화 (UX: 바로 로그인 가능하게 이메일은 유지해도 되지만, 여기선 초기화)
      formData.password = ''
      formData.passwordConfirm = ''
      submitError.value = ''
      return
    }

    // 기본 동작: 로그인 페이지로 이동
    router.push('/login')
  } catch (error) {
    submitError.value =
      error.response?.data?.message || '회원가입에 실패했습니다. 다시 시도해주세요.'
  }
}

/**
 * 이메일 입력 핸들러 (입력 단 실시간 형식 검증 + debounce 중복 확인)
 * 형식이 맞지 않으면 녹색/빨간 중복 결과는 숨기고, 형식 오류는 computed(emailFormatInvalid)로 표시
 */
const onEmailInput = () => {
  if (emailCheckTimer) clearTimeout(emailCheckTimer)
  emailCheckStatus.value = ''
  if (formData.email.trim() && !isValidEmailFormat(formData.email)) {
    errors.email = ''
    return
  }
  errors.email = ''
  if (formData.email.trim() && isValidEmailFormat(formData.email)) {
    emailCheckTimer = setTimeout(() => checkEmail(), 500)
  }
}

/** 이름 blur 시 검증 결과 표시 */
const onNameBlur = () => {
  nameHasBeenBlurred.value = true
}

/** 이름 입력 시 500ms debounce 후 검증 결과 표시 */
const onNameInput = () => {
  if (nameDebounceTimer) clearTimeout(nameDebounceTimer)
  nameDebounceTimer = setTimeout(() => {
    nameDebounceTimer = null
    nameDebounceFired.value = true
  }, 500)
}

/** 이메일 blur 시 형식이 유효할 때만 중복 확인 요청 */
const onEmailBlur = () => {
  if (formData.email.trim() && isValidEmailFormat(formData.email)) {
    checkEmail()
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
  
  if (!isValidEmailFormat(email)) {
    emailCheckStatus.value = ''
    return
  }
  
  try {
    isCheckingEmail.value = true
    emailCheckStatus.value = 'checking'
    
    const isAvailable = await authStore.checkEmailDuplicate(email)
    
    emailCheckStatus.value = isAvailable ? 'available' : 'duplicate'
  } catch (error) {
    // console.error('이메일 중복 확인 실패:', error)
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
  
  // 닉네임 형식·길이(2~20자, 한글/영문/숫자/_,-)가 유효할 때만 debounce 후 확인
  const trimmed = formData.nickname.trim()
  if (NICKNAME_REGEX.test(trimmed)) {
    nicknameCheckTimer = setTimeout(() => {
      checkNickname()
    }, 500)
  }
}

/**
 * 닉네임 중복 확인 함수
 */
const checkNickname = async () => {
  const nickname = formData.nickname.trim()
  
  // 닉네임이 비어있거나 형식(한글/영문/숫자/_,- 2~20자)이 맞지 않으면 확인하지 않음
  if (!nickname || !NICKNAME_REGEX.test(nickname)) {
    nicknameCheckStatus.value = ''
    return
  }
  
  try {
    isCheckingNickname.value = true
    nicknameCheckStatus.value = 'checking'
    
    const isAvailable = await authStore.checkNicknameDuplicate(nickname)
    
    nicknameCheckStatus.value = isAvailable ? 'available' : 'duplicate'
  } catch (error) {
    // console.error('닉네임 중복 확인 실패:', error)
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
