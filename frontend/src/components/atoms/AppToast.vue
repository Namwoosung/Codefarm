<script setup>
import { storeToRefs } from 'pinia'
import { useToastStore } from '@/stores/toast'

const toastStore = useToastStore()
const { message } = storeToRefs(toastStore)
</script>

<template>
  <Teleport to="body">
    <Transition name="toast">
      <div v-if="message" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[9999] w-[min(520px,calc(100vw-2rem))]">
        <div
          role="alert"
          class="flex items-center gap-3 rounded-2xl px-4 py-3 shadow-lg border border-farm-brown/20 bg-[var(--color-farm-paper)] text-[var(--color-farm-point)]"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="h-6 w-6 shrink-0 stroke-current">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <span class="text-sm font-semibold">{{ message }}</span>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.toast-enter-active {
  transition: opacity 180ms ease-out, transform 220ms ease-out;
  will-change: opacity, transform;
}
.toast-leave-active {
  transition: opacity 360ms ease-in, transform 360ms ease-in;
  will-change: opacity, transform;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  --tw-translate-y: 0.75rem;
}
.toast-enter-to,
.toast-leave-from {
  opacity: 1;
  --tw-translate-y: 0px;
}
</style>

