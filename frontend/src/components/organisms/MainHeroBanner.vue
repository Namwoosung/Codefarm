<template>
  <!-- 전체 폭 배너 (배경은 full-bleed) -->
  <section class="relative w-full bg-farm-olive px-20 py-3 md:py-4 overflow-hidden">
    <div class="relative">
      <transition name="banner-slide-up" mode="out-in">
        <div :key="currentSlide.key" class="min-h-[92px] md:min-h-[112px] flex flex-col justify-center">
          <!-- 인트로 슬라이드 -->
          <template v-if="currentSlide.type === 'intro'">
            <p v-if="currentSlide.kicker" class="text-xs font-bold tracking-[0.2em] text-farm-cream/80">
              {{ currentSlide.kicker }}
            </p>
            <h1 class="mt-1 text-2xl md:text-3xl font-bold text-farm-cream">
              {{ currentSlide.title }}
            </h1>
            <p v-if="currentSlide.description" class="mt-2 text-xs md:text-base text-farm-cream/90">
              {{ currentSlide.description }}
            </p>
          </template>

          <!-- 랭킹 슬라이드: rank.png 위로 텍스트 오버레이 -->
          <template v-else>
            <div class="flex items-center justify-between">
              <p class="text-xs font-bold tracking-[0.2em] text-white/80">RANKING</p>
              <span class="text-[11px] font-semibold text-white/80">TOP 3</span>
            </div>

            <div class="relative mt-2 flex justify-center">
              <img
                :src="rankImg"
                alt="rank"
                class="h-12 md:h-14 w-auto select-none pointer-events-none opacity-90 translate-y-2 md:translate-y-3"
                draggable="false"
              />

              <!-- 나무덩굴(이미지) 위에 텍스트 -->
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="-translate-y-[16px] md:-translate-y-[18px] text-center">
                  <div class="text-base md:text-lg font-extrabold text-white leading-tight drop-shadow-[0_0_10px_rgba(255,255,255,0.75)]">
                    {{ currentSlide.title }}
                  </div>
                  <div class="mt-0.5 text-xs md:text-sm font-semibold text-white/95 leading-tight drop-shadow-[0_0_10px_rgba(255,255,255,0.65)]">
                    {{ currentSlide.description }}
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
      </transition>
    </div>
  </section>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import rankImg from '@/assets/rank.png'

const props = defineProps({
  kicker: { type: String, default: 'CODE FARM' },
  title: { type: String, default: '이번주 카드 랭킹 TOP 3' },
  description: { type: String, default: '포인트를 모아 다음주 카드랭킹에 도전해보아요 !' },
  top3: { type: Array, default: () => [] },
  intervalMs: { type: Number, default: 2500 },
})

const currentIndex = ref(0)
let timer = null

const slides = computed(() => {
  const t3 = Array.isArray(props.top3) ? props.top3 : []
  const getNick = (idx) => t3[idx]?.nickname ?? '—'
  const getCount = (idx) => {
    const raw = t3[idx]?.totalCardCount ?? t3[idx]?.count ?? null
    const n = Number(raw)
    return Number.isFinite(n) ? n : null
  }

  return [
    {
      key: 'intro',
      type: 'intro',
      kicker: props.kicker,
      title: props.title,
      description: props.description,
    },
    {
      key: 'rank-1',
      type: 'rank',
      title: '1위',
      description: `${getNick(0)}${getCount(0) != null ? ` · ${getCount(0)}장` : ''}`,
    },
    {
      key: 'rank-2',
      type: 'rank',
      title: '2위',
      description: `${getNick(1)}${getCount(1) != null ? ` · ${getCount(1)}장` : ''}`,
    },
    {
      key: 'rank-3',
      type: 'rank',
      title: '3위',
      description: `${getNick(2)}${getCount(2) != null ? ` · ${getCount(2)}장` : ''}`,
    },
  ]
})

const currentSlide = computed(() => slides.value[currentIndex.value] ?? slides.value[0])

const start = () => {
  if (timer) clearInterval(timer)
  timer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % slides.value.length
  }, Math.max(800, Number(props.intervalMs) || 2500))
}

onMounted(() => start())
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
})

watch(
  () => (Array.isArray(props.top3) ? props.top3.map((u) => u?.userId ?? u?.nickname ?? '').join('|') : ''),
  () => {
    currentIndex.value = 0
  }
)
</script>

<style scoped>
.banner-slide-up-enter-active,
.banner-slide-up-leave-active {
  transition: transform 420ms ease, opacity 420ms ease;
}
.banner-slide-up-enter-from {
  transform: translateY(16px);
  opacity: 0;
}
.banner-slide-up-leave-to {
  transform: translateY(-16px);
  opacity: 0;
}
</style>

