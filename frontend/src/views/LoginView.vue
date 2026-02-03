<template>
  <div class="auth-page m-0">
    <div v-if="auth.loading" class="fixed inset-0 flex items-center justify-center z-40">
      <p class="text-sm font-medium text-gray-700 bg-white/90 px-4 py-2 rounded-lg shadow">
        슉. 슈슉...
      </p>
    </div>

    <div class="auth-shell" :class="{ 'right-panel-active': isSignup }">
      <!-- 회원가입 -->
      <div class="form-container sign-up-container">
        <div class="w-full max-w-md">
          <h1 class="text-2xl font-dnf">회원가입</h1>
          <p class="text-sm text-gray-600 mb-6">
            <button
              type="button"
              class="ml-2 text-farm-olive hover:brightness-110 font-medium md:hidden"
              @click="isSignup = false"
            >
              로그인으로
            </button>
          </p>

          <SignupForm embedded @signed-up="onSignedUp" />
        </div>
      </div>

      <!-- 로그인 -->
      <div class="form-container sign-in-container">
        <div class="w-full max-w-sm">
          <h1 class="text-2xl font-dnf mb-2">로그인</h1>
          <p class="text-sm text-gray-600 mb-6">
            <button
              type="button"
              class="ml-2 text-farm-olive hover:brightness-110 font-medium md:hidden"
              @click="isSignup = true"
            >
              회원가입으로
            </button>
          </p>

          <p v-if="signupSuccessMessage" class="mb-3 text-sm text-green-700 bg-green-50 border border-green-200 rounded-lg px-3 py-2">
            {{ signupSuccessMessage }}
          </p>

          <form class="flex flex-col gap-3" @submit.prevent="login">
            <label class="text-sm font-medium text-gray-700">
              Email
              <input
                v-model.trim="email"
                type="email"
                autocomplete="email"
                class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="이메일을 입력해주세요."
              />
            </label>

            <label class="text-sm font-medium text-gray-700">
              Password
              <input
                v-model="password"
                type="password"
                autocomplete="current-password"
                class="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
                placeholder="비밀번호를 입력해주세요."
              />
            </label>

            <p v-if="auth.errorMessage" class="text-sm text-red-600">
              {{ auth.errorMessage }}
            </p>

            <button
              type="submit"
              class="mt-2 w-full rounded-lg bg-farm-point text-farm-paper py-2 disabled:opacity-60 hover:brightness-110 active:brightness-95"
              :disabled="auth.loading"
            >
              로그인
            </button>

            <p class="text-center text-sm text-gray-600 mt-3">
              계정이 없으신가요?
              <button type="button" class="font-medium text-farm-point hover:brightness-110 ml-1" @click="isSignup = true">
                회원가입
              </button>
            </p>
          </form>
        </div>
      </div>

      <div class="overlay-container">
        <div class="overlay">
          <div class="overlay-panel overlay-left">
            <h2 class="text-3xl font-bold text-farm-paper">환영합니다</h2>
            <p class="mt-3 text-sm text-farm-paper/90 max-w-sm">
              이미 계정이 있으신가요? 로그인하고 계속 진행하세요.
            </p>
            <button class="ghost-btn mt-6" type="button" @click="isSignup = false">
              로그인
            </button>
          </div>

          <div class="overlay-panel overlay-right">
            <h2 class="text-3xl font-dnf text-farm-paper">처음이신가요?</h2>
            <p class="mt-3 text-sm text-farm-paper/90 max-w-sm">
              몇 가지 정보만 입력하면 바로 시작할 수 있어요.
            </p>
            <button class="ghost-btn mt-6" type="button" @click="isSignup = true">
              회원가입
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
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

onMounted(() => {
  isSignup.value = props.initialMode === 'signup'
})

const login = async () => {
  try {
    await auth.login({ email: email.value, password: password.value })
    router.push('/')
  } catch (e) {
    console.error(e)
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
  margin: 0;
  padding: 0;
  /* 높이 */
  min-height: calc(100vh - 4rem);
  background: var(--color-farm-cream);
  position: relative;
  z-index: 0;
}

.auth-shell {
  position: relative;
  width: min(980px, 100%);
  min-height: 600px;
  background: #fff;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(17, 24, 39, 0.15);
  z-index: 0;
  transform: translateY(-10px);
}

.form-container {
  position: absolute;
  top: 0;
  height: 100%;
  width: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: #fff;
  backface-visibility: hidden;
  transition: transform 0.6s ease-in-out, opacity 0.6s ease-in-out;
  /* 바깥 라운드( auth-shell )에 맞춰 내부도 클립 */
  overflow: hidden;
}

.sign-in-container {
  left: 0;
  z-index: 2;
  border-radius: 24px 0 0 24px;
}

.sign-up-container {
  left: 0;
  opacity: 0;
  z-index: 1;
  overflow-y: auto;
  align-items: flex-start;
  padding-top: 32px;
  padding-bottom: 32px;
  -webkit-overflow-scrolling: touch;
  border-radius: 24px 0 0 24px;
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
  border-radius: 0 24px 24px 0;
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
  transition: transform 0.6s ease-in-out;
  /* 헤더(z-50)보다 낮게 */
  z-index: 10;
}

.auth-shell.right-panel-active .overlay-container {
  transform: translateX(-100%);
  border-radius: 24px 0 0 24px;
}

.overlay {
  position: relative;
  left: -100%;
  height: 100%;
  width: 200%;
  transform: translateX(0);
  transition: transform 0.6s ease-in-out;
  background: var(--color-farm-point);
  color: #fff;
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
  padding: 0 56px;
  transition: transform 0.6s ease-in-out;
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

.ghost-btn {
  border: none;
  background: rgba(245, 242, 232, 0.5);
  color: var(--color-farm-brown-dark);
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 600;
  letter-spacing: 0.2px;
}
.ghost-btn:hover {
  background: rgba(245, 242, 232, 0.7);
}

@media (max-width: 768px) {
  .auth-shell {
    min-height: unset;
    transform: none;
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
    padding: 24px;
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
