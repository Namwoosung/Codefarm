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
      @load="updateHeight"
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

defineEmits(['select-level'])

const containerRef = ref(null)
const containerHeight = ref(0)

const updateHeight = () => {
  if (!containerRef.value) return
  const width = containerRef.value.offsetWidth
  if (width === 0) {
    setTimeout(updateHeight, 100)
    return
  }
  
  const img = new Image()
  img.src = props.backgroundImage
  img.onload = () => {
    containerHeight.value = width * (img.height / img.width)
  }
}

onMounted(() => {
  updateHeight()
  window.addEventListener('resize', updateHeight)
})

onUnmounted(() => {
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
