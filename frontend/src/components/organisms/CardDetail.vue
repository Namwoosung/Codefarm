<template>
  <button
    type="button"
    :class="[baseContainerClass, isWideCard ? wideContainerClass : normalContainerClass]"
    :data-grade="view.grade"
    :aria-label="view.name"
    @click="emit('showcard', props.card)"
  >
    <img
      v-if="view.image"
      :src="view.image"
      :alt="view.name"
      loading="lazy"
      :class="['w-full h-full block', isWideCard ? 'object-contain' : 'object-cover']"
    />
    <div
      v-else
      class="w-full h-full flex items-center justify-center bg-base-200 text-base-content/30 text-5xl font-extrabold"
      aria-hidden="true"
    >
      ?
    </div>
  </button>
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

// 카드 상세 팝업에서 사용하는 카드 정보
const view = computed(() => {
  const card = props.card ?? {}
  return {
    image: card.image ?? card.cardImage ?? card.img ?? '',
    name: card.name ?? card.cardName ?? 'Unknown',
    grade: card.grade ?? card.cardGrade ?? '',
  }
})

// 서버 등급값 기준: SPECIAL(= MEGACREW)만 가로형 카드
const isWideCard = computed(() => view.value.grade === 'SPECIAL')

// 배열 바인딩
const baseContainerClass =
  'card bg-transparent shadow-md rounded-xl overflow-hidden flex-shrink-0 transition-transform duration-200 hover:-translate-y-1 relative z-0 hover:z-10 will-change-transform appearance-none border-0 p-0'
const wideContainerClass = 'w-[320px] aspect-[1024/723]'
const normalContainerClass = 'w-[140px] aspect-[1872/2613]'
</script>

