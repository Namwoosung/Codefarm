<template>
  <div class="h-[750px] flex flex-col overflow-hidden bg-farm-cream" @dblclick.stop.prevent>
    <div class="w-full flex flex-1 min-h-0">
      <!-- 좌측: 카드 뽑기 영역 (1) -->
      <aside class="w-1/4 h-full border-r-4 border-farm-brown-dark bg-farm-paper/50 p-8 flex flex-col items-center justify-center relative overflow-hidden">
        <div class="relative z-10 w-full flex flex-col items-center gap-8">
          <div class="text-center">
            <h2 class="text-3xl font-black text-farm-brown-dark mb-2">Gacha!</h2>
            <p class="text-farm-brown font-bold opacity-75">새로운 크루를 영입해보세요</p>
          </div>

          <!-- 카드 뽑기 버튼 (이미지 형태나 큰 버튼) -->
          <div class="relative group cursor-pointer" @click="gachaCard">
            <div class="absolute inset-0 bg-farm-yellow rounded-3xl blur-xl opacity-20 group-hover:opacity-40 transition-opacity"></div>
            <div class="relative bg-white border-4 border-farm-brown-dark p-6 rounded-3xl shadow-[0_8px_0_#4E3B2A] group-hover:translate-y-1 group-hover:shadow-[0_4px_0_#4E3B2A] transition-all">
              <img :src="cardListBg" class="w-32 h-32 object-contain mb-4 opacity-80" alt="gacha" />
              <div class="bg-farm-olive text-white py-3 px-6 rounded-xl font-black text-center">
                50P 소모
              </div>
            </div>
          </div>

          <div class="bg-white/80 backdrop-blur-sm border-2 border-farm-brown/20 rounded-2xl p-4 w-full text-center">
            <p class="text-farm-brown font-bold text-sm mb-1 uppercase tracking-wider">My Points</p>
            <p class="text-2xl font-black text-farm-brown-dark">{{ user?.point?.toLocaleString() }} P</p>
          </div>
        </div>
        
        <!-- 배경 장식 -->
        <div class="absolute -bottom-10 -left-10 w-40 h-40 bg-farm-green/10 rounded-full blur-3xl"></div>
        <div class="absolute -top-10 -right-10 w-40 h-40 bg-farm-yellow/10 rounded-full blur-3xl"></div>
      </aside>

      <!-- 우측: 카드 리스트 영역 (3) -->
      <main class="w-3/4 h-full flex flex-col min-h-0 bg-farm-cream/30">
        <div class="flex-1 flex flex-col min-h-0 p-8">
          <div class="relative flex-1 flex flex-col min-h-0 border-[12px] border-farm-brown-dark bg-white rounded-[40px] shadow-2xl overflow-hidden">
            <!-- 배경 이미지 -->
            <div
              class="absolute inset-0 bg-center bg-cover opacity-25 pointer-events-none"
              :style="{ backgroundImage: `url(${cardListBg})` }"
            />

            <div class="relative z-10 p-8 pb-8 flex items-center justify-between border-b border-farm-brown/5">
              <div>
                <h2 class="text-2xl font-black text-farm-brown-dark">{{ user?.nickname }}'s Farm Crew</h2>
                <p class="text-farm-brown font-bold opacity-60">수집한 카드 목록을 확인하세요</p>
              </div>
              <div class="flex gap-4">
                <div v-for="grade in GRADES" :key="grade" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-farm-cream border border-farm-brown/10">
                  <span :class="gradeMeta[grade].color" class="w-2 h-2 rounded-full"></span>
                  <span class="text-xs font-black text-farm-brown-dark">{{ cardCountByGrade[grade] }}</span>
                </div>
              </div>
            </div>

            <!-- 등급별 리스트 -->
            <div class="relative z-10 flex-1 min-h-0 overflow-y-auto scrollbar-hide snap-y snap-mandatory p-12 pt-8 pb-12">
              <section v-for="grade in GRADES" :key="grade" class="mb-12 last:mb-0 snap-start">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-xl font-black text-farm-brown-dark flex items-center gap-3">
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
                    v-if="grade !== 'MEGA'"
                    type="button"
                    @click="scroll(grade, 'left')"
                    class="absolute -left-4 top-1/2 -translate-y-1/2 z-20 w-10 h-10 bg-white border-2 border-farm-brown-dark rounded-full shadow-lg flex items-center justify-center hover:bg-farm-cream transition-all opacity-0 group-hover:opacity-100"
                  >
                    <iconify-icon icon="mdi:chevron-left" class="text-2xl text-farm-brown-dark"></iconify-icon>
                  </button>

                  <button
                    v-if="grade !== 'MEGA'"
                    type="button"
                    @click="scroll(grade, 'right')"
                    class="absolute -right-4 top-1/2 -translate-y-1/2 z-20 w-10 h-10 bg-white border-2 border-farm-brown-dark rounded-full shadow-lg flex items-center justify-center hover:bg-farm-cream transition-all opacity-0 group-hover:opacity-100"
                  >
                    <iconify-icon icon="mdi:chevron-right" class="text-2xl text-farm-brown-dark"></iconify-icon>
                  </button>

                  <div
                    :ref="(el) => setScrollEl(grade, el)"
                    class="flex gap-6 overflow-x-auto pt-2 pb-6 px-2 scrollbar-hide snap-x"
                  >
                    <div
                      v-for="(slotCard, idx) in slotsByGrade[grade]"
                      :key="`${grade}-slot-${idx}`"
                      :class="[
                        'flex-shrink-0 snap-start transition-transform hover:scale-105 duration-300',
                        grade === 'SPECIAL' ? 'w-[340px]' : 'w-[170px]',
                      ]"
                    >
                      <CardDetail v-if="slotCard" class="w-full" :card="slotCard" @showcard="openCardModal" />
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
          </div>
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
          <div></div>
          <div></div>
          <div></div>
          <div></div>
          <div></div>
          <div></div>
          <div></div>
          <div></div>
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
import PageTitle from '@/components/atoms/PageTitle.vue'
import CardDetail from '@/components/organisms/CardDetail.vue'
import cardListBg from '@/assets/cardlist.png'

const profile = useProfileStore()
const cardStore = useCardStore()
const { user } = storeToRefs(profile)
const { cards, drawMessage } = storeToRefs(cardStore)

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
  if ((user.value?.point ?? 0) < 50) {
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
</style>
