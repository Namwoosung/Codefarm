<template>
  <div class="h-screen p-10 flex flex-col overflow-hidden">
    <div class="max-w-7xl mx-auto w-full flex flex-col flex-1 min-h-0">
      <PageTitle title="카드" />

      <div class="flex flex-col flex-1 min-h-0">
        <!-- 카드 리스트 -->
        <main class="w-full flex-1 min-h-0">
          <div class="mb-4 h-[calc(100vh-200px)] border-[15px] border-[color:var(--color-farm-brown-dark)] bg-base-100 p-8 rounded-[20px] relative flex flex-col min-h-0 overflow-hidden">
            <!-- 배경 이미지 -->
            <div
              class="absolute inset-0 rounded-[20px] bg-center bg-cover opacity-25 pointer-events-none"
              :style="{ backgroundImage: `url(${cardListBg})` }"
            />

            <div class="relative z-10 flex items-center justify-between gap-3 mb-6">
              <h2 class="text-xl font-bold text-slate-800">{{ user?.nickname }}'s Farm Crew</h2>
              <button
                type="button"
                class="btn rounded-xl border border-base-300 bg-gradient-to-b from-white to-base-200 text-base-content font-bold tracking-tight shadow-sm hover:-translate-y-0.5 active:translate-y-0"
                @click="profile.reportList?.()"
              >
                카드뽑기
              </button>
            </div>

            <!-- 등급별 페이지 스냅 (한 번에 한 등급만 노출) -->
            <div class="relative z-10 flex-1 min-h-0 overflow-y-auto overscroll-contain scrollbar-hide snap-y snap-mandatory scroll-smooth">
              <section v-for="grade in GRADES" :key="grade" class="h-full snap-start relative group flex flex-col justify-center">
                <div class="flex items-center justify-between mb-3 px-2">
                  <h3 class="text-lg font-bold text-slate-700 flex items-center gap-2">
                    <span :class="gradeMeta[grade].color" class="w-2 h-6 rounded-full"></span>
                    {{ grade }}
                  </h3>
                  <span class="text-sm text-slate-400">
                    {{ cardsByGrade[grade].length }} / {{ gradeMeta[grade].slots }}
                  </span>
                </div>

                <!-- 좌우 이동 버튼 -->
                <button
                  v-if="grade !== 'MEGA'"
                  type="button"
                  @click="scroll(grade, 'left')"
                  class="absolute left-0 top-1/2 -translate-y-1/2 z-50 bg-white/90 border border-slate-200 rounded-full p-1.5 shadow-md hover:bg-white transition-opacity md:opacity-0 md:group-hover:opacity-100 flex items-center justify-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                  </svg>
                </button>

                <button
                  v-if="grade !== 'MEGA'"
                  type="button"
                  @click="scroll(grade, 'right')"
                  class="absolute right-0 top-1/2 -translate-y-1/2 z-50 bg-white/90 border border-slate-200 rounded-full p-1.5 shadow-md hover:bg-white transition-opacity md:opacity-0 md:group-hover:opacity-100 flex items-center justify-center"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                  </svg>
                </button>

                <!-- 가로 스크롤 슬롯 -->
                <div
                  :ref="(el) => setScrollEl(grade, el)"
                  class="flex gap-5 overflow-x-auto overflow-y-visible pt-2 pb-4 px-2 scroll-smooth scrollbar-hide snap-x"
                >
                  <!-- 고정 슬롯(카드ID 기준으로 위치 배치) -->
                  <div
                    v-for="(slotCard, idx) in slotsByGrade[grade]"
                    :key="`${grade}-slot-${idx}`"
                    :class="[
                      'flex-shrink-0 snap-start',
                      grade === 'MEGA' ? 'w-[340px]' : 'w-[155px]',
                    ]"
                  >
                    <CardDetail v-if="slotCard" class="w-full" :card="slotCard" @showcard="openCardModal" />
                    <div
                      v-else
                      :class="[
                        'bg-transparent border-2 border-dashed border-base-content/35 rounded-xl shadow-md flex items-center justify-center',
                        'w-full',
                        grade === 'MEGA' ? 'aspect-[1024/723]' : 'aspect-[1872/2613]',
                      ]"
                    >
                      <span class="text-4xl font-extrabold text-base-content/20">?</span>
                    </div>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </main>
      </div>
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
        <div v-if="selectedCard" :class="popupCardContainerClass">
          <img
            :src="selectedCard.image"
            :alt="selectedCard.name"
            class="w-full h-full object-contain block"
            loading="lazy"
          />
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { useProfileStore } from '@/stores/profile'
import { storeToRefs } from 'pinia'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import PageTitle from '@/components/atoms/PageTitle.vue'
import CardDetail from '@/components/organisms/CardDetail.vue'
import cardListBg from '@/assets/cardlist.png'

const profile = useProfileStore()
const { user, cards } = storeToRefs(profile)

const selectedCard = ref(null)
const scrollLockPrev = {
  htmlOverflow: '',
  htmlPaddingRight: '',
  bodyOverflow: '',
}

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

const openCardModal = (card) => {
  selectedCard.value = card
  lockScroll()
}

const closeCardModal = () => {
  selectedCard.value = null
  unlockScroll()
}

const GRADES = ['MEGA', 'GOLD', 'SILVER', 'BRONZE']
const gradeMeta = {
  MEGA: { color: 'bg-purple-500', slots: 1 },
  GOLD: { color: 'bg-yellow-400', slots: 7 },
  SILVER: { color: 'bg-slate-400', slots: 10 },
  BRONZE: { color: 'bg-orange-400', slots: 12 },
}

const normalizeCard = (item) => (item?.card && typeof item.card === 'object' ? item.card : item)

const normalizedCards = computed(() => {
  const raw = cards.value ?? []
  const arr = Array.isArray(raw) ? raw : Object.values(raw)
  return arr.map(normalizeCard).filter(Boolean)
})

const cardsByGrade = computed(() => {
  const grouped = Object.fromEntries(GRADES.map((g) => [g, []]))
  for (const c of normalizedCards.value) {
    if (c?.grade && grouped[c.grade]) grouped[c.grade].push(c)
  }
  return grouped
})

const minCardIdByGrade = computed(() => {
  const mins = Object.fromEntries(GRADES.map((g) => [g, Number.POSITIVE_INFINITY]))
  for (const c of normalizedCards.value) {
    if (!c?.grade || mins[c.grade] === undefined) continue
    const id = Number(c.cardId)
    if (Number.isFinite(id)) mins[c.grade] = Math.min(mins[c.grade], id)
  }
  for (const g of GRADES) if (!Number.isFinite(mins[g])) mins[g] = 1
  return mins
})

const slotsByGrade = computed(() => {
  const result = Object.fromEntries(GRADES.map((g) => [g, Array.from({ length: gradeMeta[g].slots }, () => null)]))
  for (const grade of GRADES) {
    const slots = result[grade]
    const baseId = minCardIdByGrade.value[grade]
    const gradeCards = [...(cardsByGrade.value[grade] ?? [])].sort((a, b) => Number(a.cardId) - Number(b.cardId))
    for (const c of gradeCards) {
      const id = Number(c?.cardId)
      if (!Number.isFinite(id)) continue
      const idx = id - baseId
      if (idx >= 0 && idx < slots.length && slots[idx] == null) {
        slots[idx] = c
        continue
      }
      const fallback = slots.findIndex((v) => v == null)
      if (fallback !== -1) slots[fallback] = c
    }
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
    'bg-transparent rounded-2xl overflow-hidden shadow-2xl ring-1 ring-white/20 shadow-[0_0_60px_rgba(255,255,255,0.35)]'
  const grade = selectedCard.value?.grade
  // 슬롯의 약 2.5배 크기 (MEGA: 320 -> 800, 그 외: 140 -> 350)
  return grade === 'MEGA'
    ? `${base} w-[min(92vw,800px)] aspect-[1024/723]`
    : `${base} w-[min(92vw,350px)] aspect-[1872/2613]`
})

onMounted(async () => {
  try {
    await profile.userinfo()
    await profile.cardList()
  } catch (err) {
    console.warn('[CardView] mounted fetch failed:', err)
  }
})

onBeforeUnmount(() => {
  unlockScroll()
})
</script>
