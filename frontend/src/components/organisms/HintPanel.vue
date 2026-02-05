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
                  @click="viewPendingHint(msg)"
                >
                  볼게요
                </button>
                <button
                  type="button"
                  class="btn btn-xs h-7 px-2 rounded-md btn-ghost border border-base-300"
                  @click="dismissPendingHint(msg)"
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
          :placeholder="hintRemaining <= 0 ? '힌트를 모두 사용했습니다' : '선생님께 당근을 흔들어 궁금한 걸 물어보세요!'"
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
import { ref, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useIdeStore } from '@/stores/ide'
import * as hintApi from '@/api/hint'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'

const props = defineProps({
  hintRemaining: { type: Number, default: 3 },
  hintMax: { type: Number, default: 3 }
})
const emit = defineEmits(['hint-used', 'hint-exhausted', 'close', 'dismiss-hint-toast'])

const route = useRoute()
const ideStore = useIdeStore()
const chatInput = ref('')
const hintLoading = ref(false)
/** API에서 로드한 힌트 목록 (MANUAL + AUTO) */
const apiHints = ref([])
/** 수동 힌트 전송 후 API 응답까지의 임시 메시지 (아직 apiHints에 없음) */
const optimisticMessages = ref([])

/** 힌트 목록을 채팅 메시지 형태로 변환 (시간순 유지를 위해 정렬하지 않음, 병합 후 일괄 정렬). AUTO는 세션 생성 이후 것만 표시 */
function hintsToMessages(hints) {
  const list = Array.isArray(hints) ? hints : []
  const sessionStart = ideStore.sessionStartedAt ?? 0
  const messages = []
  for (const h of list) {
    if (h.hintType === 'MANUAL') {
      if (h.userQuestion) {
        messages.push({ role: 'user', text: h.userQuestion, createdAt: h.createdAt, hintId: h.hintId })
      }
      messages.push({ role: 'assistant', text: h.content ?? '', createdAt: h.createdAt ?? '', hintId: h.hintId })
    } else if (h.hintType === 'AUTO') {
      const at = h.createdAt ? new Date(h.createdAt).getTime() : 0
      if (at >= sessionStart) {
        messages.push({ role: 'assistant', text: h.content ?? '', createdAt: h.createdAt ?? '', hintId: h.hintId })
      }
    }
  }
  return messages
}

/** store의 SSE 힌트를 pending 메시지 형태로 변환 (API에 아직 없는 것만) */
function storeHintsToMessages(storeHints, apiHintIds) {
  if (!Array.isArray(storeHints)) return []
  return storeHints
    .filter((h) => !apiHintIds.has(h.hintId ?? h.hint_id))
    .map((h) => ({
      role: 'assistant',
      type: 'pending_auto_hint',
      content: h.content ?? '',
      hintId: h.hintId ?? h.hint_id,
      createdAt: h.createdAt ?? '',
      viewed: h.viewed ?? false,
      dismissed: h.dismissed ?? false
    }))
}

/** 메시지 정렬용 타임스탬프 (createdAt 우선, 없으면 0) */
function msgTime(msg) {
  const t = msg?.createdAt
  return t ? new Date(t).getTime() : 0
}

/** API 힌트 + store SSE 힌트 + 수동 힌트 임시 메시지 병합 후 시간순 정렬 → 쓴 순서대로 채팅 */
const chatMessages = computed(() => {
  const apiMsgs = hintsToMessages(apiHints.value)
  const apiIds = new Set(apiHints.value.map((h) => h.hintId ?? h.hint_id))
  const storeMsgs = storeHintsToMessages(ideStore.hints ?? [], apiIds)
  const merged = [...apiMsgs, ...storeMsgs, ...optimisticMessages.value]
  return merged.slice().sort((a, b) => msgTime(a) - msgTime(b))
})

/** 힌트 목록 로드 후 apiHints에 반영, 미열람 힌트는 열람 처리 */
async function loadHintList() {
  const sid = ideStore.sessionId
  if (sid == null) return
  try {
    const hints = await hintApi.getHintList(sid)
    apiHints.value = hints ?? []
    for (const h of apiHints.value) {
      if (h.hintId != null && h.isViewed === false) {
        hintApi.markHintViewed(sid, h.hintId).catch(() => {})
      }
    }
  } catch (_) {
    apiHints.value = []
  }
}

/** pending 자동 힌트 "볼게요" 클릭: 내용 표시 + 열람 처리 (store 업데이트) */
function viewPendingHint(msg) {
  if (!msg || msg.type !== 'pending_auto_hint' || msg.viewed || msg.dismissed) return
  ideStore.updateHintState(msg.hintId, { viewed: true })
  const sid = ideStore.sessionId
  if (sid != null && msg.hintId != null) {
    hintApi.markHintViewed(sid, msg.hintId).catch(() => {})
  }
}

/** pending 자동 힌트 "괜찮아요" 클릭: 비활성화 + 토스트 (store 업데이트) */
function dismissPendingHint(msg) {
  if (!msg || msg.type !== 'pending_auto_hint' || msg.dismissed) return
  ideStore.updateHintState(msg.hintId, { dismissed: true })
  emit('dismiss-hint-toast')
}

watch(
  () => ideStore.sessionId,
  (sid) => {
    if (sid != null) {
      loadHintList()
      optimisticMessages.value = []
    } else {
      apiHints.value = []
      optimisticMessages.value = []
    }
  },
  { immediate: true }
)

async function sendHint() {
  if (props.hintRemaining <= 0) {
    emit('hint-exhausted')
    return
  }
  const q = chatInput.value?.trim()
  if (!q || hintLoading.value) return
  optimisticMessages.value = [...optimisticMessages.value, { role: 'user', text: q, createdAt: new Date().toISOString() }]
  chatInput.value = ''
  hintLoading.value = true
  try {
    const sid = ideStore.sessionId
    const code = ideStore.getCode(route.params.id)
    const res = await hintApi.requestManualHint(sid, { userQuestion: q, code })
    const d = res?.data ?? res
    if (d) {
      apiHints.value = [
        ...apiHints.value,
        {
          hintType: 'MANUAL',
          userQuestion: q,
          content: d.content ?? '',
          createdAt: d.createdAt ?? new Date().toISOString(),
          hintId: d.hintId,
          isViewed: true
        }
      ]
      optimisticMessages.value = optimisticMessages.value.filter((m) => m.role !== 'user' || m.text !== q)
      emit('hint-used', { usedHint: d.usedHint ?? 0, maxHint: d.maxHint ?? 3 })
    } else {
      optimisticMessages.value = [
        ...optimisticMessages.value,
        { role: 'assistant', text: '힌트를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', createdAt: new Date().toISOString() }
      ]
    }
  } catch (_) {
    optimisticMessages.value = [
      ...optimisticMessages.value,
      { role: 'assistant', text: '힌트를 불러오지 못했어요. 잠시 후 다시 시도해 주세요.', createdAt: new Date().toISOString() }
    ]
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
