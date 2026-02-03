<template>
  <div
    ref="cardEl"
    class="hover-3d cursor-pointer flex-shrink-0"
    :class="[isWideCard ? wideContainerClass : normalContainerClass]"
    role="button"
    tabindex="0"
    :data-grade="view.grade"
    :aria-label="view.name"
    :style="pointerTransformStyle"
    @click="emit('showcard', props.card)"
    @keydown.enter.prevent="emit('showcard', props.card)"
    @keydown.space.prevent="emit('showcard', props.card)"
    @pointerdown="onPointerDown"
    @pointermove="onPointerMove"
    @pointerup="onPointerUp"
    @pointerleave="onPointerUp"
  >
    <figure class="w-full h-full rounded-xl overflow-hidden relative block m-0">
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
    </figure>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const emit = defineEmits(['showcard'])

const props = defineProps({
  card: {
    type: Object,
    required: true
  }
})

const cardEl = ref(null)
const pointerActive = ref(false)
const pointerTransform = ref({ x: 0, y: 0 })

function getPointerPosition(e) {
  const el = cardEl.value
  if (!el) return null
  const rect = el.getBoundingClientRect()
  const clientX = e.clientX ?? e.touches?.[0]?.clientX
  const clientY = e.clientY ?? e.touches?.[0]?.clientY
  if (clientX == null || clientY == null) return null
  const normX = (clientX - rect.left) / rect.width
  const normY = (clientY - rect.top) / rect.height
  const x = Math.max(-1, Math.min(1, (normX - 0.5) * 2))
  const y = Math.max(-1, Math.min(1, (0.5 - normY) * 2))
  return { x, y }
}

function onPointerDown(e) {
  pointerActive.value = true
  const pos = getPointerPosition(e)
  if (pos) pointerTransform.value = pos
}

function onPointerMove(e) {
  if (!pointerActive.value) return
  const pos = getPointerPosition(e)
  if (pos) pointerTransform.value = pos
}

function onPointerUp() {
  pointerActive.value = false
  pointerTransform.value = { x: 0, y: 0 }
}

const pointerTransformStyle = computed(() => {
  if (!pointerActive.value) return {}
  const { x, y } = pointerTransform.value
  return {
    '--transform': `${x}, ${y}`,
    '--shine': `${(x + 1) * 50}% ${(y + 1) * 50}%`,
    '--shadow': `${x * 0.5}rem ${y * 0.5}rem`,
  }
})

// 백엔드가 카드 이미지를 .svg로 주는 경우 .png로 변환
const toCardImageUrl = (url) => {
  if (typeof url !== 'string' || !url) return ''
  return url.replace(/\.svg$/i, '.png')
}

// 카드 상세 팝업에서 사용하는 카드 정보
const view = computed(() => {
  const card = props.card ?? {}
  const rawImage = card.image ?? card.cardImage ?? card.img ?? ''
  return {
    image: toCardImageUrl(rawImage),
    name: card.name ?? card.cardName ?? 'Unknown',
    grade: card.grade ?? card.cardGrade ?? '',
  }
})

// 서버 등급값 기준: SPECIAL(= MEGACREW)만 가로형 카드
const isWideCard = computed(() => view.value.grade === 'SPECIAL')

const wideContainerClass = 'w-[320px] aspect-[1024/723]'
const normalContainerClass = 'w-[140px] aspect-[1872/2613]'
</script>

