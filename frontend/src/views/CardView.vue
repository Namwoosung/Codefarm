<template>
  <div
    class="flex flex-col w-full h-[calc(100vh-4rem)] max-h-[calc(100vh-4rem)] min-h-0 overflow-hidden bg-farm-cream"
    @dblclick.stop.prevent
  >
    <!-- 상단 배너 -->
    <section class="relative w-full bg-farm-olive px-20 py-3 md:py-4 overflow-hidden flex-shrink-0">
      <div class="min-h-[92px] md:min-h-[112px] flex flex-col justify-center px-10">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl md:text-3xl font-bold text-farm-cream font-dnf tracking-tight">
            {{ user?.nickname ?? 'Farm' }}'s Farm Crew
          </h1>
          <span class="text-sm md:text-base font-black text-farm-cream/95 tracking-tight">
            {{ (cards?.length ?? 0) }} / {{ GRADES.reduce((sum, g) => sum + gradeMeta[g].slots, 0) }} 개
          </span>
        </div>
      </div>
    </section>

    <!-- 카드 목록 영역: 남은 화면을 전부 사용 -->
    <div class="w-full flex flex-1 min-h-0 overflow-hidden">
      <!-- 좌측: 카드 뽑기 영역 (1) -->
      <aside class="w-2/7 h-full border-r-2 border-farm-brown-dark/50 px-8 pt-6 pb-10 flex flex-col items-center justify-start relative overflow-hidden flex-shrink-0">
        <div class="relative z-10 w-full flex flex-col items-center gap-4">
          <div class="text-center">
            <div class="inline-flex items-center gap-3 mb-4">
              <span class="px-2.5 py-1 rounded-full bg-farm-olive text-farm-paper text-[11px] font-black tracking-wider shadow-sm">
                GACHA CONSOLE
              </span>
              <span class="px-2.5 py-1 rounded-full bg-farm-yellow/30 text-farm-brown-dark text-[11px] font-black tracking-wider border border-farm-brown/15">
                DAILY
              </span>
            </div>
            <h2 class="text-3xl font-dnf text-farm-olive mb-2">Gacha!</h2>
            <p class="text-farm-olive font-bold opacity-75">새로운 크루를 영입해보세요</p>
          </div>

          <!-- 카드 뽑기 버튼 (이미지 형태나 큰 버튼) -->
          <img :src="gachaImg" class="w-120 h-50 object-contain select-none" alt="gacha" draggable="false" />

          <!-- 버튼 하단 HUD 박스 -->
          <div class="w-full rounded-2xl p-4">
            <!-- Charge: 버튼 바로 아래 -->
            <div class="flex flex-col items-center w-full">
              <div class="w-[88%] max-w-[260px] h-3.5 rounded-full bg-farm-brown/20 overflow-hidden border border-farm-brown/30 flex-shrink-0">
                <div
                  :class="[
                    'gacha-bar h-full rounded-full bg-gradient-to-r from-farm-yellow to-farm-green transition-[width] duration-200 ease-out',
                    { 'gacha-bar--full': chargeProgress >= 1 },
                  ]"
                  :style="{ width: `${Math.max(0, Math.min(100, chargeProgress * 100))}%` }"
                ></div>
              </div>
              <p class="mt-3 text-xs font-bold text-farm-brown-dark/80 text-center w-full block">
                보유 포인트 : {{ points.toLocaleString() }}P
              </p>
            </div>
          </div>
          <button
            type="button"
            class="mx-auto inline-flex items-center justify-center bg-farm-paper text-farm-brown-dark py-2 px-10 rounded-3xl font-black text-center cursor-pointer border-4 border-farm-brown-dark shadow-[4px_6px_0_var(--color-farm-brown-dark)] transition-all hover:translate-y-1 hover:translate-x-1 hover:shadow-[3px_3px_0_var(--color-farm-brown-dark)] hover:brightness-95 active:translate-y-2 active:translate-x-2 active:shadow-[1px_1px_0_var(--color-farm-brown-dark)] active:brightness-90 focus:outline-none focus-visible:ring-4 focus-visible:ring-farm-brown-dark/50"
            @click="gachaCard"
          >
            카드뽑기 | 100P
          </button>
        </div>
        
        <!-- 배경 장식 -->
        <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-farm-green/10 rounded-full blur-3xl"></div>
        <div class="absolute -top-10 -right-10 w-40 h-40 bg-farm-yellow/10 rounded-full blur-3xl"></div>
      </aside>

      <!-- 우측: 카드 리스트 영역 - 너비·높이 꽉 채움 -->
      <main class="flex-1 h-full min-w-0 flex flex-col min-h-0 bg-farm-cream/30 relative overflow-hidden">
        <!-- 배경 텍스처 (선택) -->
        <div
          class="absolute inset-0 bg-center bg-cover opacity-20 pointer-events-none"
          :style="{ backgroundImage: `url(${cardListBg})` }"
        />
        <!-- 등급별 보유 개수 요약: 카드 목록 시작점을 내려서 상단 잘림 방지 -->
        <div class="relative z-10 flex-shrink-0 flex flex-wrap items-center gap-2 px-6 py-3 border-b border-farm-brown/15 bg-farm-cream/50">
          <span class="text-xs font-bold text-farm-brown-dark/80 mr-1">등급별 보유</span>
          <template v-for="grade in GRADES" :key="grade">
            <span
              class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-dnf bg-white/80 border border-farm-brown/20 text-farm-brown-dark shadow-sm"
            >
              <span :class="gradeMeta[grade].color" class="w-2 h-2 rounded-full flex-shrink-0"></span>
              {{ gradeMeta[grade].name }} {{ cardCountByGrade[grade] }}/{{ gradeMeta[grade].slots }}
            </span>
          </template>
        </div>
        <!-- 등급별 리스트: 오른쪽 전체 채움 -->
        <div class="relative z-10 flex-1 min-h-0 overflow-y-auto scrollbar-hide snap-y snap-mandatory scroll-py-2 px-6 py-4">
          <section
            v-for="grade in GRADES"
            :key="grade"
            class="snap-center min-h-[48%] my-2 flex flex-col justify-center px-4 py-4 rounded-2xl"
          >
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-xl font-dnf text-farm-brown-dark flex items-center gap-3">
                    <span :class="gradeMeta[grade].color" class="w-3 h-8 rounded-lg shadow-sm"></span>
                    {{ gradeMeta[grade].name }}
                  </h3>
                  <span class="px-3 py-1 rounded-lg bg-farm-cream text-sm font-bold text-farm-brown">
                    {{ cardCountByGrade[grade] }} / {{ gradeMeta[grade].slots }}
                  </span>
                </div>

                <!-- 가로 스크롤 슬롯 -->
                <div class="relative group">
                  <!-- 좌우 이동 버튼 -->
                  <button
                    v-if="grade !== 'SPECIAL'"
                    type="button"
                    @click="scroll(grade, 'left')"
                    class="absolute -left-4 top-1/2 -translate-y-1/2 z-[80] w-10 h-10 bg-transparent rounded-full flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 hover:bg-white/25 active:bg-white/35"
                  >
                    <iconify-icon icon="mdi:chevron-left" class="text-2xl text-farm-brown-dark"></iconify-icon>
                  </button>

                  <button
                    v-if="grade !== 'SPECIAL'"
                    type="button"
                    @click="scroll(grade, 'right')"
                    class="absolute -right-4 top-1/2 -translate-y-1/2 z-[80] w-10 h-10 bg-transparent rounded-full flex items-center justify-center transition-all opacity-0 group-hover:opacity-100 hover:bg-white/25 active:bg-white/35"
                  >
                    <iconify-icon icon="mdi:chevron-right" class="text-2xl text-farm-brown-dark"></iconify-icon>
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

                        <!-- 카드 아래 count 표시 -->
                        <div
                          class="mt-2 inline-flex items-center rounded-full bg-farm-cream/90 border border-farm-brown/15 px-2 py-0.5 text-xs font-black text-farm-brown-dark shadow-sm"
                        >
                          x{{ getCardCount(slotCard) }}
                        </div>
                      </div>
                      <div
                        v-else
                        :class="[
                          'bg-transparent border-2 border-dashed border-base-content/35 rounded-xl shadow-md flex items-center justify-center',
                          'w-full',
                          grade === 'SPECIAL' ? 'aspect-[1024/723]' : 'aspect-[1872/2613]',
                        ]"
                      >
                        <span class="text-4xl font-extrabold text-base-content/20">?</span>
                      </div>
                    </div>
                  </div>
                </div>
          </section>
        </div>
      </main>
    </div>
  </div>

  <!-- 카드 확대 팝업 -->
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
            <div
              v-if="isGachaModal && drawMessage"
              class="absolute top-3 left-1/2 -translate-x-1/2 z-10 px-4 py-2 rounded-full bg-black/70 text-white text-sm font-bold shadow-lg backdrop-blur-sm"
            >
              {{ drawMessage }}
            </div>
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

<script setup>
import { useProfileStore } from '@/stores/profile'
import { useCardStore } from '@/stores/card'
import { storeToRefs } from 'pinia'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import CardDetail from '@/components/organisms/CardDetail.vue'
import cardListBg from '@/assets/cardlist.png'
import gachaImg from '@/assets/Gacha.png'

const profile = useProfileStore()
const cardStore = useCardStore()
const { user } = storeToRefs(profile)
const { cards, drawMessage } = storeToRefs(cardStore)

const points = computed(() => Number(user.value?.point ?? 0))

// Charge: 100P 기준(0~100%), 100P 이상이면 100%
const chargeProgress = computed(() => Math.min(1, Math.max(0, points.value / 100)))

onMounted(async () => {
  try {
    await profile.userinfo()
    await cardStore.cardList()
  } catch (err) {
    console.warn('[CardView] mounted fetch failed:', err)
  }
})

onBeforeUnmount(() => {
  unlockScroll()
})

// 카드 뽑기
const gachaCard = async () => {
  if ((user.value?.point ?? 0) < 100) {
    alert('포인트가 부족합니다.')
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
/* 3D 기울임 시 카드가 잘리지 않도록 overflow 제거 */
.modal-card-3d,
.modal-card-3d > :first-child {
  overflow: visible !important;
}

/* Charge bar: 100%일 때만 반짝임 */
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
</style>
