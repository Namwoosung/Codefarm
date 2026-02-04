<template>
  <div 
    class="relative w-full overflow-visible" 
    ref="containerRef"
    :style="{ height: containerHeight + 'px' }"
  >
    <!-- 배경 이미지 레이어 -->
    <img 
      :src="backgroundImage" 
      class="absolute inset-0 w-full h-full object-contain pointer-events-none"
      decoding="async"
      fetchpriority="high"
      @load="onBgLoad"
    />
    
    <!-- 레벨 선택 영역들 -->
    <div
      v-for="level in levels"
      :key="level.id"
      class="absolute cursor-pointer flex items-center justify-center transition-all duration-300 z-10 hover:scale-110 active:scale-95 group"
      :style="level.style"
      @click="$emit('select-level', level.id)"
    >
      <div class="relative flex items-center justify-center w-14 h-9 pointer-events-auto">
        <!-- 배경 타원 (색상 #EAD7B5, 투명도 적용, 입체감 추가) -->
        <div class="absolute inset-0 bg-[#EAD7B5]/85 rounded-[100%] border-b-4 border-[#D7C4A3] shadow-lg group-hover:bg-[#EAD7B5] group-active:border-b-0 group-active:translate-y-0.5 transition-all"></div>
        
        <!-- 숫자 텍스트 -->
        <span class="relative font-dnf text-[#4E3B2A] text-xl drop-shadow-[0_1px_0_rgba(255,255,255,0.4)]">
          {{ level.id }}
        </span>
      </div>
    </div>
    <slot></slot>
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
@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
.animate-bounce-slow {
  animation: bounce-slow 3s infinite ease-in-out;
}
/* 핀 꼬리 색상 상속을 위한 설정 */
.border-t-inherit {
  border-top-color: inherit;
}
</style>
