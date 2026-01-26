<template>
  <div class="min-h-screen flex items-center justify-center p-6">
    <div
      v-if="auth.loading"
      class="fixed inset-0 flex items-center justify-center"
    >
      <p class="text-sm font-medium text-gray-700 bg-white/90 px-4 py-2 rounded-lg shadow">
        슉. 슈슉...
      </p>
    </div>

    <div class="w-full max-w-sm bg-white rounded-2xl shadow p-6">
      <h1 class="text-xl font-bold mb-6">로그인</h1>

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
          class="mt-2 w-full rounded-lg bg-black text-white py-2 disabled:opacity-60"
          :disabled="auth.loading"
        >
          로그인
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const email = ref('')
const password = ref('')

const login = async () => {
  try {
    await auth.login({ email: email.value, password: password.value })
    router.push('/')
  } catch (e) {
    // 에러 메시지는 auth.errorMessage로 표시됨
  }
}
</script>
