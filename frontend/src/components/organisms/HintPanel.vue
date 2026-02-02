<template>
  <div class="flex flex-col w-full h-full min-w-[280px] max-w-[320px] bg-[#FFE082] border-r border-base-300 flex-shrink-0">
    <div class="flex items-center justify-between px-4 h-10 min-h-10 border-b border-base-300 flex-shrink-0">
      <span class="text-sm font-semibold text-[#1a1a1a]">힌트</span>
      <button
        type="button"
        class="btn btn-ghost btn-sm btn-square text-[var(--color-farm-brown-dark)] hover:bg-base-200/50"
        title="힌트 패널 접기"
        @click="$emit('close')"
      >
        <iconify-icon icon="mdi:chevron-left" class="text-lg"></iconify-icon>
      </button>
    </div>
    <div class="flex flex-col flex-1 min-h-0 p-3">
      <div class="flex-1 min-h-0 overflow-y-auto mb-3">
        <div class="flex items-start gap-2 mb-3 p-2.5 rounded-lg bg-white/70 shadow-sm">
          <div class="hint-avatar w-8 h-8 min-w-8 rounded-full bg-[#f5d54a] flex items-center justify-center flex-shrink-0">
            <CarrotIcon />
          </div>
          <p class="text-xs font-normal text-[#1a1a1a] leading-snug m-0">
            도움이 필요하신가요? 어떤 부분에서 어렵다고 느끼셨나요?
          </p>
        </div>
        <div
          v-for="(msg, idx) in chatMessages"
          :key="msg.hintId != null ? 'hint-' + msg.hintId : idx"
          class="mb-2.5"
          :class="msg.role === 'user' ? 'text-right' : 'text-left'"
        >
          <span class="block text-[0.65rem] text-neutral-500 mb-0.5">{{ msg.role === 'user' ? '나' : '힌트' }}</span>
          <!-- 자동 힌트 도착: 확인 전/볼게요/괜찮아요 -->
          <div
            v-if="msg.type === 'pending_auto_hint'"
            class="inline-block px-2.5 py-1.5 rounded-md text-xs max-w-full bg-white/70 text-[#1a1a1a]"
          >
            <template v-if="msg.dismissed">
              <span class="text-neutral-400 italic">힌트를 보지 않았어요</span>
            </template>
            <template v-else-if="msg.viewed">
              <p class="m-0 break-words">{{ msg.content }}</p>
            </template>
            <template v-else>
              <p class="m-0 flex items-center gap-1.5 mb-2">
                <iconify-icon icon="mdi:message-text-outline" class="text-[var(--color-farm-green)] shrink-0"></iconify-icon>
                <span>힌트가 도착했습니다. 확인하시겠습니까?</span>
              </p>
              <div class="flex gap-2 flex-wrap">
                <button
                  type="button"
                  class="btn btn-xs h-7 px-2 rounded-md bg-[var(--color-farm-green)] text-white border-none"
                  @click="viewPendingHint(idx)"
                >
                  볼게요
                </button>
                <button
                  type="button"
                  class="btn btn-xs h-7 px-2 rounded-md btn-ghost border border-base-300"
                  @click="dismissPendingHint(idx)"
                >
                  괜찮아요
                </button>
              </div>
            </template>
          </div>
          <p
            v-else
            class="inline-block px-2.5 py-1.5 rounded-md text-xs m-0 break-words max-w-full"
            :class="msg.role === 'user' ? 'bg-white/90 text-[#1a1a1a]' : 'bg-white/70 text-[#1a1a1a]'"
          >
            {{ msg.text }}
          </p>
        </div>
        <div v-if="hintLoading" class="mb-2.5 text-left">
          <span class="block text-[0.65rem] text-neutral-500 mb-0.5">힌트</span>
          <p class="inline-block px-2.5 py-1.5 rounded-md text-xs bg-white/70 text-[#1a1a1a] m-0">💡 힌트 생성 중...</p>
        </div>
      </div>
      <form class="flex flex-col gap-2 flex-shrink-0" @submit.prevent="sendHint">
        <input
          v-model="chatInput"
          type="text"
          class="input input-bordered input-sm w-full rounded-md bg-base-100 border-base-300 text-xs"
          placeholder="선생님께 당근을 흔들어 궁금한 걸 물어보세요!"
          :disabled="hintLoading || hintRemaining <= 0"
          @keydown.enter.exact.prevent="sendHint"
        />
        <div class="flex items-center justify-between">
          <span class="text-[0.7rem] text-neutral-500">당근 수: {{ hintRemaining }}/{{ hintMax }}</span>
          <button
            type="submit"
            class="btn btn-sm h-8 min-h-8 px-3 rounded-md bg-[var(--color-farm-green)] text-white border-none hover:bg-[var(--color-farm-green-dark)] disabled:opacity-50 disabled:cursor-not-allowed"
            :disabled="!chatInput.trim() || hintLoading || hintRemaining <= 0"
          >
            <iconify-icon icon="mdi:send" class="text-base"></iconify-icon>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { useIdeStore } from '@/stores/ide'
import * as hintApi from '@/api/hint'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'

const props = defineProps({
  hintRemaining: { type: Number, default: 3 },
  hintMax: { type: Number, default: 3 }
})
const emit = defineEmits(['hint-used', 'close', 'auto-hint-arrived', 'dismiss-hint-toast'])

const route = useRoute()
const ideStore = useIdeStore()
const chatInput = ref('')
const chatMessages = ref([])
const hintLoading = ref(false)
/** SSE 구독 해제 함수 */
let unsubscribeSSE = () => {}

/** 힌트 목록을 채팅 메시지 형태로 변환 (과거순) */
function hintsToMessages(hints) {
  const list = Array.isArray(hints) ? [...hints].reverse() : []
  const messages = []
  for (const h of list) {
    if (h.hintType === 'MANUAL' && h.userQuestion) {
      messages.push({ role: 'user', text: h.userQuestion, createdAt: h.createdAt, hintId: h.hintId })
    }
    messages.push({ role: 'assistant', text: h.content ?? '', createdAt: h.createdAt ?? '', hintId: h.hintId })
  }
  return messages
}

/** 힌트 목록 로드 후 채팅에 반영, 미열람 힌트는 열람 처리 */
async function loadHintList() {
  const sid = ideStore.sessionId
  if (sid == null) return
  try {
    const hints = await hintApi.getHintList(sid)
    chatMessages.value = hintsToMessages(hints)
    for (const h of hints) {
      if (h.hintId != null && h.isViewed === false) {
        hintApi.markHintViewed(sid, h.hintId).catch(() => {})
      }
    }
  } catch (_) {
    chatMessages.value = []
  }
}

/** SSE 자동 힌트 수신 시: 알림 + pending 말풍선 (볼게요/괜찮아요) */
function handleAutoHint(data) {
  if (!data?.content) return
  emit('auto-hint-arrived')
  chatMessages.value.push({
    role: 'assistant',
    type: 'pending_auto_hint',
    content: data.content,
    hintId: data.hintId,
    createdAt: data.createdAt ?? new Date().toISOString(),
    viewed: false,
    dismissed: false
  })
}

/** pending 자동 힌트 "볼게요" 클릭: 내용 표시 + 열람 처리 */
function viewPendingHint(idx) {
  const msg = chatMessages.value[idx]
  if (!msg || msg.type !== 'pending_auto_hint' || msg.viewed || msg.dismissed) return
  msg.viewed = true
  const sid = ideStore.sessionId
  if (sid != null && msg.hintId != null) {
    hintApi.markHintViewed(sid, msg.hintId).catch(() => {})
  }
}

/** pending 자동 힌트 "괜찮아요" 클릭: 비활성화 + 토스트 */
function dismissPendingHint(idx) {
  const msg = chatMessages.value[idx]
  if (!msg || msg.type !== 'pending_auto_hint' || msg.dismissed) return
  msg.dismissed = true
  emit('dismiss-hint-toast')
}

function startSSE() {
  const sid = ideStore.sessionId
  if (sid == null) return
  unsubscribeSSE()
  unsubscribeSSE = hintApi.subscribeHintSSE(sid, {
    onAutoHint: handleAutoHint
  })
}

function stopSSE() {
  unsubscribeSSE()
  unsubscribeSSE = () => {}
}

watch(
  () => ideStore.sessionId,
  (sid) => {
    if (sid != null) {
      loadHintList()
      startSSE()
    } else {
      chatMessages.value = []
      stopSSE()
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  stopSSE()
})

async function sendHint() {
  const q = chatInput.value?.trim()
  if (!q || hintLoading.value || props.hintRemaining <= 0) return
  chatMessages.value.push({ role: 'user', text: q, createdAt: new Date().toISOString() })
  chatInput.value = ''
  hintLoading.value = true
  try {
    const sid = ideStore.sessionId
    const code = ideStore.getCode(route.params.id)
    const res = await hintApi.requestManualHint(sid, { userQuestion: q, code })
    const d = res?.data ?? res
    if (d) {
      chatMessages.value.push({ role: 'assistant', text: d.content, createdAt: d.createdAt })
      emit('hint-used', { usedHint: d.usedHint ?? 0, maxHint: d.maxHint ?? 3 })
    } else {
      chatMessages.value.push({ role: 'assistant', text: '힌트를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', createdAt: new Date().toISOString() })
    }
  } catch (_) {
    chatMessages.value.push({ role: 'assistant', text: '힌트를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', createdAt: new Date().toISOString() })
  } finally {
    hintLoading.value = false
  }
}
</script>

<style scoped>
.hint-avatar :deep(svg) {
  width: 1rem;
  height: 1rem;
}
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}
.overflow-y-auto::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 2px;
}
</style>
