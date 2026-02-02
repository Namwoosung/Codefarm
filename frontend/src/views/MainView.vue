<template>
  <div class="min-h-screen p-10">
    <!-- 30분 무입력 강제 종료 후 메인 진입 시 안내 모달 (X로 닫기) -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showIdleCancelModal" class="fixed inset-0 flex items-center justify-center bg-black/40 z-[9999]">
          <div class="card bg-base-100 shadow-2xl rounded-xl p-6 min-w-[320px] max-w-[90vw] border border-base-300 relative">
            <button
              type="button"
              class="btn btn-ghost btn-sm btn-square absolute top-3 right-3 text-[var(--color-farm-brown)]"
              aria-label="닫기"
              @click="closeIdleCancelModal"
            >
              <iconify-icon icon="mdi:close" class="text-xl"></iconify-icon>
            </button>
            <p class="text-lg font-semibold text-[var(--color-farm-brown-dark)] pr-8">문제를 장시간동안 풀지 않아 자동으로 문제풀기가 취소되었습니다.</p>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 풀고 있는 문제가 있을 때 다른 문제 클릭 시 확인 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showActiveSessionModal && activeSessionPayload" class="fixed inset-0 flex items-center justify-center bg-black/40 z-[9999]">
          <div class="card bg-base-100 shadow-2xl rounded-xl p-6 min-w-[320px] max-w-[90vw] border border-base-300">
            <p class="text-lg font-semibold text-[var(--color-farm-brown-dark)] mb-4">
              풀고 있는 문제가 있습니다. (현재 {{ activeSessionPayload.otherProblemId }}번 문제)
            </p>
            <div class="flex justify-end gap-3">
              <button
                type="button"
                class="btn btn-sm btn-ghost border border-base-300"
                @click="goToExistingProblem"
              >
                기존 문제로
              </button>
              <button
                type="button"
                class="btn btn-sm bg-[var(--color-farm-green)] text-white border-none hover:bg-[var(--color-farm-green-dark)]"
                :disabled="activeSessionLoading"
                @click="goToNewProblem"
              >
                {{ activeSessionLoading ? '처리 중...' : '이 문제로 풀기' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-farm-brown-dark mb-2">CODE FARM 문제 목록</h1>
        <p class="text-farm-brown">
          문제를 선택하면 IDE 화면으로 이동해 풀 수 있어요.
        </p>
      </div>

      <!-- 로딩 / 에러 -->
      <div v-if="loading" class="text-center py-12 text-farm-brown">문제 목록을 불러오는 중...</div>
      <div v-else-if="error" class="text-center py-12 text-red-600">{{ error }}</div>

      <!-- 문제 카드 리스트 -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="problem in problems"
          :key="problem.problemId ?? problem.id"
          role="button"
          tabindex="0"
          class="block bg-farm-paper border-4 border-farm-brown rounded-2xl p-6 hover:shadow-lg transition-shadow cursor-pointer"
          @click="onClickProblem(problem)"
          @keydown.enter="onClickProblem(problem)"
        >
          <div class="mb-3 flex items-center justify-between text-sm text-farm-brown-dark">
            <span class="inline-flex items-center gap-1">
              <span class="px-3 py-1 bg-farm-cream rounded-full text-xs font-semibold">
                Lv.{{ problem.difficulty }}
              </span>
              <span class="font-medium">#{{ problem.algorithm }}</span>
            </span>
            <span class="text-xs text-farm-brown/70">ID: {{ problem.problemId ?? problem.id }}</span>
          </div>
          <h2 class="text-xl font-bold text-farm-brown-dark">
            {{ problem.title }}
          </h2>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProblemList } from '@/api/problem'
import * as sessionApi from '@/api/session'

const route = useRoute()
const router = useRouter()
const problems = ref([])
const loading = ref(true)
const error = ref(null)

const showIdleCancelModal = computed(() => route.query.idle_cancel === '1')

/** 풀고 있는 문제가 있을 때 다른 문제 클릭 시 모달 */
const showActiveSessionModal = ref(false)
/** { otherSessionId, otherProblemId, targetProblemId } */
const activeSessionPayload = ref(null)
const activeSessionLoading = ref(false)

function closeIdleCancelModal() {
  router.replace({ path: '/', query: {} })
}

async function onClickProblem(problem) {
  const problemId = Number(problem.problemId ?? problem.id)
  if (!problemId) return
  try {
    const { data: res } = await sessionApi.getActiveSession()
    const session = res?.data
    if (session && session.problemId !== problemId) {
      activeSessionPayload.value = {
        otherSessionId: session.sessionId,
        otherProblemId: session.problemId,
        targetProblemId: problemId,
      }
      showActiveSessionModal.value = true
      return
    }
  } catch (_) {
    // 404 등 = 활성 세션 없음 → 그대로 이동
  }
  router.push(`/ide/${problemId}`)
}

function goToExistingProblem() {
  const payload = activeSessionPayload.value
  if (!payload) return
  showActiveSessionModal.value = false
  activeSessionPayload.value = null
  router.push(`/ide/${payload.otherProblemId}`)
}

async function goToNewProblem() {
  const payload = activeSessionPayload.value
  if (!payload || activeSessionLoading.value) return
  activeSessionLoading.value = true
  try {
    await sessionApi.closeSession(payload.otherSessionId)
  } catch (_) {}
  showActiveSessionModal.value = false
  activeSessionPayload.value = null
  activeSessionLoading.value = false
  router.push(`/ide/${payload.targetProblemId}`)
}

onMounted(async () => {
  try {
    loading.value = true
    error.value = null
    const { data } = await getProblemList()
    problems.value = data ?? []
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '문제 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
})
</script>
