<template>
  <Teleport to="body">
    <div v-if="show" class="hint-modal-overlay" @click.self="$emit('close')">
      <div class="hint-modal-card">
        <div class="hint-modal-header">
          <h2 class="hint-modal-title">🥕 힌트 ({{ remaining }}/{{ maxHint }})</h2>
          <button type="button" class="hint-modal-close" aria-label="닫기" @click="$emit('close')">
            <iconify-icon icon="mdi:close"></iconify-icon>
          </button>
        </div>

        <!-- 채팅 메시지 목록 -->
        <div ref="messagesEl" class="hint-modal-messages">
          <div
            v-for="(msg, idx) in messages"
            :key="idx"
            class="hint-modal-msg"
            :class="msg.role === 'user' ? 'hint-modal-msg-user' : 'hint-modal-msg-assistant'"
          >
            <span class="hint-modal-msg-label">{{ msg.role === 'user' ? '나' : '힌트' }}</span>
            <p class="hint-modal-msg-text">{{ msg.text }}</p>
            <span v-if="msg.createdAt" class="hint-modal-msg-time">{{ formatTime(msg.createdAt) }}</span>
          </div>
          <div v-if="loading" class="hint-modal-msg hint-modal-msg-assistant hint-modal-msg-loading">
            <span class="hint-modal-msg-label">힌트</span>
            <p class="hint-modal-msg-text">💡 힌트 생성 중...</p>
          </div>
          <p v-if="messages.length === 0 && !loading" class="hint-modal-empty">질문을 입력하면 힌트를 받을 수 있어요.</p>
        </div>

        <!-- 질문 입력창 (form으로 전송 처리) -->
        <form class="hint-modal-footer" @submit.prevent="sendIfCan">
          <input
            v-model="inputQuestion"
            type="text"
            class="hint-modal-input"
            placeholder="질문을 입력하세요..."
            :disabled="loading || remaining <= 0"
            autocomplete="off"
          />
          <button
            type="submit"
            class="hint-modal-send"
            :disabled="loading || remaining <= 0 || !inputQuestion.trim()"
            :title="remaining <= 0 ? '힌트를 모두 사용했습니다' : '전송'"
          >
            <iconify-icon icon="mdi:send"></iconify-icon>
          </button>
        </form>
        <p v-if="remaining <= 0" class="hint-modal-exhausted">힌트를 모두 사용했습니다.</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  messages: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  usedHint: { type: Number, default: 0 },
  maxHint: { type: Number, default: 3 }
})
const emit = defineEmits(['close', 'send'])

const remaining = computed(() => Math.max(0, props.maxHint - props.usedHint))
const inputQuestion = ref('')
const messagesEl = ref(null)

watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
    })
  }
)

function formatTime(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function sendIfCan() {
  const q = inputQuestion.value?.trim()
  if (!q || props.loading || remaining.value <= 0) return
  emit('send', q)
  inputQuestion.value = ''
}
</script>

<style scoped>
.hint-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.hint-modal-card {
  background: var(--color-farm-paper, #fffdf5);
  border-radius: 1rem;
  padding: 0;
  max-width: 480px;
  width: 100%;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
}

.hint-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-farm-cream);
}

.hint-modal-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-farm-green-dark, #5e8d48);
  margin: 0;
}

.hint-modal-close {
  padding: 0.35rem;
  color: var(--color-farm-brown);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 0.5rem;
}
.hint-modal-close:hover {
  background: var(--color-farm-cream);
  color: var(--color-farm-brown-dark);
}

.hint-modal-messages {
  flex: 1;
  min-height: 200px;
  max-height: 360px;
  overflow-y: auto;
  padding: 1rem 1.25rem;
}

.hint-modal-msg {
  margin-bottom: 1rem;
  max-width: 90%;
}
.hint-modal-msg-user {
  margin-left: auto;
  text-align: right;
}
.hint-modal-msg-assistant {
  margin-right: auto;
  text-align: left;
}

.hint-modal-msg-label {
  font-size: 0.75rem;
  color: var(--color-farm-brown);
  display: block;
  margin-bottom: 0.25rem;
}

.hint-modal-msg-user .hint-modal-msg-text {
  display: inline-block;
  padding: 0.5rem 0.75rem;
  background: var(--color-farm-green-light);
  color: var(--color-farm-brown-dark);
  border-radius: 0.75rem;
  font-size: 0.9rem;
  margin: 0;
  text-align: left;
}
.hint-modal-msg-assistant .hint-modal-msg-text {
  display: inline-block;
  padding: 0.5rem 0.75rem;
  background: var(--color-farm-cream);
  color: var(--color-farm-brown-dark);
  border-radius: 0.75rem;
  font-size: 0.9rem;
  margin: 0;
  text-align: left;
}

.hint-modal-msg-loading .hint-modal-msg-text {
  color: var(--color-farm-brown);
}

.hint-modal-msg-time {
  font-size: 0.7rem;
  color: var(--color-farm-brown);
  display: block;
  margin-top: 0.2rem;
}

.hint-modal-empty {
  font-size: 0.9rem;
  color: var(--color-farm-brown);
  text-align: center;
  margin: 2rem 0 0;
}

.hint-modal-footer {
  display: flex;
  gap: 0.5rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--color-farm-cream);
}

.hint-modal-input {
  flex: 1;
  padding: 0.6rem 0.75rem;
  font-size: 0.9rem;
  border: 1px solid var(--color-farm-cream);
  border-radius: 0.75rem;
  background: #fff;
  color: var(--color-farm-brown-dark);
}
.hint-modal-input:focus {
  outline: none;
  border-color: var(--color-farm-green);
}
.hint-modal-input:disabled {
  background: var(--color-farm-cream);
  cursor: not-allowed;
}

.hint-modal-send {
  padding: 0.6rem 0.9rem;
  background: var(--color-farm-green);
  color: #fff;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
}
.hint-modal-send:hover:not(:disabled) {
  background: var(--color-farm-green-dark);
}
.hint-modal-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint-modal-exhausted {
  font-size: 0.8rem;
  color: var(--color-farm-brown);
  padding: 0 1.25rem 1rem;
  margin: 0;
}
</style>
