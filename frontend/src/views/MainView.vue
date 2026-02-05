<template>
  <div class="min-h-screen bg-farm-cream">
    <!-- 최상단 배너 -->
    <MainHeroBanner :top3="top3" />
    <main class="px-4 py-8 sm:px-6 lg:px-8">
    <!-- 30분 무입력 강제 종료 후 메인 진입 시 안내 모달 (X로 닫기) -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showIdleCancelModal" class="fixed inset-0 flex items-center justify-center bg-farm-brown-dark/30 backdrop-blur-sm z-[9999]">
          <div class="bg-farm-paper shadow-2xl rounded-2xl p-6 min-w-[320px] max-w-[90vw] border border-farm-brown/20 relative">
            <button
              type="button"
              class="absolute top-3 right-3 p-1.5 rounded-lg text-farm-brown/70 hover:bg-farm-cream hover:text-farm-brown-dark transition-colors"
              aria-label="닫기"
              @click="closeIdleCancelModal"
            >
              <iconify-icon icon="mdi:close" class="text-xl"></iconify-icon>
            </button>
            <p class="text-base font-medium text-farm-brown-dark pr-10">문제를 장시간동안 풀지 않아 자동으로 문제풀기가 취소되었습니다.</p>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- 풀고 있는 문제가 있을 때 다른 문제 클릭 시 확인 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showActiveSessionModal && activeSessionPayload" class="fixed inset-0 flex items-center justify-center bg-farm-brown-dark/30 backdrop-blur-sm z-[9999]">
          <div class="bg-farm-paper shadow-2xl rounded-2xl p-6 min-w-[320px] max-w-[90vw] border border-farm-brown/20">
            <p class="text-base font-medium text-farm-brown-dark mb-5">
              풀고 있는 문제가 있습니다. (현재 {{ activeSessionPayload.otherProblemId }}번 문제)
            </p>
            <div class="flex justify-end gap-2">
              <button
                type="button"
                class="px-4 py-2 rounded-xl text-sm font-medium text-farm-brown-dark border border-farm-brown/30 hover:bg-farm-cream transition-colors"
                @click="goToExistingProblem"
              >
                기존 문제로
              </button>
              <button
                type="button"
                class="px-4 py-2 rounded-xl text-sm font-medium text-farm-paper bg-farm-green hover:bg-farm-green-dark disabled:opacity-50 transition-colors"
                :disabled="activeSessionLoading"
                @click="goToNewProblem"
              >
                {{ activeSessionLoading ? '처리 중...' : '이 문제로 풀기' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <div class="max-w-6xl mx-auto">
      <!-- 필터 / 정렬 UI -->
      <div class="mb-6 flex flex-wrap items-center gap-3">
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

        <!-- 풀이 상태 필터: 해결 / 미해결 / 도전중 -->
        <div class="flex items-center gap-1.5 rounded-3xl border border-farm-brown/25 bg-white p-1 shadow-sm">
          <button
            v-for="opt in statusFilterOptions"
            :key="opt.value"
            type="button"
            class="rounded-2xl px-3 py-1.5 text-xs font-semibold transition-colors"
            :class="statusFilter === opt.value
              ? 'bg-farm-brown text-white'
              : 'text-farm-brown-dark/70 hover:bg-farm-paper hover:text-farm-brown-dark'"
            @click="statusFilter = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>

        <!-- 초기화 -->
        <button
          class="btn btn-sm h-10 min-h-10 ml-auto rounded-3xl border-farm-brown/30 bg-white ms-auto text-sm font-semibold text-farm-brown-dark shadow-sm hover:bg-farm-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30"
          @click="resetFilters"
          type="button"
        >
          초기화
        </button>
      </div>

      <!-- 구분선 -->
      <hr class="my-6 border-0 h-px bg-gradient-to-r from-transparent via-farm-brown/20 to-transparent" />
      <!-- 에러 -->
      <div v-if="error" class="mb-6 rounded-xl border border-farm-point/40 bg-farm-point/10 px-4 py-3 text-sm text-farm-point">
        {{ error }}
      </div>

      <!-- 문제 카드 리스트 -->
      <div class="relative" :aria-busy="isCurrentPageLoading ? 'true' : 'false'">
        <div
          class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-5 transition-opacity"
          :class="isCurrentPageLoading ? 'opacity-50 pointer-events-none' : 'opacity-100'"
        >
          <ProblemCard
            v-for="problem in pagedProblems"
            :key="problem.problemId ?? problem.id"
            :problem="problem"
            @click="onClickProblem"
          />
        </div>

        <div v-if="isCurrentPageLoading" class="absolute inset-0 flex items-center justify-center">
          <span class="loading loading-spinner loading-lg app-loading-spinner"></span>
        </div>

        <div v-if="!loading && !error && pagedProblems.length === 0" class="py-20 text-center">
          <p class="text-farm-brown/70 text-sm">조건에 맞는 문제가 없어요.</p>
          <button type="button" class="mt-3 text-sm font-medium text-farm-point hover:underline" @click="resetFilters">
            필터 초기화
          </button>
        </div>

        <!-- 추가 데이터 로딩 중 표시 -->
        <div v-if="loadingMore" class="mt-4 text-center">
          <span class="text-xs text-farm-brown/60">추가 데이터 로딩 중...</span>
        </div>
      </div>
      <!-- 페이지네이션 -->
      <nav
        v-if="totalPages > 1"
        class="mt-12 pt-6 border-t border-farm-brown/10"
        aria-label="Pagination"
      >
        <div class="flex items-center justify-between gap-4">
          <!-- Previous -->
          <button
            type="button"
            class="h-10 rounded-xl bg-transparent px-3 text-sm font-semibold text-farm-brown-dark transition-colors hover:bg-transparent hover:text-farm-brown-dark/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-farm-brown/30 disabled:cursor-not-allowed disabled:text-farm-brown/30"
            :disabled="isCurrentPageLoading || currentPage <= 1"
            @click="back"
          >
            이전
          </button>

          <!-- Page numbers -->
          <div class="flex items-center justify-center gap-2 text-sm">
            <template v-for="item in paginationItems" :key="item.key">
              <button
                type="button"
                class="min-w-8 rounded-lg px-2 py-2 text-sm font-semibold transition-colors"
                :class="
                  item.page === currentPage
                    ? 'text-farm-brown-dark'
                    : 'text-farm-brown/60 hover:text-farm-brown-dark'
                "
                :disabled="isCurrentPageLoading"
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
            :disabled="isCurrentPageLoading || currentPage >= totalPages"
            @click="next"
          >
            다음
          </button>
        </div>
      </nav>
    </div>
    </main>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProblemList } from '@/api/problem'
import { useCardStore } from '@/stores/card'
import MainHeroBanner from '@/components/organisms/MainHeroBanner.vue'
import ProblemCard from '@/components/organisms/ProblemCard.vue'
onMounted(() => {
  cardStore.ranking()
})
const cardStore = useCardStore()
const rankingList = computed(() => cardStore.rankingList)
const top3 = computed(() => (rankingList.value ?? []).slice(0, 3))
import * as sessionApi from '@/api/session'

const route = useRoute()
const router = useRouter()
const allProblems = ref([]) // 전체 문제 목록 (API에서 가져온 원본)
const loading = ref(true) // 초기 로딩 (첫 페이지)
const loadingMore = ref(false) // 추가 데이터 로딩 중
const error = ref(null)
const totalFromServer = ref(0) // 서버에서 알려준 전체 개수
const currentPage = ref(1)
const postsPerPage = ref(21)

// idle cancel 모달 (30분 무입력 강제 종료 안내)
const showIdleCancelModal = computed(() => route.query.idle_cancel === '1')

/** 풀고 있는 문제가 있을 때 다른 문제 클릭 시 모달 */
const showActiveSessionModal = ref(false)
/** { otherSessionId, otherProblemId, targetProblemId } */
const activeSessionPayload = ref(null)
const activeSessionLoading = ref(false)

function closeIdleCancelModal() {
  router.replace({ path: '/', query: {} })
}

// 필터/정렬 상태
const sortBy = ref('difficulty')
const difficultySelected = ref([])
const algorithmSelected = ref([])
const statusFilter = ref('') // '' | 'solved' | 'unsolved' | 'tried'

const statusFilterOptions = [
  { value: '', label: '전체' },
  { value: 'solved', label: '해결' },
  { value: 'unsolved', label: '미해결' },
  { value: 'tried', label: '도전중' },
]

// 옵션 (필요 시 여기만 수정)
const difficultyOptions = ['1', '2', '3', '4', '5']
const algorithmOptions = [
  "BRUTEFORCE",
  "QUEUE",
  "STACK",
]

const API_PAGE_SIZE = 100 // 백엔드 최대 size 제한

const buildQueryParams = (page = 0) => ({
  size: API_PAGE_SIZE,
  page,
  sortBy: sortBy.value || undefined,
  algorithm: algorithmSelected.value.length ? algorithmSelected.value.join(',') : undefined,
  difficulty: difficultySelected.value.length ? difficultySelected.value.join(',') : undefined,
  problemType: 'NORMAL',
})

// 클라이언트 측 필터링 (NORMAL 타입 + statusFilter)
const filteredProblems = computed(() => {
  const list = allProblems.value ?? []
  // 1. NORMAL 타입만 필터링
  const normalOnly = list.filter((p) => (p?.problemType ?? p?.problem_type ?? 'NORMAL') === 'NORMAL')
  // 2. statusFilter 적용
  const status = statusFilter.value
  if (!status) return normalOnly
  if (status === 'solved') return normalOnly.filter((p) => p?.userStatus?.isSolved)
  if (status === 'unsolved') return normalOnly.filter((p) => !p?.userStatus?.isSolved && !p?.userStatus?.isTried)
  if (status === 'tried') return normalOnly.filter((p) => p?.userStatus?.isTried && !p?.userStatus?.isSolved)
  return normalOnly
})

// 전체 페이지 수 계산 (statusFilter가 없으면 서버 total 기준, 있으면 필터링된 개수 기준)
const totalPages = computed(() => {
  if (!statusFilter.value && totalFromServer.value > 0) {
    return Math.max(1, Math.ceil(totalFromServer.value / postsPerPage.value))
  }
  return Math.max(1, Math.ceil(filteredProblems.value.length / postsPerPage.value))
})

// 현재 페이지에 표시할 문제 목록 (21개씩)
const pagedProblems = computed(() => {
  const perPage = postsPerPage.value
  const start = (currentPage.value - 1) * perPage
  return filteredProblems.value.slice(start, start + perPage)
})

// 현재 페이지 데이터가 아직 로드 중인지 확인
const isCurrentPageLoading = computed(() => {
  if (loading.value) return true
  if (!loadingMore.value) return false
  return pagedProblems.value.length === 0
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

async function onClickProblem(problem) {
  const problemId = Number(problem.problemId ?? problem.id)
  if (!problemId) return
  try {
    const { data: res } = await sessionApi.getActiveSession()
    const session = res?.data
    if (session && session.problemId !== problemId) {
      activeSessionPayload.value = {
        otherSessionId: session.sessionId,
        otherProblemId: session.problemId,
        targetProblemId: problemId,
      }
      showActiveSessionModal.value = true
      return
    }
  } catch (_) {
    // 404 등 = 활성 세션 없음 → 그대로 이동
  }
  try {
    sessionStorage.setItem(MAIN_SCROLL_STORAGE_KEY, String(window.scrollY))
  } catch (_) {}
  router.push(`/ide/${problemId}`)
}

function goToExistingProblem() {
  const payload = activeSessionPayload.value
  if (!payload) return
  showActiveSessionModal.value = false
  activeSessionPayload.value = null
  try {
    sessionStorage.setItem(MAIN_SCROLL_STORAGE_KEY, String(window.scrollY))
  } catch (_) {}
  router.push(`/ide/${payload.otherProblemId}`)
}

async function goToNewProblem() {
  const payload = activeSessionPayload.value
  if (!payload || activeSessionLoading.value) return
  activeSessionLoading.value = true
  try {
    await sessionApi.closeSession(payload.otherSessionId)
  } catch (_) {}
  showActiveSessionModal.value = false
  activeSessionPayload.value = null
  activeSessionLoading.value = false
  try {
    sessionStorage.setItem(MAIN_SCROLL_STORAGE_KEY, String(window.scrollY))
  } catch (_) {}
  router.push(`/ide/${payload.targetProblemId}`)
}

// 점진적 로딩: 첫 페이지 빠르게 표시 → 나머지 백그라운드 로드
const fetchProblems = async () => {
  try {
    loading.value = true
    loadingMore.value = false
    error.value = null
    allProblems.value = []
    
    // 1. 첫 페이지 호출 → 빠르게 화면 표시
    const firstResult = await getProblemList(buildQueryParams(0))
    const firstData = firstResult.data ?? []
    const total = firstResult.total ?? firstData.length
    
    totalFromServer.value = total
    allProblems.value = firstData
    loading.value = false // 첫 페이지 로딩 완료 → 화면 표시
    
    // 2. 추가 페이지가 필요하면 백그라운드에서 로드
    const totalApiPages = Math.ceil(total / API_PAGE_SIZE)
    
    if (totalApiPages > 1) {
      loadingMore.value = true
      
      // 나머지 페이지 병렬 호출 (백그라운드)
      const promises = []
      for (let page = 1; page < totalApiPages; page++) {
        promises.push(getProblemList(buildQueryParams(page)))
      }
      const results = await Promise.all(promises)
      
      // 결과 합치기
      const allData = [...firstData]
      for (const result of results) {
        allData.push(...(result.data ?? []))
      }
      allProblems.value = allData
      loadingMore.value = false
    }
    
    // totalPages는 computed이므로 다음 tick에 갱신됨. 현재 페이지가 새 total 초과면 보정
    nextTick(() => {
      if (currentPage.value > totalPages.value) {
        currentPage.value = totalPages.value
      }
    })
  } catch (e) {
    error.value = e.response?.data?.message || e.message || '문제 목록을 불러오지 못했습니다.'
    loading.value = false
    loadingMore.value = false
  }
}

const resetFilters = () => {
  sortBy.value = 'createdAt'
  difficultySelected.value = []
  algorithmSelected.value = []
  statusFilter.value = ''
  currentPage.value = 1
  syncPageToRoute(1)
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
    syncPageToRoute(currentPage.value)
    scrollToTop()
  }
}

const next = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    syncPageToRoute(currentPage.value)
    scrollToTop()
  }
}

const goToPage = (page) => {
  if (isCurrentPageLoading.value) return
  const p = Number(page)
  if (!Number.isFinite(p)) return
  const clamped = Math.min(Math.max(1, p), totalPages.value)
  if (clamped === currentPage.value) return
  currentPage.value = clamped
  syncPageToRoute(clamped)
  scrollToTop()
}

const paginationItems = computed(() => {
  const total = totalPages.value
  const current = currentPage.value
  const items = []

  const pushPage = (p) => items.push({ type: 'page', page: p, key: `p-${p}` })

  // 5쪽씩 묶어서 표시. 현재 페이지가 속한 구간의 5개만 표시 (1~5, 6~10, …)
  const startPage = Math.floor((current - 1) / 5) * 5 + 1
  const endPage = Math.min(startPage + 4, total)

  for (let p = startPage; p <= endPage; p += 1) {
    pushPage(p)
  }

  return items
})

// 메인(/)으로 복귀 시(뒤로가기·메인으로 버튼 등) URL 또는 sessionStorage로 페이지 복원
watch(
  () => (route.path === '/' ? route.query.page : undefined),
  (pageQuery) => {
    if (route.path !== '/') return
    const fromQuery = pageQuery != null ? parseInt(pageQuery, 10) : null
    const p =
      fromQuery != null && Number.isFinite(fromQuery)
        ? Math.max(1, fromQuery)
        : (() => {
            try {
              const v = parseInt(sessionStorage.getItem(MAIN_PAGE_STORAGE_KEY), 10)
              return Number.isFinite(v) && v >= 1 ? v : 1
            } catch (_) {
              return 1
            }
          })()
    if (p !== currentPage.value) {
      currentPage.value = p
      try {
        sessionStorage.setItem(MAIN_PAGE_STORAGE_KEY, String(p))
      } catch (_) {}
      if (pageQuery == null && p > 1) syncPageToRoute(p)
    }
  },
  { immediate: true }
)

watch(
  () => ({
    sortBy: sortBy.value,
    difficultyKey: normalizeArrayKey(difficultySelected.value),
    algorithmKey: normalizeArrayKey(algorithmSelected.value),
  }),
  (next, prev) => {
    // prev 없음 = 최초 1회 실행. 이때는 페이지 리셋하면 안 됨(URL/sessionStorage 복원값이 덮어씌워짐)
    const criteriaChanged =
      !prev ||
      next.sortBy !== prev.sortBy ||
      next.difficultyKey !== prev.difficultyKey ||
      next.algorithmKey !== prev.algorithmKey

    if (criteriaChanged) {
      currentPage.value = 1
      scheduleFetch(200)
    }
  },
  { immediate: true }
)

// statusFilter 변경 시 페이지만 리셋 (API 호출 불필요)
watch(statusFilter, () => {
  currentPage.value = 1
})

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
  document.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
  document.removeEventListener('keydown', handleEscape)
  if (fetchTimer) clearTimeout(fetchTimer)
})
</script>
