<template>
  <div
    ref="containerRef"
    class="roadmap-map relative w-full overflow-visible"
    :style="{ height: containerHeight + 'px' }"
  >
    <img
      :src="backgroundImage"
      class="absolute inset-0 w-full h-full object-contain pointer-events-none select-none"
      decoding="async"
      fetchpriority="high"
      @load="onBgLoad"
    />

    <!-- 레벨 선택 버튼 -->
    <button
      v-for="level in levels"
      :key="level.id"
      type="button"
      class="roadmap-level-btn absolute flex items-center justify-center z-10 focus:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/40 focus-visible:ring-offset-2 rounded-full"
      :style="level.style"
      :aria-label="`레벨 ${level.id} 선택`"
      @click="$emit('select-level', level.id)"
    >
      <div class="roadmap-level-pill">
        <span class="roadmap-level-num">{{ level.id }}</span>
      </div>
    </button>
    <slot />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  backgroundImage: { type: String, required: true },
  levels: {
    type: Array,
    default: () => [
      { id: 1, style: { top: '18%', left: '35%' } },
      { id: 2, style: { top: '31%', left: '46%' } },
      { id: 3, style: { top: '48%', left: '48%' } },
      { id: 4, style: { top: '65%', left: '47%' } },
      { id: 5, style: { top: '78%', left: '55%' } }
    ]
  }
})

const emit = defineEmits(['select-level', 'bg-loaded'])

const containerRef = ref(null)
// 초기 레이아웃 점프를 줄이기 위해 기본 비율로 먼저 높이를 잡고,
// 실제 이미지 로드 후 naturalWidth/Height로 정확한 비율로 보정한다.
const aspectRatio = ref(0.75) // height / width
const containerHeight = ref(0)
let resizeObserver = null

const updateHeight = (forcedWidth) => {
  if (!containerRef.value) return
  const width = typeof forcedWidth === 'number' ? forcedWidth : containerRef.value.offsetWidth
  if (width === 0) return
  containerHeight.value = Math.round(width * aspectRatio.value)
}

const onBgLoad = (e) => {
  const imgEl = e?.target
  const w = imgEl?.naturalWidth
  const h = imgEl?.naturalHeight
  if (typeof w === 'number' && typeof h === 'number' && w > 0 && h > 0) {
    aspectRatio.value = h / w
  }
  updateHeight()
  emit('bg-loaded')
}

onMounted(() => {
  // 1) 초기 높이 선계산 (레이아웃 점프 최소화)
  updateHeight()

  // 2) 컨테이너 폭 변화에만 반응 (window resize보다 정확하고 가벼움)
  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver((entries) => {
      const entry = entries?.[0]
      const w = entry?.contentRect?.width
      if (typeof w === 'number') updateHeight(w)
    })
    if (containerRef.value) resizeObserver.observe(containerRef.value)
  } else {
    window.addEventListener('resize', updateHeight)
  }
})

onUnmounted(() => {
  if (resizeObserver) {
    try {
      resizeObserver.disconnect()
    } catch (_) {
      // noop
    }
    resizeObserver = null
    return
  }
  window.removeEventListener('resize', updateHeight)
})
</script>

<style scoped>
.roadmap-level-btn {
  transition: transform 0.25s ease;
}
.roadmap-level-btn:hover {
  transform: scale(1.1);
}
.roadmap-level-btn:active {
  transform: scale(0.98);
}
.roadmap-level-pill {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 3.5rem;
  height: 3.5rem;
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 253, 245, 1), transparent 50%),
    radial-gradient(circle at 70% 70%, rgba(181, 217, 156, 0.4), transparent 60%),
    radial-gradient(circle at 50% 50%, rgba(255, 235, 180, 0.9), rgba(220, 235, 180, 0.7));
  border-radius: 50%;
  border: 2px solid rgba(123, 174, 95, 0.5);
  box-shadow:
    0 4px 14px rgba(94, 141, 72, 0.25),
    0 2px 4px rgba(78, 59, 42, 0.12),
    inset 0 2px 0 rgba(255, 255, 255, 0.7),
    inset 0 -1px 0 rgba(123, 174, 95, 0.2);
  transition: all 0.2s ease;
  pointer-events: auto;
}
.roadmap-level-btn:hover .roadmap-level-pill {
  background:
    radial-gradient(circle at 30% 30%, rgba(255, 253, 245, 1), transparent 50%),
    radial-gradient(circle at 70% 70%, rgba(181, 217, 156, 0.55), transparent 60%),
    radial-gradient(circle at 50% 50%, rgba(255, 240, 190, 0.95), rgba(200, 230, 170, 0.8));
  border-color: rgba(123, 174, 95, 0.75);
  box-shadow:
    0 6px 20px rgba(94, 141, 72, 0.35),
    0 3px 8px rgba(78, 59, 42, 0.15),
    inset 0 2px 0 rgba(255, 255, 255, 0.8);
}
.roadmap-level-btn:active .roadmap-level-pill {
  box-shadow:
    0 2px 8px rgba(94, 141, 72, 0.2),
    inset 0 2px 4px rgba(123, 174, 95, 0.15);
}

.roadmap-level-num {
  position: relative;
  font-family: var(--font-dnf);
  font-size: 1.4rem;
  color: #3d3228;
  text-shadow:
    0 1px 0 rgba(255, 255, 255, 0.8),
    0 1px 2px rgba(78, 59, 42, 0.15);
}
.roadmap-level-btn:hover .roadmap-level-num {
  color: #2e251d;
}
</style>
