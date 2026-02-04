<template>
  <div>
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-150 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="isInitialLoading"
          class="fixed inset-0 z-[9998] flex items-center justify-center bg-[rgba(245,242,232,0.92)]"
        >
          <span class="loading loading-spinner loading-lg app-loading-spinner"></span>
        </div>
      </Transition>
    </Teleport>

    <template v-if="!isInitialLoading">
      <div
        class="flex flex-col w-full h-[calc(100vh-4rem)] max-h-[calc(100vh-4rem)] min-h-0 overflow-hidden bg-farm-cream"
        @dblclick.stop.prevent
      >
        <!-- 상단 배너 -->
        <section class="card-hero relative w-full overflow-visible flex-shrink-0">
          <div class="absolute inset-0 opacity-20 pointer-events-none z-0">
            <div class="absolute top-0 left-0 w-32 h-32 bg-farm-yellow/30 rounded-full blur-3xl"></div>
            <div class="absolute bottom-0 right-0 w-40 h-40 bg-farm-green/30 rounded-full blur-3xl"></div>
          </div>
          <div class="absolute inset-0 opacity-[0.06] pointer-events-none z-0" style="background-image: repeating-linear-gradient(45deg, transparent, transparent 8px, rgba(255,255,255,0.15) 8px, rgba(255,255,255,0.15) 16px);"></div>

          <div class="relative z-10 h-[120px] md:h-[140px] flex items-center justify-between px-6 sm:px-10 md:px-16">
            <div class="flex flex-col justify-center pl-2 pr-4 sm:pr-8">
              <p class="text-xl md:text-3xl font-dnf text-farm-cream drop-shadow-lg tracking-tight leading-tight">
                Gacha ! 새로운 크루 뽑으러 가기
              </p>
              <p class="mt-1 text-sm md:text-base text-farm-cream/85 font-dnf">
                {{ bannerNickname }}의 Farm Crew
              </p>
            </div>
            <div class="absolute right-4 sm:right-8 md:right-12 -bottom-1.5 z-10 pointer-events-none select-none flex items-end">
              <div class="hero-blob absolute -right-4 -bottom-6 w-32 h-32 md:w-48 md:h-48 rounded-full blur-2xl"></div>
              <div class="absolute right-20 -top-2 w-9 h-9 rounded-full flex items-center justify-center bg-white/25 border border-white/30 text-white/95 backdrop-blur-sm shadow-lg hero-spark--1">
                <iconify-icon icon="mdi:sparkles" class="text-lg"></iconify-icon>
              </div>
              <div class="absolute right-2 top-4 w-9 h-9 rounded-full flex items-center justify-center bg-white/25 border border-white/30 text-white/95 backdrop-blur-sm shadow-lg hero-spark--2 hidden sm:flex">
                <iconify-icon icon="mdi:star-four-points" class="text-lg"></iconify-icon>
              </div>
              <img
                :src="farmerImg"
                alt="farmer"
                draggable="false"
                class="hero-farmer h-[100px] md:h-[130px] w-auto opacity-95 drop-shadow-[0_12px_24px_rgba(0,0,0,0.25)] relative"
              />
            </div>
          </div>
        </section>

    <div class="w-full flex flex-1 min-h-0 overflow-hidden">
      <aside class="w-72 md:w-80 h-full border-r border-farm-brown/20 bg-farm-paper/50 px-4 py-5 flex flex-col items-center justify-center relative overflow-hidden flex-shrink-0">
        <div class="gacha-panel w-full h-full max-h-full flex flex-col">
          
          <div class="gacha-stage gacha-stage--panel relative w-full flex justify-center items-end" :class="{ 'gacha-stage--ready': canDraw }" aria-hidden="true">
            <div class="gacha-shadow"></div>
            <div class="gacha-float h-full flex items-center justify-center">
              <img :src="gachaImg" class="gacha-card-img w-full max-w-[16rem] h-auto max-h-full object-contain select-none" alt="gacha" draggable="false" />
            </div>
          </div>

          <div class="w-full max-w-[280px] flex flex-col items-center gap-2.5 relative z-10">
            <div class="gacha-panel__track w-full" aria-hidden="true">
              <div
                :class="[
                  'gacha-bar h-full rounded-full bg-gradient-to-r from-farm-yellow to-farm-green transition-[width] duration-200 ease-out',
                  { 'gacha-bar--full': chargeProgress >= 1 },
                ]"
                :style="{ width: `${Math.max(0, Math.min(100, chargeProgress * 100))}%` }"
              ></div>
            </div>
            <div class="text-sm text-farm-brown-dark/80 relative z-10 w-full text-center font-dnf font-semibold">보유 포인트 <span class="text-farm-point font-bold">{{ points.toLocaleString() }}P</span></div>
          </div>

          <button type="button" class="gacha-draw-btn gacha-draw-btn--wide font-dnf" @click="gachaCard" :disabled="!canDraw">
            <span
              class="gacha-draw-btn__fill"
              :style="{ width: `${Math.max(0, Math.min(100, chargeProgress * 100))}%` }"
              aria-hidden="true"
            ></span>
            <span class="relative z-[2] inline-flex items-center gap-2.5">
              <span class="gacha-draw-btn__label">Gacha !</span>
              <span class="gacha-draw-btn__cost bg-white/55 border border-farm-brown/20 shadow-sm">100P</span>
            </span>
          </button>
        </div>
      </aside>

      <main class="flex-1 h-full min-w-0 flex flex-col min-h-0 bg-farm-cream/40 relative overflow-hidden">
        <div
          class="absolute inset-0 bg-center bg-cover opacity-[0.18] pointer-events-none"
          :style="{ backgroundImage: `url(${cardListBg})` }"
        />
        <div class="relative z-10 flex-shrink-0 flex flex-wrap items-center gap-2 px-4 sm:px-6 py-3 border-b border-farm-brown/15 bg-farm-cream/60 backdrop-blur-sm">
          <span class="text-xs font-bold text-farm-brown-dark/90">등급별 보유</span>
          <template v-for="grade in GRADES" :key="grade">
            <span
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-dnf bg-farm-paper/95 border border-farm-brown/15 text-farm-brown-dark shadow-sm"
            >
              <span :class="gradeMeta[grade].color" class="w-2 h-2 rounded-full flex-shrink-0"></span>
              {{ gradeMeta[grade].name }} {{ cardCountByGrade[grade] }}/{{ gradeMeta[grade].slots }}
            </span>
          </template>
        </div>
        <div class="relative z-10 flex-1 min-h-0 overflow-y-auto scrollbar-hide snap-y snap-mandatory scroll-py-2 px-4 sm:px-6 py-4">
          <section
            v-for="grade in GRADES"
            :key="grade"
            class="snap-center min-h-[48%] my-3 flex flex-col justify-center px-3 sm:px-4 py-4 rounded-xl bg-farm-paper/30"
          >
                <div class="flex items-center justify-between mb-3">
                  <h3 class="text-lg md:text-xl font-dnf text-farm-brown-dark font-bold flex items-center gap-2">
                    <span :class="gradeMeta[grade].color" class="w-2.5 h-7 rounded-md shadow-sm"></span>
                    {{ gradeMeta[grade].name }}
                  </h3>
                  <span class="px-2.5 py-1 rounded-lg bg-farm-cream/90 border border-farm-brown/10 text-sm font-bold text-farm-brown-dark">
                    {{ cardCountByGrade[grade] }} / {{ gradeMeta[grade].slots }}
                  </span>
                </div>

                <div class="relative group">
                  <button
                    v-if="grade !== 'SPECIAL'"
                    type="button"
                    @click="scroll(grade, 'left')"
                    class="absolute -left-2 sm:-left-4 top-1/2 -translate-y-1/2 z-[80] w-9 h-9 sm:w-10 sm:h-10 bg-farm-paper/80 hover:bg-farm-paper border border-farm-brown/15 rounded-full flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 shadow-sm"
                  >
                    <iconify-icon icon="mdi:chevron-left" class="text-xl sm:text-2xl text-farm-brown-dark"></iconify-icon>
                  </button>

                  <button
                    v-if="grade !== 'SPECIAL'"
                    type="button"
                    @click="scroll(grade, 'right')"
                    class="absolute -right-2 sm:-right-4 top-1/2 -translate-y-1/2 z-[80] w-9 h-9 sm:w-10 sm:h-10 bg-farm-paper/80 hover:bg-farm-paper border border-farm-brown/15 rounded-full flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 shadow-sm"
                  >
                    <iconify-icon icon="mdi:chevron-right" class="text-xl sm:text-2xl text-farm-brown-dark"></iconify-icon>
                  </button>

                  <div
                    :ref="(el) => setScrollEl(grade, el)"
                    class="flex gap-4 overflow-x-auto pt-4 pb-6 px-4 scrollbar-hide snap-x"
                  >
                    <div
                      v-for="(slotCard, idx) in slotsByGrade[grade]"
                      :key="`${grade}-slot-${idx}`"
                      :class="[
                        'relative flex-shrink-0 snap-start transition-transform hover:scale-105 hover:z-50 duration-300',
                        grade === 'SPECIAL' ? 'w-[340px]' : 'w-[170px]',
                      ]"
                    >
                      <div v-if="slotCard" class="w-full flex flex-col items-center">
                        <CardDetail class="w-full" :card="slotCard" @showcard="openCardModal" />

                        <div
                          class="mt-2 inline-flex items-center rounded-full bg-farm-cream/90 border border-farm-brown/15 px-2 py-0.5 text-xs font-black text-farm-brown-dark shadow-sm"
                        >
                          x{{ getCardCount(slotCard) }}
                        </div>
                      </div>
                      <div
                        v-else
                        :class="[
                          'bg-farm-cream/40 border-2 border-dashed border-farm-brown/25 rounded-xl flex items-center justify-center',
                          'w-full',
                          grade === 'SPECIAL' ? 'aspect-[1024/723]' : 'aspect-[1872/2613]',
                        ]"
                      >
                        <span class="text-3xl md:text-4xl font-bold text-farm-brown/30">?</span>
                      </div>
                    </div>
                  </div>
                </div>
          </section>
        </div>
      </main>
    </div>
      </div>

      <Transition
        enter-active-class="transition-opacity duration-150 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition-opacity duration-100 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div
          v-if="selectedCard"
          class="fixed inset-0 z-[999] flex items-center justify-center bg-black/50 backdrop-blur-[1px] p-4"
          @click.self="closeCardModal"
        >
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 scale-95 translate-y-2"
            enter-to-class="opacity-100 scale-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 scale-100 translate-y-0"
            leave-to-class="opacity-0 scale-95 translate-y-2"
          >
            <div
              ref="modalCardEl"
              class="modal-card-3d"
              :class="popupCardContainerClass"
              :style="modalPointerStyle"
              @pointerenter="onModalPointerMove"
              @pointermove="onModalPointerMove"
              @pointerleave="onModalPointerLeave"
            >
              <figure class="w-full h-full rounded-2xl overflow-visible relative block m-0">
                <img
                  :src="modalCardImage"
                  :alt="selectedCard.name"
                  class="w-full h-full object-contain block"
                  loading="lazy"
                />
              </figure>
            </div>
          </Transition>
        </div>
      </Transition>
    </template>
  </div>
</template>

<script setup>
import { useProfileStore } from '@/stores/profile'
import { useCardStore } from '@/stores/card'
import { storeToRefs } from 'pinia'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useToastStore } from '@/stores/toast'
import CardDetail from '@/components/organisms/CardDetail.vue'
import cardListBg from '@/assets/card/cardlist.png'
import gachaImg from '@/assets/card/Gacha.png'
import farmerImg from '@/assets/roadmap/farmer.png'

const profile = useProfileStore()
const cardStore = useCardStore()
const { user } = storeToRefs(profile)
const { cards, drawMessage } = storeToRefs(cardStore)
const toastStore = useToastStore()

const points = computed(() => Number(user.value?.point ?? 0))
const bannerNickname = computed(() => user.value?.nickname ?? 'Farm')
const totalOwnedCards = computed(() => (Array.isArray(cards.value) ? cards.value.length : 0))
const canDraw = computed(() => points.value >= 100)

const isInitialLoading = ref(true)

// Charge: 100P 기준(0~100%), 100P 이상이면 100%
const chargeProgress = computed(() => Math.min(1, Math.max(0, points.value / 100)))

onMounted(async () => {
  try {
    await profile.userinfo()
    await cardStore.cardList()
  } catch (err) {
    console.warn('[CardView] mounted fetch failed:', err)
  } finally {
    isInitialLoading.value = false
  }
})

onBeforeUnmount(() => {
  unlockScroll()
})

// 카드 뽑기
const gachaCard = async () => {
  if ((user.value?.point ?? 0) < 100) {
    toastStore.showToast('포인트가 부족합니다.')
    return
  } else {
    await cardStore.cardDraw()
    await profile.userinfo()
    selectedCard.value = cardStore.newcard?.card ?? cardStore.newcard
    console.log('남은 포인트:', user.value.point)
    isGachaModal.value = true
    lockScroll()
  }
}

watch(
  () => drawMessage.value,
  (msg) => {
    if (!msg) return
    const text = String(msg)
    const durationMs = text.includes('이미 보유') ? 900 : 2600
    setTimeout(() => {
      toastStore.showToast(text, { durationMs })
    }, 350)
  }
)

// 카드 상세 팝업
const openCardModal = (card) => {
  drawMessage.value = ''
  isGachaModal.value = false
  selectedCard.value = card
  lockScroll()
}
const closeCardModal = () => {
  drawMessage.value = ''
  isGachaModal.value = false
  selectedCard.value = null
  toastStore.clearToast()
  unlockScroll()
}
const selectedCard = ref(null)
const isGachaModal = ref(false)

// 백엔드가 카드 이미지를 .svg로 주는 경우 .png로 변환
const modalCardImage = computed(() => {
  const c = selectedCard.value
  if (!c) return ''
  const raw = c.image ?? c.cardImage ?? c.img ?? ''
  return typeof raw === 'string' ? raw.replace(/\.svg$/i, '.png') : ''
})

const scrollLockPrev = {
  htmlOverflow: '',
  htmlPaddingRight: '',
  bodyOverflow: '',
}

// 스크롤 잠금 및 해제
const lockScroll = () => {
  const html = document.documentElement
  const body = document.body

  scrollLockPrev.htmlOverflow = html.style.overflow
  scrollLockPrev.htmlPaddingRight = html.style.paddingRight
  scrollLockPrev.bodyOverflow = body.style.overflow

  const scrollbarWidth = window.innerWidth - html.clientWidth
  html.style.overflow = 'hidden'
  if (scrollbarWidth > 0) html.style.paddingRight = `${scrollbarWidth}px`
  body.style.overflow = 'hidden'
}
const unlockScroll = () => {
  const html = document.documentElement
  const body = document.body
  html.style.overflow = scrollLockPrev.htmlOverflow
  html.style.paddingRight = scrollLockPrev.htmlPaddingRight
  body.style.overflow = scrollLockPrev.bodyOverflow
}

// 카드 등급별 카드 구분 
const GRADES = ['SPECIAL', 'GOLD', 'SILVER', 'BRONZE']
const gradeMeta = {
  SPECIAL: { name: 'MEGACREW', color: 'bg-purple-500', slots: 1 },
  GOLD: { name: 'MEGA', color: 'bg-yellow-400', slots: 7 },
  SILVER: { name: 'SUPER', color: 'bg-slate-400', slots: 10 },
  BRONZE: { name: 'BASIC', color: 'bg-orange-400', slots: 12 },
}

const cardCountByGrade = computed(() => {
  const counts = Object.fromEntries(GRADES.map((g) => [g, 0]))
  for (const c of cards.value ?? []) {
    if (c?.grade && counts[c.grade] !== undefined) counts[c.grade] += 1
  }
  return counts
})

const slotsByGrade = computed(() => {
  const result = Object.fromEntries(GRADES.map((g) => [g, Array.from({ length: gradeMeta[g].slots }, () => null)]))
  // cards를 한 번만 순회하면서 등급/슬롯 위치에 바로 배치
  // no(1-based) -> idx(0-based)
  for (const c of cards.value ?? []) {
    const grade = c?.grade
    if (!grade || result[grade] === undefined) continue
    const slots = result[grade]
    const no = Number(c?.no)
    if (!Number.isFinite(no)) continue
    const idx = no - 1
    if (idx < 0 || idx >= slots.length) continue
    slots[idx] = c
  }
  return result
})

const scrollElByGrade = new Map()
const setScrollEl = (grade, el) => {
  if (!el) return
  scrollElByGrade.set(grade, el)
}
const scroll = (grade, direction) => {
  const container = scrollElByGrade.get(grade)
  if (!container) return
  container.scrollBy({
    left: direction === 'left' ? -300 : 300,
    behavior: 'smooth',
  })
}
const popupCardContainerClass = computed(() => {
  const base =
    'hover-3d relative bg-transparent rounded-2xl overflow-visible shadow-2xl shadow-[0_0_60px_rgba(255,255,255,0.35)]'
  const grade = selectedCard.value?.grade
  return grade === 'SPECIAL'
    ? `${base} w-[min(92vw,800px)] aspect-[1024/723]`
    : `${base} w-[min(92vw,350px)] aspect-[1872/2613]`
})

const getCardCount = (card) => {
  const n = Number(card?.count)
  return Number.isFinite(n) && n > 0 ? n : 1
}

const modalCardEl = ref(null)
const modalPointerPos = ref({ x: 0, y: 0 })
const modalPointerActive = ref(false)

function getModalPointerPosition(e) {
  const el = modalCardEl.value
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

function onModalPointerMove(e) {
  modalPointerActive.value = true
  const pos = getModalPointerPosition(e)
  if (pos) modalPointerPos.value = pos
}

function onModalPointerLeave() {
  modalPointerActive.value = false
  modalPointerPos.value = { x: 0, y: 0 }
}

const modalPointerStyle = computed(() => {
  if (!modalPointerActive.value) return {}
  const { x, y } = modalPointerPos.value
  return {
    '--transform': `${x}, ${y}`,
    '--shine': `${(x + 1) * 50}% ${(y + 1) * 50}%`,
    '--shadow': `${x * 0.5}rem ${y * 0.5}rem`,
  }
})
</script>

<style scoped>
.card-hero {
  background: linear-gradient(120deg, rgba(255, 210, 95, 0.98), rgba(143, 193, 96, 0.95) 55%, rgba(124, 187, 103, 0.95));
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}
.card-hero::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.22;
  background:
    radial-gradient(1200px 260px at 10% 0%, rgba(255, 255, 255, 0.55), transparent 60%),
    radial-gradient(900px 260px at 95% 15%, rgba(255, 255, 255, 0.35), transparent 62%),
    repeating-linear-gradient(135deg, rgba(255, 255, 255, 0.18) 0 1px, transparent 1px 10px);
  mix-blend-mode: soft-light;
}
.card-hero::after {
  content: '';
  position: absolute;
  inset: -2px;
  pointer-events: none;
  opacity: 0.22;
  background: radial-gradient(600px 220px at 30% 100%, rgba(0, 0, 0, 0.25), transparent 60%);
}
.hero-blob {
  background: radial-gradient(circle at 30% 30%, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0.0) 60%),
    radial-gradient(circle at 70% 70%, rgba(255, 214, 93, 0.55), rgba(255, 214, 93, 0.0) 65%);
  opacity: 0.85;
}
.hero-farmer {
  animation: none;
}
.hero-spark--1,
.hero-spark--2 {
  animation: hero-float 5.4s ease-in-out infinite;
}
.hero-spark--1 {
  animation-delay: -1.2s;
}
.hero-spark--2 {
  animation-delay: -2.6s;
}
@keyframes hero-float {
  0%,
  100% {
    transform: translate3d(0, 0, 0);
  }
  50% {
    transform: translate3d(0, -6px, 0);
  }
}
.modal-card-3d,
.modal-card-3d > :first-child {
  overflow: visible !important;
}
.gacha-bar {
  position: relative;
}
.gacha-bar--full {
  animation: gacha-bar-glow 2.2s ease-in-out infinite;
}
.gacha-bar--full::after {
  content: '';
  position: absolute;
  top: -30%;
  bottom: -30%;
  width: 42%;
  left: -60%;
  transform: skewX(-20deg);
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.65),
    transparent
  );
  animation: gacha-bar-shine 3.6s ease-in-out infinite;
  pointer-events: none;
  opacity: 0.95;
}

@keyframes gacha-bar-shine {
  0% { left: -60%; opacity: 0; }
  20% { opacity: 0.9; }
  50% { left: 120%; opacity: 0.9; }
  100% { left: 120%; opacity: 0; }
}

@keyframes gacha-bar-glow {
  0%, 100% {
    filter: saturate(1.05) brightness(1.02);
    box-shadow: 0 0 0 rgba(255, 214, 93, 0);
  }
  50% {
    filter: saturate(1.15) brightness(1.08);
    box-shadow: 0 0 14px rgba(255, 214, 93, 0.55);
  }
}
.gacha-panel {
  width: 100%;
  padding: clamp(20px, 3%, 14px) clamp(12px, 4%, 16px);
  border-radius: 26px;
  background:
    radial-gradient(520px 260px at 50% 0%, rgba(255, 255, 255, 0.78), rgba(255, 255, 255, 0) 62%),
    linear-gradient(180deg, rgba(255, 253, 245, 0.92), rgba(245, 242, 232, 0.72));
  border: 1px solid rgba(122, 92, 62, 0.14);
  box-shadow: 0 18px 42px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: clamp(4px, 2%, 8px);
  min-height: 0;
}

.gacha-panel::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 2px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.55), rgba(56, 189, 248, 0.55), rgba(255, 224, 130, 0.40));
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0.75;
  pointer-events: none;
  z-index: 0;
}

.gacha-panel__headline {
  font-size: 45px;
  line-height: 1;
  color: rgba(74, 74, 41, 0.95);
  letter-spacing: -0.03em;
}

.gacha-panel__sub {
  margin-top: 8px;
  font-size: 18px;
  color: rgba(78, 59, 42, 0.55);
}

.gacha-stage--panel {
  margin-top: 0;
  margin-bottom: 0;
  flex: 1 1 0;
  min-height: 0;
}

.gacha-panel__track {
  width: 100%;
  height: 16px;
  border-radius: 9999px;
  background: rgba(122, 92, 62, 0.14);
  border: 1px solid rgba(122, 92, 62, 0.18);
  overflow: hidden;
  position: relative;
  z-index: 1;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.gacha-panel__track::after {
  content: '';
  position: absolute;
  left: 0;
  right: 0;
  top: 0;
  height: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.55), transparent);
  pointer-events: none;
  opacity: 0.65;
}

.gacha-draw-btn--wide {
  width: 100%;
  max-width: 260px;
}
.gacha-stage {
  padding-bottom: clamp(2px, 0.6%, 4px);
  user-select: none;
  -webkit-user-select: none;
  isolation: isolate;
}

.gacha-float {
  position: relative;
  transform-origin: 50% 100%;
  animation: gacha-float 2.8s ease-in-out infinite;
  will-change: transform;
}

.gacha-card-img {
  display: block;
  transform-origin: 50% 85%;
  animation: gacha-wiggle 6.2s ease-in-out infinite;
  will-change: transform, filter;
  filter: drop-shadow(0 18px 18px rgba(0, 0, 0, 0.25));
}

.gacha-shadow {
  position: absolute;
  left: 50%;
  bottom: 2px;
  transform: translateX(-50%);
  width: min(78%, 380px);
  height: 19px;
  border-radius: 9999px;
  background: radial-gradient(closest-side, rgba(0, 0, 0, 0.34), rgba(0, 0, 0, 0) 72%);
  filter: blur(3px);
  opacity: 0.72;
  animation: gacha-shadow 2.8s ease-in-out infinite;
  z-index: -1;
  pointer-events: none;
}

.gacha-stage--ready .gacha-card-img {
  filter: drop-shadow(0 18px 18px rgba(0, 0, 0, 0.25)) saturate(1.05) brightness(1.02);
}
.gacha-stage--ready::after {
  content: '';
  position: absolute;
  inset: 10% 12% 24% 12%;
  background: radial-gradient(circle at 50% 45%, rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0) 62%);
  mix-blend-mode: soft-light;
  opacity: 0.0;
  animation: gacha-ready-glow 2.4s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

@keyframes gacha-float {
  0%, 100% {
    transform: translate3d(0, 0, 0) scale(1.06);
  }
  50% {
    transform: translate3d(0, -12px, 0) scale(1.06);
  }
}

@keyframes gacha-wiggle {
  0%, 100% {
    transform: rotate(-1.2deg) translate3d(-1px, 0, 0);
  }
  50% {
    transform: rotate(1.2deg) translate3d(1px, 0, 0);
  }
}

@keyframes gacha-shadow {
  0%, 100% {
    transform: translateX(-50%) scaleX(0.92);
    opacity: 0.62;
  }
  50% {
    transform: translateX(-50%) scaleX(1.05);
    opacity: 0.82;
  }
}

@keyframes gacha-ready-glow {
  0%, 100% {
    opacity: 0.08;
  }
  50% {
    opacity: 0.22;
  }
}

@media (prefers-reduced-motion: reduce) {
  .gacha-float,
  .gacha-card-img,
  .gacha-shadow,
  .gacha-stage--ready::after {
    animation: none !important;
  }
}
.gacha-draw-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 18px;
  min-width: 120px;
  border-radius: 9999px;
  border: 3px solid var(--color-farm-yellow);
  color: var(--color-farm-olive);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), var(--color-farm-yellow));
  box-shadow: 5px 6px 0 var(--color-farm-yellow);
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  transition: transform 140ms ease, filter 140ms ease, box-shadow 140ms ease;
  isolation: isolate;
}

.gacha-draw-btn__fill {
  position: absolute;
  inset: 0;
  width: 0%;
  border-radius: inherit;
  background: linear-gradient(90deg, rgba(255, 214, 93, 0.55), rgba(255, 245, 220, 0.85));
  opacity: 0.9;
  z-index: 0;
}

.gacha-draw-btn::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  background: conic-gradient(
    from 180deg,
    rgba(255, 214, 93, 0.0),
    rgba(255, 214, 93, 0.75),
    rgba(255, 245, 220, 0.85),
    rgba(255, 214, 93, 0.0)
  );
  filter: blur(10px);
  opacity: 0;
  z-index: -1;
  transition: opacity 180ms ease;
}

.gacha-draw-btn::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  width: 22%;
  left: -30%;
  border-radius: inherit;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.78), transparent);
  transform: skewX(-18deg);
  opacity: 0;
  pointer-events: none;
  z-index: 1;
}

.gacha-draw-btn__label {
  letter-spacing: -0.02em;
  font-size: 18px;
  color: var(--color-farm-olive);
}

.gacha-draw-btn__cost {
  font-weight: 1000;
  font-size: 14px;
  color: var(--color-farm-olive);
  padding: 4px 10px;
  border-radius: 9999px;
}

.gacha-draw-btn:hover:not(:disabled) {
  transform: translate(1px, 1px);
  box-shadow: 4px 4px 0 var(--color-farm-yellow);
  filter: saturate(1.04) brightness(1.05);
}
.gacha-draw-btn:hover:not(:disabled)::before {
  opacity: 0.7;
}

.gacha-draw-btn:hover:not(:disabled)::after {
  opacity: 0.9;
  animation: gacha-btn-shine 1.15s ease-out forwards;
}

.gacha-draw-btn:active:not(:disabled) {
  transform: translate(2px, 2px);
  box-shadow: 2px 2px 0 var(--color-farm-yellow);
  filter: brightness(0.98);
}

.gacha-draw-btn:disabled {
  cursor: not-allowed;
  opacity: 0.55;
  filter: grayscale(0.25) brightness(0.98);
  box-shadow: 5px 6px 0 var(--color-farm-yellow);
}

@keyframes gacha-btn-shine {
  0% { left: -30%; opacity: 0; }
  15% { opacity: 0.9; }
  100% { left: 115%; opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .gacha-draw-btn {
    animation: none !important;
  }
  .gacha-draw-btn::after {
    animation: none !important;
  }
}
</style>
