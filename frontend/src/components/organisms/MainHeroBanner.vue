<template>
  <section class="ranking-banner relative w-full overflow-hidden h-[120px] md:h-[140px] flex items-center justify-center px-4 sm:px-8 md:px-12 lg:px-16">
    <div class="absolute inset-0 opacity-20 pointer-events-none">
      <div class="absolute top-0 left-0 w-32 h-32 bg-farm-yellow/30 rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 right-0 w-40 h-40 bg-farm-green/30 rounded-full blur-3xl"></div>
    </div>
    
    <!-- 패턴 오버레이 -->
    <div class="absolute inset-0 opacity-10 pointer-events-none" style="background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.1) 10px, rgba(255,255,255,0.1) 20px);"></div>
    
    <div class="relative z-10 w-full h-full flex items-center">
      <transition name="banner-slide-up" mode="out-in">
        <div :key="currentSlide.key" class="w-full max-w-5xl h-full flex flex-col justify-center mx-auto">
          <template v-if="currentSlide.type === 'intro'">
            <div class="flex items-center gap-2 mb-1">
              <iconify-icon icon="mdi:trophy" class="text-farm-yellow text-lg shrink-0"></iconify-icon>
              <p v-if="currentSlide.kicker" class="text-xs font-bold tracking-[0.2em] text-farm-cream/85">
                {{ currentSlide.kicker }}
              </p>
            </div>
            <h1 class="text-xl md:text-2xl font-dnf text-farm-cream font-bold drop-shadow-lg leading-tight">
              {{ currentSlide.title }}
            </h1>
            <p v-if="currentSlide.description" class="mt-2 text-xs md:text-sm text-farm-cream/90 flex items-center gap-2">
              <iconify-icon icon="mdi:cards" class="text-farm-yellow/80 shrink-0"></iconify-icon>
              {{ currentSlide.description }}
            </p>
          </template>

          <!-- 랭킹 슬라이드 -->
          <template v-else>
            <div class="flex items-center justify-between gap-4 sm:gap-6 w-full">
              <!-- 좌측: RANKING -->
              <div class="flex flex-col items-start justify-center shrink-0">
                <div class="flex items-center gap-2">
                  <iconify-icon icon="mdi:trophy-variant" class="text-farm-yellow text-lg md:text-xl shrink-0"></iconify-icon>
                  <p class="text-xs md:text-sm font-dnf tracking-[0.25em] text-[#D4E6A8] font-bold rank-text-shadow uppercase">RANKING</p>
                </div>
                <p class="text-2xl md:text-4xl font-dnf text-white font-black rank-text-shadow tabular-nums leading-tight mt-0.5 pl-9 md:pl-10">
                  {{ currentSlide.title }}
                </p>
              </div>

              <!-- 중간: 구분선 + 포인트 뱃지 -->
              <div class="hidden sm:flex flex-1 flex-col items-center justify-center min-w-0 px-4">
                <div class="w-full flex flex-col items-center gap-3">
                  <div class="w-full flex justify-between items-center">
                    <span class="w-2 h-2 rounded-full bg-farm-yellow/70 ring-2 ring-farm-cream/40 shrink-0"></span>
                    <span class="flex-1 mx-2 border-t border-dashed border-farm-cream/35"></span>
                    <div class="flex items-center gap-1.5 shrink-0">
                      <iconify-icon icon="mdi:star-four-points" class="text-farm-yellow/90 text-xs shrink-0"></iconify-icon>
                      <span class="text-[10px] md:text-xs font-dnf font-bold tracking-[0.15em] text-farm-cream/95 uppercase whitespace-nowrap">문제별 포인트</span>
                    </div>
                    <span class="flex-1 mx-2 border-t border-dashed border-farm-cream/35"></span>
                    <span class="w-2 h-2 rounded-full bg-farm-yellow/70 ring-2 ring-farm-cream/40 shrink-0"></span>
                  </div>
                  <div class="flex flex-col items-center gap-2">
                    <div class="flex items-center justify-center gap-2 md:gap-2.5">
                      <div
                        v-for="n in 3"
                        :key="n"
                        class="level-point-badge flex items-center gap-1.5 px-2 py-1 rounded-full"
                      >
                        <span class="text-[10px] md:text-xs font-bold text-farm-cream/90 tabular-nums">Lv.{{ n }}</span>
                        <span class="w-px h-3 bg-farm-cream/40 rounded-full"></span>
                        <span class="text-farm-yellow font-black text-xs tabular-nums drop-shadow-sm">{{ levelPoints[n - 1] }}<span class="text-[9px] font-semibold text-farm-cream/70 ml-0.5">pt</span></span>
                      </div>
                    </div>
                    <div class="flex items-center justify-center gap-2 md:gap-2.5">
                      <div
                        v-for="n in [4, 5]"
                        :key="n"
                        class="level-point-badge flex items-center gap-1.5 px-2 py-1 rounded-full"
                      >
                        <span class="text-[10px] md:text-xs font-bold text-farm-cream/90 tabular-nums">Lv.{{ n }}</span>
                        <span class="w-px h-3 bg-farm-cream/40 rounded-full"></span>
                        <span class="text-farm-yellow font-black text-xs tabular-nums drop-shadow-sm">{{ levelPoints[n - 1] }}<span class="text-[9px] font-semibold text-farm-cream/70 ml-0.5">pt</span></span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 우측: 랭킹 이미지 -->
              <div class="flex justify-end items-center shrink-0 flex-1 min-w-0">
                <div class="relative inline-block leading-[0] translate-y-3 md:translate-y-5">
                  <img
                    :src="rankImg"
                    alt="rank"
                    class="h-16 md:h-20 w-auto select-none pointer-events-none opacity-95 drop-shadow-2xl block"
                    draggable="false"
                  />
                  <div class="absolute inset-0 flex items-center justify-center text-center pb-10 md:pb-17">
                    <div>
                      <div class="text-base md:text-2xl font-dnf text-white leading-tight font-bold text-glow-olive">
                        {{ currentSlide.nickname ?? '—' }}
                      </div>
                      <div v-if="currentSlide.cardCount != null" class="mt-1 flex items-center justify-center gap-1.5 text-xs md:text-sm font-semibold text-white/95 leading-tight drop-shadow-lg">
                        <span>{{ currentSlide.cardCount }}장</span>
                        <span class="text-white/60">·</span>
                        <span>{{ (currentSlide.cardCount ?? 0) * 100 }}pt</span>
                      </div>
                    </div>
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
import rankImg from '@/assets/banner/rank.png'

const levelPoints = [30, 50, 80, 100, 150]

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
      nickname: getNick(0),
      cardCount: getCount(0),
    },
    {
      key: 'rank-2',
      type: 'rank',
      title: '2위',
      nickname: getNick(1),
      cardCount: getCount(1),
    },
    {
      key: 'rank-3',
      type: 'rank',
      title: '3위',
      nickname: getNick(2),
      cardCount: getCount(2),
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
.ranking-banner {
  background: linear-gradient(135deg, rgba(124, 187, 103, 1) 0%, rgba(143, 193, 96, 0.95) 50%, rgba(124, 187, 103, 1) 100%);
}

.ranking-banner::before {
  content: '';
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(255, 214, 93, 0.2) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}


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

.text-glow-olive {
  text-shadow: 
    0 0 4px rgba(124, 187, 103, 0.4),
    0 0 8px rgba(124, 187, 103, 0.3),
    0 0 12px rgba(124, 187, 103, 0.2),
    0 2px 4px rgba(0, 0, 0, 0.5);
}

.rank-text-shadow {
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
}

.level-point-badge {
  background: linear-gradient(135deg, rgba(255, 250, 240, 0.28) 0%, rgba(255, 224, 130, 0.15) 100%);
  border: 1px solid rgba(255, 250, 240, 0.4);
  box-shadow: 
    0 1px 4px rgba(78, 59, 42, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
}
</style>

