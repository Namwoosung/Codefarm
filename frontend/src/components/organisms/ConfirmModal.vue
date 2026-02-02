<template>
  <Teleport to="body">
    <div v-if="show" class="modal modal-open">
      <div class="modal-box max-w-md">
        <h3 v-if="title" class="text-lg font-black text-farm-brown-dark">
          {{ title }}
        </h3>

        <div class="mt-3">
          <div role="alert" :class="['alert', variantClass, 'alert-soft']">
            <svg v-if="variant === 'warning'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <svg v-else-if="variant === 'error'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="variant === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="h-6 w-6 shrink-0 stroke-current">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <span class="text-sm font-semibold whitespace-pre-wrap">{{ message }}</span>
          </div>
        </div>

        <div class="modal-action">
          <button type="button" class="btn" @click="emitCancel">
            {{ cancelText }}
          </button>
          <button
            type="button"
            class="btn bg-[#6B6B3A] text-farm-paper border-none hover:brightness-110 active:brightness-95"
            :disabled="confirmDisabled"
            @click="emitConfirm"
          >
            {{ confirmText }}
          </button>
        </div>
      </div>

      <div class="modal-backdrop" @click="emitCancel">
        <button aria-label="닫기">close</button>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, onUnmounted, watch } from 'vue'

const props = defineProps({
  show: { type: Boolean, default: false },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  variant: { type: String, default: 'warning' }, // 'info' | 'success' | 'warning' | 'error'
  confirmText: { type: String, default: '확인' },
  cancelText: { type: String, default: '취소' },
  confirmDisabled: { type: Boolean, default: false }
})

const emit = defineEmits(['confirm', 'cancel'])

const variantClass = computed(() => {
  if (props.variant === 'success') return 'alert-success'
  if (props.variant === 'error') return 'alert-error'
  if (props.variant === 'info') return 'alert-info'
  return 'alert-warning'
})

function emitCancel() {
  emit('cancel')
}
function emitConfirm() {
  emit('confirm')
}

function onKeyDown(e) {
  if (e.key === 'Escape') emitCancel()
}

watch(
  () => props.show,
  (v) => {
    if (v) window.addEventListener('keydown', onKeyDown)
    else window.removeEventListener('keydown', onKeyDown)
  }
)

onUnmounted(() => {
  window.removeEventListener('keydown', onKeyDown)
})
</script>
