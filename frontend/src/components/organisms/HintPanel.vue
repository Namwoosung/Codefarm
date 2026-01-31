<template>
  <div class="flex flex-col w-full h-full min-w-[280px] max-w-[320px] bg-[#FFE082] border-r border-base-300 flex-shrink-0">
    <div class="flex items-center px-4 py-3 border-b border-base-300 flex-shrink-0">
      <span class="text-sm font-semibold text-[#1a1a1a]">힌트</span>
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
          :key="idx"
          class="mb-2.5"
          :class="msg.role === 'user' ? 'text-right' : 'text-left'"
        >
          <span class="block text-[0.65rem] text-neutral-500 mb-0.5">{{ msg.role === 'user' ? '나' : '힌트' }}</span>
          <p class="inline-block px-2.5 py-1.5 rounded-md text-xs m-0 break-words max-w-full" :class="msg.role === 'user' ? 'bg-white/90 text-[#1a1a1a]' : 'bg-white/70 text-[#1a1a1a]'">
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
          placeholder="자... 힌트를"
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
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useIdeStore } from '@/stores/ide'
import * as hintApi from '@/api/hint'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'

const props = defineProps({
  hintRemaining: { type: Number, default: 3 },
  hintMax: { type: Number, default: 3 }
})
const emit = defineEmits(['hint-used'])

const route = useRoute()
const ideStore = useIdeStore()
const chatInput = ref('')
const chatMessages = ref([])
const hintLoading = ref(false)

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
    const d = res?.data
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
