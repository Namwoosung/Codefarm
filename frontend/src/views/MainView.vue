<template>
  <div class="min-h-screen p-10">
    <div class="max-w-7xl mx-auto">
      <div class="text-center mb-10">
        <h1 class="text-3xl font-bold text-farm-brown-dark mb-2">CODE FARM 문제 목록</h1>
        <p class="text-farm-brown">
          문제를 선택하면 IDE 화면으로 이동해 풀 수 있어요.
        </p>
      </div>
 
      <!-- 필터 / 정렬 UI -->
      <div class="mb-6 flex flex-wrap items-center gap-3 ">
        <!-- 문제 유형 -->
        <div class="relative" data-filter-dropdown>
          <button
            type="button"
            class="btn btn-sm h-10 min-h-10 rounded-3xl border-farm-brown/30 bg-white px-4 text-sm font-semibold text-farm-brown-dark shadow-sm hover:bg-farm-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30"
            @click="toggleDropdown('algorithm')"
          >
            <span class="flex w-full items-center justify-between gap-3">
              <span class="flex items-center gap-2 truncate">
                <span class="truncate">문제유형</span>
                <span
                  v-if="algorithmSelected.length"
                  class="badge badge-sm border-farm-brown/20 bg-farm-paper text-farm-brown-dark"
                >
                  {{ algorithmSelected.length }}
                </span>
              </span>
              <span
                class="text-farm-brown-dark/60 transition-transform"
                :class="openDropdown === 'algorithm' ? 'rotate-180' : ''"
              >
                ▾
              </span>
            </span>
          </button>

          <div
            v-if="openDropdown === 'algorithm'"
            class="absolute left-0 z-20 mt-2 w-80 rounded-xl border border-farm-brown/25 bg-white p-3 shadow-xl"
          >
            <div class="mb-2 flex items-center justify-between">
              <div class="text-xs font-bold tracking-wide text-farm-brown-dark">문제 유형</div>
              <div class="text-[11px] text-farm-brown/80">복수 선택</div>
            </div>
            <div class="grid grid-cols-2 gap-1.5">
              <label
                v-for="a in algorithmOptions"
                :key="a"
                class="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1.5 text-xs font-medium text-farm-brown-dark hover:bg-farm-paper"
              >
                <input
                  v-model="algorithmSelected"
                  type="checkbox"
                  class="checkbox checkbox-sm border-farm-brown/40 [--chkbg:theme(colors.farm.brown.dark)] [--chkfg:white]"
                  :value="a"
                />
                <span class="truncate">{{ a }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 난이도 -->
        <div class="relative" data-filter-dropdown>
          <button
            type="button"
            class="btn btn-sm h-10 min-h-10 rounded-3xl border-farm-brown/30 bg-white px-4 text-sm font-semibold text-farm-brown-dark shadow-sm hover:bg-farm-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30"
            @click="toggleDropdown('difficulty')"
          >
            <span class="flex w-full items-center justify-between gap-3">
              <span class="flex items-center gap-2 truncate">
                <span class="truncate">난이도</span>
                <span
                  v-if="difficultySelected.length"
                  class="badge badge-sm border-farm-brown/20 bg-farm-paper text-farm-brown-dark"
                >
                  {{ difficultySelected.length }}
                </span>
              </span>
              <span
                class="text-farm-brown-dark/60 transition-transform"
                :class="openDropdown === 'difficulty' ? 'rotate-180' : ''"
              >
                ▾
              </span>
            </span>
          </button>

          <div
            v-if="openDropdown === 'difficulty'"
            class="absolute left-0 z-20 mt-2 w-72 rounded-xl border border-farm-brown/25 bg-white p-3 shadow-xl"
          >
            <div class="mb-2 flex items-center justify-between">
              <div class="text-xs font-bold tracking-wide text-farm-brown-dark">난이도</div>
              <div class="text-[11px] text-farm-brown/80">복수 선택</div>
            </div>
            <div class="grid grid-cols-3 gap-1.5">
              <label
                v-for="d in difficultyOptions"
                :key="d"
                class="flex cursor-pointer items-center gap-2 rounded-lg px-2 py-1.5 text-xs font-medium text-farm-brown-dark hover:bg-farm-paper"
              >
                <input
                  v-model="difficultySelected"
                  type="checkbox"
                  class="checkbox checkbox-sm border-farm-brown/40 [--chkbg:theme(colors.farm.brown.dark)] [--chkfg:white]"
                  :value="d"
                />
                <span>Lv.{{ d }}</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 초기화 -->
        <button
          class="btn btn-sm h-10 min-h-10 ml-auto rounded-3xl border-farm-brown/30 bg-white px-4 text-sm font-semibold text-farm-brown-dark shadow-sm hover:bg-farm-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30"
          @click="resetFilters"
          type="button"
        >
          초기화
        </button>
      </div>
      <!-- 에러 -->
      <div v-if="error" class="mb-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
        {{ error }}
      </div>

      <!-- 문제 카드 리스트 (로딩 시에도 유지 + 오버레이만 표시) -->
      <div class="relative" :aria-busy="loading ? 'true' : 'false'">
        <div
          class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 transition-opacity"
          :class="loading ? 'opacity-50 pointer-events-none' : 'opacity-100'"
        >
          <router-link
            v-for="problem in problems"
            :key="problem.problemId ?? problem.id"
            :to="`/ide/${problem.problemId ?? problem.id}`"
            class="block bg-farm-paper border-4 border-farm-brown rounded-2xl p-6 hover:shadow-lg transition-shadow"
          >
            <div class="mb-3 flex items-center justify-between text-sm text-farm-brown-dark">
              <span class="inline-flex items-center gap-1">
                <span class="px-3 py-1 bg-farm-cream rounded-full text-xs font-semibold">
                  Lv.{{ problem.difficulty }}
                </span>
                <span class="font-medium">#{{ problem.algorithm }}</span>
              </span>
              <span class="text-xs text-farm-brown/70">ID: {{ problem.problemId ?? problem.id }}</span>
            </div>
            <h2 class="text-xl font-bold text-farm-brown-dark">
              {{ problem.title }}
            </h2>
          </router-link>
        </div>

        <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
          <span class="loading loading-spinner loading-lg text-farm-brown-dark"></span>
        </div>

        <div v-if="!loading && !error && problems.length === 0" class="py-16 text-center text-farm-brown/80">
          조건에 맞는 문제가 없어요.
        </div>
      </div>
      <!-- 페이지네이션 -->
      <nav
        v-if="totalPages > 1"
        class="mt-10 rounded-2xl px-4 py-4"
        aria-label="Pagination"
      >
        <div class="flex items-center justify-between gap-4">
          <!-- Previous -->
          <button
            type="button"
            class="h-10 rounded-xl bg-transparent px-3 text-sm font-semibold text-farm-brown-dark transition-colors hover:bg-transparent hover:text-farm-brown-dark/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30 disabled:cursor-not-allowed disabled:text-farm-brown/30"
            :disabled="loading || currentPage <= 1"
            @click="back"
          >
            이전
          </button>

          <!-- Page numbers -->
          <div class="flex items-center justify-center gap-2 text-sm">
            <template v-for="item in paginationItems" :key="item.key">
              <span v-if="item.type === 'ellipsis'" class="px-2 text-farm-brown/50">…</span>
              <button
                v-else
                type="button"
                class="min-w-8 rounded-lg px-2 py-2 text-sm font-semibold transition-colors"
                :class="
                  item.page === currentPage
                    ? 'text-farm-brown-dark'
                    : 'text-farm-brown/60 hover:text-farm-brown-dark'
                "
                :disabled="loading"
                @click="goToPage(item.page)"
              >
                <span
                  class="inline-block px-1 pb-1"
                  :class="item.page === currentPage ? 'border-b-2 border-farm-brown-dark' : 'border-b-2 border-transparent'"
                >
                  {{ item.page }}
                </span>
              </button>
            </template>
          </div>

          <!-- Next -->
          <button
            type="button"
            class="h-10 rounded-xl bg-transparent px-3 text-sm font-semibold text-farm-brown-dark transition-colors hover:bg-transparent hover:text-farm-brown-dark/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30 disabled:cursor-not-allowed disabled:text-farm-brown/30"
            :disabled="loading || currentPage >= totalPages"
            @click="next"
          >
            다음
          </button>
        </div>
      </nav>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { getProblemList } from '@/api/problem'

// 원본(전체) 문제 목록 + 화면에 보여줄(필터/페이지 적용) 목록
const problems = ref([])
const loading = ref(true)
const error = ref(null)
const currentPage = ref(1)
const postsPerPage = ref(21)
const totalPages = ref(10)

// 필터/정렬 상태
const sortBy = ref('createdAt') // UI는 제거됐지만, 파라미터는 통합 관리
const difficultySelected = ref([]) // ['LEVEL1','LEVEL2', ...]
const algorithmSelected = ref([]) // ['완전탐색','그래프', ...]

// 옵션 (필요 시 여기만 수정)
const difficultyOptions = ['1', '2', '3', '4', '5']
const algorithmOptions = [
  "BRUTEFORCE",
  "QUEUE",
  "STACK",
]

const buildQueryParams = () => ({
  size: postsPerPage.value,
  // 백엔드는 0-based page 사용 (PageRequest.of(page, ...))
  page: Math.max(0, currentPage.value - 1),
  sortBy: sortBy.value || undefined,
  algorithm: algorithmSelected.value.length ? algorithmSelected.value.join(',') : undefined,
  difficulty: difficultySelected.value.length ? difficultySelected.value.join(',') : undefined,
})

// 드롭다운 상태
const openDropdown = ref(null) // 'algorithm' | 'difficulty' | null
const toggleDropdown = (key) => {
  openDropdown.value = openDropdown.value === key ? null : key
}

const handleOutsideClick = (e) => {
  if (!openDropdown.value) return
  const target = e?.target
  if (!(target instanceof Element)) return
  if (!target.closest('[data-filter-dropdown]')) {
    openDropdown.value = null
  }
}

const handleEscape = (e) => {
  if (e?.key === 'Escape') openDropdown.value = null
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  document.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleEscape)
})

const fetchProblems = async () => {
  try {
    loading.value = true
    error.value = null
    const { data, total } = await getProblemList(buildQueryParams())
    problems.value = data ?? []
    const safeTotal = Number.isFinite(Number(total)) ? Number(total) : (data?.length ?? 0)
    totalPages.value = Math.max(1, Math.ceil(safeTotal / postsPerPage.value))
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '문제 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  sortBy.value = 'createdAt'
  difficultySelected.value = []
  algorithmSelected.value = []
  currentPage.value = 1
}

// 단일 Watcher: 페이지/필터/정렬을 한 곳에서만 감시해서 중복 호출 방지
let fetchTimer = null
const scheduleFetch = (delayMs = 0) => {
  if (fetchTimer) clearTimeout(fetchTimer)
  if (delayMs > 0) {
    fetchTimer = setTimeout(() => {
      fetchProblems()
    }, delayMs)
  } else {
    fetchProblems()
  }
}

const normalizeArrayKey = (arr) => (Array.isArray(arr) ? [...arr].map(String).sort().join('|') : '')

const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const back = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    scrollToTop()
  }
}

const next = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    scrollToTop()
  }
}

const goToPage = (page) => {
  if (loading.value) return
  const p = Number(page)
  if (!Number.isFinite(p)) return
  const clamped = Math.min(Math.max(1, p), totalPages.value)
  if (clamped === currentPage.value) return
  currentPage.value = clamped
  scrollToTop()
}

const paginationItems = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const items = []

  const pushPage = (p) => items.push({ type: 'page', page: p, key: `p-${p}` })
  const pushEllipsis = (k) => items.push({ type: 'ellipsis', key: `e-${k}` })

  if (total <= 9) {
    for (let p = 1; p <= total; p += 1) pushPage(p)
    return items
  }

  pushPage(1)

  const left = Math.max(2, current - 1)
  const right = Math.min(total - 1, current + 1)

  if (left > 2) pushEllipsis('l')
  for (let p = left; p <= right; p += 1) pushPage(p)
  if (right < total - 1) pushEllipsis('r')

  pushPage(total)
  return items
})

watch(
  () => ({
    page: currentPage.value,
    size: postsPerPage.value,
    sortBy: sortBy.value,
    difficultyKey: normalizeArrayKey(difficultySelected.value),
    algorithmKey: normalizeArrayKey(algorithmSelected.value),
  }),
  (next, prev) => {
    const criteriaChanged =
      !prev ||
      next.size !== prev.size ||
      next.sortBy !== prev.sortBy ||
      next.difficultyKey !== prev.difficultyKey ||
      next.algorithmKey !== prev.algorithmKey

    // 필터/정렬(또는 size)이 바뀌면 페이지를 1로 돌리되, fetch는 한 번만
    if (criteriaChanged && next.page !== 1) {
      currentPage.value = 1
      return
    }

    // 필터/정렬 변경은 디바운스, 페이징은 즉시
    scheduleFetch(criteriaChanged ? 200 : 0)
  },
  { immediate: true }
)

onBeforeUnmount(() => {
  if (fetchTimer) clearTimeout(fetchTimer)
})
</script>
