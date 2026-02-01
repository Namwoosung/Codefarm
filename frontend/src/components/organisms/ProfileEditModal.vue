<template>
  <Teleport to="body">
    <div v-if="show" class="profile-edit-modal-overlay" @click.self="emit('close')">
      <div class="profile-edit-modal-card" role="dialog" aria-modal="true" aria-label="프로필 수정">
        <div class="profile-edit-modal-header">
          <h2 class="profile-edit-modal-title">프로필 수정</h2>
          <button type="button" class="profile-edit-modal-close" aria-label="닫기" @click="emit('close')">
            <iconify-icon icon="mdi:close"></iconify-icon>
          </button>
        </div>

        <form class="profile-edit-modal-body" @submit.prevent="submitIfCan">
          <label class="profile-edit-field">
            <span class="profile-edit-label">닉네임</span>
            <input
              v-model.trim="form.nickname"
              type="text"
              class="profile-edit-input"
              placeholder="닉네임"
              :disabled="isSaving"
              autocomplete="nickname"
              maxlength="30"
            />
          </label>

          <label class="profile-edit-field">
            <span class="profile-edit-label">이름</span>
            <input
              v-model.trim="form.name"
              type="text"
              class="profile-edit-input"
              placeholder="이름"
              :disabled="isSaving"
              autocomplete="name"
              maxlength="50"
            />
          </label>

          <div class="profile-edit-grid">
            <label class="profile-edit-field">
              <span class="profile-edit-label">나이</span>
              <input
                v-model="form.age"
                type="number"
                inputmode="numeric"
                class="profile-edit-input"
                placeholder="나이"
                :disabled="isSaving"
                min="0"
                max="150"
              />
            </label>

            <label class="profile-edit-field">
              <span class="profile-edit-label">코딩 레벨</span>
              <select v-model="form.codingLevel" class="profile-edit-input" :disabled="isSaving">
                <option v-for="lv in 5" :key="lv" :value="lv">LEVEL {{ lv }}</option>
              </select>
            </label>
          </div>

          <p v-if="errorMessage" class="profile-edit-error">{{ errorMessage }}</p>

          <div class="profile-edit-actions">
            <button type="button" class="profile-edit-btn profile-edit-btn-secondary" :disabled="isSaving" @click="emit('close')">
              취소
            </button>
            <button type="submit" class="profile-edit-btn profile-edit-btn-primary" :disabled="isSaving">
              {{ isSaving ? '저장 중...' : '저장' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { reactive, ref, watch, onUnmounted } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  user: { type: Object, default: null },
  isSaving: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'submit'])

const errorMessage = ref(null)
const form = reactive({
  age: '',
  name: '',
  codingLevel: 1,
  nickname: ''
})

function resetFromUser() {
  const u = props.user ?? {}
  form.nickname = u.nickname ?? ''
  form.name = u.name ?? ''
  form.age = u.age ?? ''
  const lv = Number(u.codingLevel)
  form.codingLevel = Number.isFinite(lv) && lv >= 1 && lv <= 5 ? lv : 1
}

function validate() {
  if (!form.nickname || !String(form.nickname).trim()) return '닉네임을 입력해주세요.'
  if (!form.name || !String(form.name).trim()) return '이름을 입력해주세요.'

  const ageNum = Number(form.age)
  if (!Number.isFinite(ageNum) || ageNum < 0 || ageNum > 150) return '나이는 0~150 사이의 숫자여야 합니다.'

  const lv = Number(form.codingLevel)
  if (!Number.isFinite(lv) || lv < 1 || lv > 5) return '코딩 레벨은 1~5 사이여야 합니다.'

  return null
}

function submitIfCan() {
  if (props.isSaving) return
  const msg = validate()
  if (msg) {
    errorMessage.value = msg
    return
  }

  errorMessage.value = null
  emit('submit', {
    age: Number(form.age),
    name: String(form.name).trim(),
    codingLevel: Number(form.codingLevel),
    nickname: String(form.nickname).trim()
  })
}

function onKeyDown(e) {
  if (e.key === 'Escape') emit('close')
}

watch(
  () => props.show,
  (v) => {
    if (v) {
      errorMessage.value = null
      resetFromUser()
      window.addEventListener('keydown', onKeyDown)
    } else {
      window.removeEventListener('keydown', onKeyDown)
    }
  }
)

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})
</script>

<style scoped>
.profile-edit-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.profile-edit-modal-card {
  background: var(--color-farm-paper, #fffdf5);
  border-radius: 1rem;
  width: 100%;
  max-width: 520px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.profile-edit-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--color-farm-cream);
}

.profile-edit-modal-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: var(--color-farm-green-dark, #5e8d48);
  margin: 0;
}

.profile-edit-modal-close {
  padding: 0.35rem;
  color: var(--color-farm-brown, #4e3b2a);
  background: none;
  border: none;
  cursor: pointer;
  border-radius: 0.5rem;
}
.profile-edit-modal-close:hover {
  background: var(--color-farm-cream);
  color: var(--color-farm-brown-dark, #2d2a26);
}

.profile-edit-modal-body {
  padding: 1rem 1.25rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.profile-edit-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.profile-edit-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-farm-brown, #4e3b2a);
}

.profile-edit-input {
  width: 100%;
  padding: 0.6rem 0.75rem;
  font-size: 0.95rem;
  border: 1px solid var(--color-farm-cream);
  border-radius: 0.75rem;
  background: #fff;
  color: var(--color-farm-brown-dark, #2d2a26);
}
.profile-edit-input:focus {
  outline: none;
  border-color: var(--color-farm-green, #5e8d48);
}
.profile-edit-input:disabled {
  background: var(--color-farm-cream);
  cursor: not-allowed;
}

.profile-edit-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
@media (max-width: 520px) {
  .profile-edit-grid {
    grid-template-columns: 1fr;
  }
}

.profile-edit-error {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  color: #c0392b;
}

.profile-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.profile-edit-btn {
  padding: 0.65rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
}
.profile-edit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-edit-btn-secondary {
  background: #fff;
  color: var(--color-farm-brown-dark, #2d2a26);
  border: 1px solid #e0e0e0;
}
.profile-edit-btn-secondary:hover:not(:disabled) {
  background: #fafafa;
  border-color: var(--color-farm-green, #5e8d48);
}

.profile-edit-btn-primary {
  background: var(--color-farm-green, #5e8d48);
  color: #fff;
}
.profile-edit-btn-primary:hover:not(:disabled) {
  background: var(--color-farm-green-dark, #4a7340);
}
</style>
