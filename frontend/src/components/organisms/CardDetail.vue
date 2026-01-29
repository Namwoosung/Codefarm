<template>
  <div
    :class="containerClass"
    :data-grade="gradeText"
    role="button"
    tabindex="0"
    @click="emit('showcard', props.card)"
    @keydown.enter.prevent="emit('showcard', props.card)"
    @keydown.space.prevent="emit('showcard', props.card)"
  >
    <img
      v-if="imageSrc"
      :src="imageSrc"
      :alt="nameText"
      loading="lazy"
      :class="imageClass"
    />
    <div
      v-else
      class="w-full h-full flex items-center justify-center bg-base-200 text-base-content/30 text-5xl font-extrabold"
      aria-hidden="true"
    >
      ?
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const emit = defineEmits(['showcard'])

const props = defineProps({
  card: {
    type: Object,
    required: true
  }
})

// API/화면에서 사용하는 키를 최대한 흡수
const imageSrc = computed(() => props.card?.image ?? props.card?.cardImage ?? props.card?.img)
const nameText = computed(() => props.card?.name ?? props.card?.cardName ?? 'Unknown')
const gradeText = computed(() => props.card?.grade ?? props.card?.cardGrade ?? '')

const isMega = computed(() => gradeText.value === 'MEGA')

// MEGA 카드(가로형): 제공 이미지 비율(1024/723)로 맞춤
const containerClass = computed(() => {
  const base =
    'card bg-transparent shadow-md rounded-xl overflow-hidden flex-shrink-0 transition-transform duration-200 hover:-translate-y-1 relative z-0 hover:z-10 will-change-transform'

  return isMega.value
    ? `${base} w-[320px] aspect-[1024/723]`
    : `${base} w-[140px] aspect-[1872/2613]`
})

const imageClass = computed(() => {
  // 가로형 MEGA는 전체가 잘리지 않게 contain 권장
  return isMega.value ? 'w-full h-full object-contain block' : 'w-full h-full object-cover block'
})
</script>

