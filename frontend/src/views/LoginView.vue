<template>
  <div class="auth-page">
    <div v-if="auth.loading" class="auth-loading fixed inset-0 flex items-center justify-center z-40 bg-farm-cream/80 backdrop-blur-sm">
      <div class="flex flex-col items-center gap-3">
        <span class="loading loading-spinner loading-lg text-farm-point"></span>
        <p class="text-sm font-medium text-farm-brown-dark">슉. 슈슉...</p>
      </div>
    </div>

    <div class="auth-shell" :class="{ 'right-panel-active': isSignup }">
      <!-- 회원가입 -->
      <div class="form-container sign-up-container">
        <div class="w-full max-w-md">
          <h1 class="text-2xl font-dnf text-farm-brown-dark mb-1">회원가입</h1>
          <p class="text-sm text-farm-brown/70 mb-6">
            <button type="button" class="text-farm-point hover:text-farm-point/80 font-medium md:hidden" @click="isSignup = false">
              ← 로그인으로
            </button>
          </p>
          <SignupForm embedded @signed-up="onSignedUp" />
        </div>
      </div>

      <!-- 로그인 -->
      <div class="form-container sign-in-container">
        <div class="w-full max-w-sm">
          <h1 class="text-2xl font-dnf text-farm-brown-dark mb-1">로그인</h1>
          <p class="text-sm text-farm-brown/70 mb-6">
            <button type="button" class="text-farm-point hover:text-farm-point/80 font-medium md:hidden" @click="isSignup = true">
              회원가입으로 →
            </button>
          </p>

          <p v-if="signupSuccessMessage" class="mb-4 text-sm text-farm-green-dark bg-farm-green-light/30 border border-farm-green/50 rounded-xl px-4 py-3">
            {{ signupSuccessMessage }}
          </p>

          <form class="flex flex-col gap-4" @submit.prevent="login">
            <label class="block">
              <span class="text-sm font-medium text-farm-brown-dark">이메일</span>
              <input
                v-model.trim="email"
                type="email"
                autocomplete="email"
                class="auth-input mt-2 w-full rounded-xl border border-farm-brown/20 bg-farm-paper px-4 py-3 text-farm-brown-dark placeholder:text-farm-brown/40 focus:border-farm-point focus:ring-2 focus:ring-farm-point/20 focus:outline-none"
                placeholder="example@email.com"
              />
            </label>

            <label class="block">
              <span class="text-sm font-medium text-farm-brown-dark">비밀번호</span>
              <input
                v-model="password"
                type="password"
                autocomplete="current-password"
                class="auth-input mt-2 w-full rounded-xl border border-farm-brown/20 bg-farm-paper px-4 py-3 text-farm-brown-dark placeholder:text-farm-brown/40 focus:border-farm-point focus:ring-2 focus:ring-farm-point/20 focus:outline-none"
                placeholder="비밀번호 입력"
              />
            </label>

            <p v-if="auth.errorMessage" class="text-sm text-farm-point">
              {{ auth.errorMessage }}
            </p>

            <button
              type="submit"
              class="auth-btn mt-1 w-full rounded-xl bg-farm-point text-farm-paper py-3 font-medium disabled:opacity-60 hover:bg-farm-point/90 active:scale-[0.99] transition-all"
              :disabled="auth.loading"
            >
              로그인
            </button>

            <p class="text-center text-sm text-farm-brown/70 mt-2">
              계정이 없으신가요?
              <button type="button" class="font-medium text-farm-point hover:underline ml-1" @click="isSignup = true">
                회원가입
              </button>
            </p>
          </form>
        </div>
      </div>

      <div class="overlay-container">
        <div class="overlay">
          <div class="overlay-panel overlay-left">
            <h2 class="text-2xl font-dnf text-farm-paper">환영합니다</h2>
            <p class="mt-3 text-sm text-farm-paper/90 leading-relaxed whitespace-nowrap">
              이미 계정이 있으신가요? 로그인하고 모험을 이어가세요.
            </p>
            <button class="auth-ghost-btn mt-8" type="button" @click="isSignup = false">
              로그인
            </button>
          </div>

          <div class="overlay-panel overlay-right">
            <h2 class="text-2xl font-dnf text-farm-paper">처음이신가요?</h2>
            <p class="mt-3 text-sm text-farm-paper/90 leading-relaxed whitespace-nowrap">
              몇 가지 정보만 입력하면 바로 시작할 수 있어요.
            </p>
            <button class="auth-ghost-btn mt-8" type="button" @click="isSignup = true">
              회원가입
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import SignupForm from '@/components/organisms/SignupForm.vue'

const props = defineProps({
  /** 라우트에서 기본 모드 지정용: 'login' | 'signup' */
  initialMode: { type: String, default: 'login' }
})

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')
const isSignup = ref(false)
const signupSuccessMessage = ref('')

watch(
  () => props.initialMode,
  (mode) => {
    isSignup.value = mode === 'signup'
    // 화면 진입 모드가 바뀌면, 이전 성공 메시지는 UX상 초기화
    signupSuccessMessage.value = ''
  },
  { immediate: true }
)

const login = async () => {
  try {
    await auth.login({ email: email.value, password: password.value })
    await nextTick()
    router.push('/')
  } catch (e) {
    // console.error(e)
  }
}

const onSignedUp = ({ email: signedUpEmail } = {}) => {
  signupSuccessMessage.value = '회원가입이 완료되었습니다. 로그인해 주세요.'
  if (signedUpEmail) email.value = signedUpEmail
  isSignup.value = false
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 4rem);
  min-height: calc(100dvh - 4rem);
  padding: 2rem 1rem;
  background: var(--color-farm-cream);
  position: relative;
}

.auth-shell {
  position: relative;
  width: min(960px, 100%);
  min-height: 540px;
  background: var(--color-farm-paper);
  border-radius: 28px;
  overflow: hidden;
  box-shadow:
    0 4px 6px -1px rgba(78, 59, 42, 0.06),
    0 10px 30px -8px rgba(78, 59, 42, 0.12),
    0 0 0 1px rgba(78, 59, 42, 0.04);
  transition: box-shadow 0.2s ease;
}

.form-container {
  position: absolute;
  top: 0;
  height: 100%;
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 40px;
  background: var(--color-farm-paper);
  backface-visibility: hidden;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.5s ease;
  overflow: hidden;
}

.sign-in-container {
  left: 0;
  z-index: 2;
  border-radius: 28px 0 0 28px;
}

.sign-up-container {
  left: 0;
  opacity: 0;
  z-index: 1;
  overflow-y: auto;
  align-items: flex-start;
  padding-top: 40px;
  padding-bottom: 40px;
  -webkit-overflow-scrolling: touch;
  border-radius: 28px 0 0 28px;
}

.auth-shell.right-panel-active .sign-in-container {
  transform: translateX(100%);
  opacity: 0;
  pointer-events: none;
}

.auth-shell.right-panel-active .sign-up-container {
  transform: translateX(100%);
  opacity: 1;
  z-index: 5;
  border-radius: 0 28px 28px 0;
}

.auth-shell:not(.right-panel-active) .sign-up-container {
  pointer-events: none;
}

.overlay-container {
  position: absolute;
  top: 0;
  left: 50%;
  width: 50%;
  height: 100%;
  overflow: hidden;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 10;
}

.auth-shell.right-panel-active .overlay-container {
  transform: translateX(-100%);
  border-radius: 28px 0 0 28px;
}

.overlay {
  position: relative;
  left: -100%;
  height: 100%;
  width: 200%;
  transform: translateX(0);
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
  background: linear-gradient(135deg, var(--color-farm-point) 0%, #d96a52 100%);
  border-radius: inherit;
}

.auth-shell.right-panel-active .overlay {
  transform: translateX(50%);
}

.overlay-panel {
  position: absolute;
  top: 0;
  height: 100%;
  width: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 0 48px;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.overlay-left {
  left: 0;
  transform: translateX(-20%);
}
.auth-shell.right-panel-active .overlay-left {
  transform: translateX(0);
}

.overlay-right {
  right: 0;
  transform: translateX(0);
}
.auth-shell.right-panel-active .overlay-right {
  transform: translateX(20%);
}

.auth-ghost-btn {
  border: 2px solid rgba(255, 253, 245, 0.6);
  background: rgba(255, 253, 245, 0.15);
  color: var(--color-farm-paper);
  padding: 12px 28px;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.95rem;
  transition: background 0.2s, border-color 0.2s, transform 0.15s;
}
.auth-ghost-btn:hover {
  background: rgba(255, 253, 245, 0.3);
  border-color: rgba(255, 253, 245, 0.8);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .auth-page {
    padding: 1rem 0.75rem;
    align-items: flex-start;
    padding-top: 1.5rem;
  }
  .auth-shell {
    min-height: unset;
    border-radius: 20px;
    box-shadow: 0 4px 20px rgba(78, 59, 42, 0.08);
  }
  .overlay-container {
    display: none;
  }
  .form-container {
    position: relative;
    width: 100%;
    transform: none !important;
    opacity: 1 !important;
    z-index: auto !important;
    padding: 28px 24px;
    border-radius: 20px !important;
  }
  .sign-up-container,
  .sign-in-container {
    display: none;
  }
  .auth-shell:not(.right-panel-active) .sign-in-container {
    display: flex;
  }
  .auth-shell.right-panel-active .sign-up-container {
    display: flex;
  }
}
</style>
