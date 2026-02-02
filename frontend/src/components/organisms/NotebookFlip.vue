<template>
  <div class="w-full h-full">
    <!-- Diary wrapper -->
    <div class="diary h-full">
      <div class="diary__cover">
        <div class="diary__spine" aria-hidden="true"></div>
        <div class="diary__content">
          <!-- Book -->
          <div class="book-shell">
            <div ref="bookEl" class="pageflip" aria-label="다이어리 페이지">
              <div v-for="page in pages" :key="page.key" class="page">
                <div class="paper">
                  <template v-if="page.kind === 'report-list'">
                    <div class="h-full flex flex-col min-h-0">
                      <div class="flex items-start justify-between gap-3">
                        <div>
                          <h2 class="text-lg font-black text-farm-brown-dark">리포트 목록</h2>
                          <p class="mt-1 text-xs font-semibold text-farm-brown-dark/70">
                            총 {{ page.totalElements }}개 중 최신 {{ page.rows.length }}개 표시
                          </p>
                        </div>
                      </div>

                      <div class="mt-4 flex-1 min-h-0 overflow-hidden rounded-xl border border-farm-brown/15 bg-farm-paper/70">
                        <div class="h-full overflow-x-auto overflow-y-auto">
                          <table class="table table-pin-rows table-sm">
                            <thead>
                              <tr class="bg-base-100 sticky top-0 z-10">
                                <th class="text-left font-semibold text-[var(--color-farm-brown)]">제출일시</th>
                                <th class="text-left font-semibold text-[var(--color-farm-brown)]">결과</th>
                                <th class="text-left font-semibold text-[var(--color-farm-brown)]">문제</th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr
                                v-for="(row, idx) in page.rows"
                                :key="row?.resultId ?? idx"
                                class="hover:bg-base-200/50"
                              >
                                <td class="py-2">
                                  <span class="px-1.5 mr-1">{{ formatCreatedDate(row?.createdAt) }}</span>
                                  <span
                                    class="status status-sm align-middle"
                                    :class="resultStatusClass(row?.resultType)"
                                    :title="resultTypeLabel(row?.resultType)"
                                    aria-hidden="true"
                                  ></span>
                                </td>
                                <td>
                                  <button
                                    type="button"
                                    class="btn btn-xs bg-farm-olive text-farm-paper hover:brightness-110 active:brightness-95"
                                    :disabled="row?.resultId == null"
                                    @click.stop="row?.resultId != null ? openReportModal(row.resultId) : null"
                                  >
                                    보기
                                  </button>
                                </td>
                                <td class="max-w-[320px] truncate">
                                  {{ row?.problem?.title ?? '-' }}
                                </td>
                              </tr>
                              <tr v-if="page.rows.length === 0">
                                <td colspan="3" class="text-center text-[var(--color-farm-brown)] py-10">
                                  리포트가 없습니다.
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>
                    </div>
                  </template>
                  <template v-else-if="page.kind === 'info'">
                    <h1 class="text-xl font-black text-farm-brown-dark">내 정보</h1>
                    <div class="mt-4 space-y-2 text-sm text-farm-brown-dark/85 font-semibold">
                      <p>해결한 문제 수 : <span class="font-black">{{ solvedCount }}</span></p>
                      <p>보유한 카드 수 : <span class="font-black">{{ cardCount }}</span></p>
                    </div>
                    <p class="mt-6 text-sm text-farm-brown-dark/70">
                      다음 페이지에서 리포트 목록을 확인할 수 있어요.
                    </p>
                  </template>
                  <template v-else-if="page.kind === 'report'">
                    <div class="flex items-start justify-between gap-3">
                      <h2 class="text-lg font-black text-farm-brown-dark">
                        {{ page.report?.problem?.title ?? '리포트' }}
                      </h2>
                      <span class="text-xs font-black text-farm-brown-dark/70">
                        #{{ page.report?.resultId }}
                      </span>
                    </div>

                    <div class="mt-3 space-y-1.5 text-sm text-farm-brown-dark/85 font-semibold">
                      <p>
                        결과: <span class="font-black">{{ page.report?.resultType }}</span>
                      </p>
                      <p>
                        언어: <span class="font-black">{{ page.report?.language }}</span>
                      </p>
                      <p v-if="page.report?.solveTime != null">
                        풀이 시간: <span class="font-black">{{ page.report.solveTime }}s</span>
                      </p>
                      <p v-if="page.report?.execTime != null">
                        실행 시간: <span class="font-black">{{ page.report.execTime }}ms</span>
                      </p>
                      <p v-if="page.report?.createdAt">
                        제출: <span class="font-black">{{ page.report.createdAt }}</span>
                      </p>
                    </div>

                    <div v-if="page.report?.feedback" class="mt-4 rounded-xl border border-farm-brown/15 bg-farm-cream/40 p-3">
                      <p class="text-sm font-black text-farm-brown-dark mb-1">피드백</p>
                      <p class="text-sm text-farm-brown-dark/80 leading-relaxed">
                        {{ page.report.feedback }}
                      </p>
                    </div>
                  </template>
                  <template v-else>
                    <h2 class="text-lg font-bold text-farm-brown-dark">{{ page.title }}</h2>
                    <p class="mt-2 text-sm text-farm-brown-dark/80 leading-relaxed">
                      {{ page.body }}
                    </p>
                  </template>
                </div>
              </div>
            </div>
          </div>

          <ReportModal
            :show="showReportModal"
            :report="reportModalData"
            :report-loading="reportModalLoading"
            :report-load-failed="reportModalLoadFailed"
            @close="onReportModalClose"
          />

          <!-- Index tabs (붙어있는 다이어리 인덱스) -->
          <div class="diary__index" aria-label="다이어리 인덱스">
            <button
              v-for="(tab, idx) in tabs"
              :key="tab.key"
              class="diary__tab"
              :class="{ 'is-active': activeTabIndex === idx }"
              type="button"
              :style="{ top: `${idx * 52 + 18}px` }"
              @click="goToTab(idx)"
            >
              <span class="diary__tabLabel">{{ tab.label }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { PageFlip } from 'page-flip'
import { useProfileStore } from '@/stores/profile'
import { useCardStore } from '@/stores/card'
import ReportModal from '@/components/organisms/ReportModal.vue'
import { getReportDetail } from '@/api/reports'

// 리포트 조회
const profile = useProfileStore()
const cardStore = useCardStore()
const solvedCount = ref(0)
const cardCount = ref(0)

const showReportModal = ref(false)
const reportModalLoading = ref(false)
const reportModalLoadFailed = ref(false)
const reportModalData = ref(null)

const openReportModal = async (reportId) => {
  if (reportId == null) return
  showReportModal.value = true
  reportModalLoading.value = true
  reportModalLoadFailed.value = false
  reportModalData.value = null
  try {
    const detail = await getReportDetail(reportId)
    reportModalData.value = detail ? { result: detail } : null
    reportModalLoadFailed.value = !detail
  } catch (_) {
    reportModalData.value = null
    reportModalLoadFailed.value = true
  } finally {
    reportModalLoading.value = false
  }
}

const onReportModalClose = () => {
  showReportModal.value = false
  reportModalLoading.value = false
  reportModalLoadFailed.value = false
  reportModalData.value = null
}

const reportResults = computed(() => {
  const list = profile.reports?.results ?? []
  return Array.isArray(list) ? list : []
})

const reportTotalElements = computed(() => {
  const n = Number(profile.reports?.page?.totalElements ?? reportResults.value.length)
  return Number.isFinite(n) && n >= 0 ? n : reportResults.value.length
})

// (기존 로직 유지) 마이페이지에서는 최신 10개까지만 노출
const latestReportResults = computed(() => {
  const list = [...reportResults.value]
  list.sort((a, b) => {
    const at = a?.createdAt ? Date.parse(a.createdAt) : NaN
    const bt = b?.createdAt ? Date.parse(b.createdAt) : NaN
    if (!Number.isFinite(at) && !Number.isFinite(bt)) return 0
    if (!Number.isFinite(at)) return 1
    if (!Number.isFinite(bt)) return -1
    return bt - at
  })
  return list.slice(0, 10)
})

// "목록만 추가": 기존 페이지(내정보/리포트페이지)는 그대로 두고, 목록 페이지를 맨 앞에 추가
const reportListPage = computed(() => ({
  key: 'report-list',
  kind: 'report-list',
  rows: reportResults.value,
  totalElements: reportTotalElements.value,
}))

const reportPages = computed(() => {
  if (latestReportResults.value.length === 0) {
    return [
      {
        key: 'report-empty',
        kind: 'report-empty',
        title: '학습 기록',
        body: '아직 리포트가 없어요. 문제를 풀고 리포트를 만들어보세요!',
      },
    ]
  }

  const pages = latestReportResults.value.map((r) => ({
    key: `report-${r?.resultId ?? Math.random().toString(16).slice(2)}`,
    kind: 'report',
    report: r,
  }))

  if (reportTotalElements.value > latestReportResults.value.length) {
    pages.push({
      key: 'report-more',
      kind: 'report-more',
      title: '리포트 더보기',
      body: '마이페이지에서는 최신 10개만 표시됩니다. 전체 리포트 목록에서 확인해 주세요.',
    })
  }

  return pages
})

// 페이지 인덱스
const infoStartPageIndex = computed(() => 0) // 내정보 페이지
const recordStartPageIndex = computed(() => 1) // 목록 페이지

const getTabIndexForPage = (pageIndex) => {
  // 탭 0: 내 정보, 탭 1: 학습 기록(목록 + 리포트들)
  return pageIndex === infoStartPageIndex.value ? 0 : 1
}

onMounted(async () => {
  // API로 불러온 리포트 목록을 첫 페이지(목록 페이지)에 노출
  await profile.reportList({ page: 0, size: 10, sort: 'createdAt,DESC' })
  await cardStore.cardList()

  solvedCount.value = reportResults.value.filter((report) => report?.resultType === 'SUCCESS').length
  const cardList = cardStore.cards ?? []
  cardCount.value = (Array.isArray(cardList) ? cardList : []).reduce((sum, c) => {
    const n = Number(c?.count ?? 1)
    const cnt = Number.isFinite(n) && n > 0 ? n : 1
    return sum + cnt
  }, 0)

  // 리포트/카드 로딩 후 페이지 수가 바뀌므로 PageFlip에 반영
  await refreshPages()
})

const bookEl = ref(null)
const flip = ref(null)
const activeTabIndex = ref(0)
const isCompact = ref(false)

const BREAKPOINT_PX = 768
const rafId = ref(0)
const mql = ref(null)
const onResize = ref(null)
const onMqlChange = ref(null)

// 탭 1개당 '스프레드(좌/우 2페이지)'로 가정
const tabs = [
  { key: 'info', label: '내 정보' },
  { key: 'record', label: '학습 기록' },
]

// 페이지 목록록
const pages = computed(() => {
  // mobile: 0(목록) -> 1(내정보) -> 리포트 페이지들
  if (isCompact.value) {
    return [
      { key: 'm-info', kind: 'info', title: '내 정보', body: '' },
      reportListPage.value,
      ...reportPages.value,
    ]
  }

  // desktop: 0(내정보) -> 1(목록) -> 리포트 페이지들
  return [
    { key: 'p-info', kind: 'info', title: '내 정보', body: '' },
    reportListPage.value,
    ...reportPages.value,
  ]
})

const getIsCompact = () => window.matchMedia(`(max-width: ${BREAKPOINT_PX}px)`).matches

const syncCompactMode = () => {
  const next = getIsCompact()
  const changed = isCompact.value !== next
  isCompact.value = next
  return changed
}

const scheduleUpdate = () => {
  if (!flip.value) return
  if (rafId.value) cancelAnimationFrame(rafId.value)
  rafId.value = requestAnimationFrame(() => {
    flip.value?.update()
  })
}

const initIfNeeded = async () => {
  await nextTick()
  if (!bookEl.value) return

  if (flip.value) {
    scheduleUpdate()
    return
  }

  const instance = new PageFlip(bookEl.value, {
    width: 400,
    height: 520,
    size: 'stretch',
    minWidth: 320,
    maxWidth: 980,
    minHeight: 400,
    maxHeight: 800,
    maxShadowOpacity: 0.55,
    showCover: false,
    usePortrait: true,
    mobileScrollSupport: false,
    flippingTime: 700,
    useMouseEvents: true,
  })

  const htmlPages = bookEl.value.querySelectorAll('.page')
  instance.loadFromHTML(htmlPages)

  instance.on('flip', (e) => {
    const pageIndex = typeof e?.data === 'number' ? e.data : instance.getCurrentPageIndex()
    activeTabIndex.value = getTabIndexForPage(pageIndex)
  })

  flip.value = instance

  // 0페이지(내 정보)부터 시작
  try {
    instance.turnToPage(0)
  } catch {
    // ignore
  }
}

const refreshPages = async () => {
  // isCompact 변경으로 v-for 페이지 개수가 달라지므로 DOM 패치 완료 후 updateFromHtml
  await nextTick()
  if (!bookEl.value || !flip.value) return

  const htmlPages = bookEl.value.querySelectorAll('.page')
  flip.value.updateFromHtml(htmlPages)
  flip.value.update()

  // 현재 페이지 인덱스가 범위를 벗어나면 클램프
  const maxIndex = Math.max(0, flip.value.getPageCount() - 1)
  const cur = flip.value.getCurrentPageIndex()
  if (cur > maxIndex) {
    flip.value.turnToPage(maxIndex)
  }

  // 0페이지는 "내 정보"이므로 강제 이동 보정은 하지 않음
}

const goToTab = (idx) => {
  activeTabIndex.value = idx
  const pageIndex = idx === 0 ? infoStartPageIndex.value : recordStartPageIndex.value
  if (flip.value) flip.value.flip(pageIndex)
}

const flipNext = () => flip.value?.flipNext()
const flipPrev = () => flip.value?.flipPrev()

onMounted(() => {
  syncCompactMode()
  initIfNeeded()

  // breakpoint 변경(= 모드 변경)은 matchMedia로 감지해서 페이지 목록/탭 매핑을 갱신
  mql.value = window.matchMedia(`(max-width: ${BREAKPOINT_PX}px)`)
  onMqlChange.value = () => {
    const changed = syncCompactMode()
    if (changed) refreshPages()
  }
  // Safari 구버전 fallback
  if (mql.value.addEventListener) mql.value.addEventListener('change', onMqlChange.value)
  else mql.value.addListener(onMqlChange.value)

  // 단순 resize(같은 모드 내)는 update()만 호출해서 접힘 방지
  onResize.value = () => scheduleUpdate()
  window.addEventListener('resize', onResize.value, { passive: true })
})

// 리포트가 늘어나면 페이지 수가 늘어나도록 PageFlip 갱신
watch(
  () => reportResults.value.length,
  async () => {
    await refreshPages()
  }
)

function formatCreatedAt(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

function formatCreatedDate(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

function resultStatusClass(type) {
  if (type === 'SUCCESS') {
    // 더 진한 초록
    return 'status-success saturate-200 brightness-95 shadow-[0_0_10px_rgba(16,185,129,0.95)] ring-1 ring-emerald-300/70'
  }
  if (type === 'GIVE_UP') {
    // 더 어두운 빨강
    return 'status-error saturate-200 brightness-90 shadow-[0_0_10px_rgba(220,38,38,0.95)] ring-1 ring-red-300/70'
  }
  return 'status-neutral opacity-60'
}

function resultTypeLabel(type) {
  const map = { SUCCESS: '정답', FAIL: '오답', GIVE_UP: '탈주' }
  return map[type] ?? type ?? '-'
}

function resultTypeBadgeClass(type) {
  const map = { SUCCESS: 'badge-success text-white', FAIL: 'badge-error text-white', GIVE_UP: 'badge-ghost' }
  return map[type] ?? 'badge-ghost'
}

// 다른 화면에서 리포트가 추가된 뒤, 다시 마이페이지로 돌아오면 최신 목록을 재조회
const refreshLatestReports = async () => {
  try {
    await profile.reportList({ page: 0, size: 10, sort: 'createdAt,DESC' })
  } catch (_) {
    // ignore
  }
}

const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') refreshLatestReports()
}
const onWindowFocus = () => refreshLatestReports()

onMounted(() => {
  document.addEventListener('visibilitychange', onVisibilityChange)
  window.addEventListener('focus', onWindowFocus)
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', onVisibilityChange)
  window.removeEventListener('focus', onWindowFocus)
})

onBeforeUnmount(() => {
  if (rafId.value) cancelAnimationFrame(rafId.value)
  if (onResize.value) window.removeEventListener('resize', onResize.value)

  if (mql.value && onMqlChange.value) {
    if (mql.value.removeEventListener) mql.value.removeEventListener('change', onMqlChange.value)
    else mql.value.removeListener(onMqlChange.value)
  }

  if (flip.value) {
    try {
      flip.value.destroy()
    } catch {
      // ignore
    }
  }
})
</script>

<style scoped>
.diary {
  width: 100%;
  display: flex;
  justify-content: center;
}

.diary__cover {
  position: relative;
  width: min(980px, 100%);
  height: 100%;
  display: flex;
  flex-direction: column;
  border-radius: 28px;
  padding: 18px 20px 20px 20px;
  /* 가죽 커버 텍스처(그라데이션 레이어로 결/주름 느낌) */
  background:
    /* 미세한 세로 결 */
    repeating-linear-gradient(
      90deg,
      rgba(255, 255, 255, 0.04) 0 1px,
      rgba(0, 0, 0, 0.03) 1px 3px,
      rgba(255, 255, 255, 0.02) 3px 4px
    ),
    /* 가죽 하이라이트/음영 */
    radial-gradient(140% 110% at 18% 18%, rgba(255, 255, 255, 0.10), transparent 55%),
    radial-gradient(120% 120% at 88% 82%, rgba(0, 0, 0, 0.28), transparent 60%),
    linear-gradient(145deg, #5b4633 0%, #3f2e22 100%);
  background-size:
    6px 100%,
    100% 100%,
    100% 100%,
    100% 100%;
  background-blend-mode:
    overlay,
    screen,
    multiply,
    normal;
  box-shadow:
    0 16px 40px rgba(0, 0, 0, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.15),
    inset 0 0 0 1px rgba(255, 255, 255, 0.06),
    inset 0 -18px 38px rgba(0, 0, 0, 0.22);
}

.diary__spine {
  position: absolute;
  left: 18px;
  top: 18px;
  bottom: 18px;
  width: 26px;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(0, 0, 0, 0.25), rgba(255, 255, 255, 0.08));
  box-shadow:
    inset -2px 0 0 rgba(0, 0, 0, 0.25),
    inset 2px 0 0 rgba(255, 255, 255, 0.06);
}

.diary__title {
  display: flex;
  align-items: baseline;
  gap: 10px;
  margin-left: 54px;
  margin-bottom: 14px;
  color: var(--color-farm-paper);
}

.diary__badge {
  font-weight: 800;
  letter-spacing: 0.12em;
  font-size: 12px;
  padding: 7px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.16);
}

.diary__subtitle {
  font-weight: 700;
  font-size: 14px;
  opacity: 0.9;
}

.diary__content {
  position: relative;
  margin-left: 54px;
  border-radius: 22px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.book-shell {
  width: 100%;
  display: flex;
  justify-content: center;
  flex: 1;
  min-height: 0;
}

.pageflip {
  width: min(980px, 100%);
  border-radius: 16px;
  /* 리사이즈 순간 0 높이로 접히는 현상 방지 */
  min-height: 0;
  height: 100%;
}

.page {
  /* StPageFlip이 내부에서 사이즈를 잡지만, 배경/여백을 위해 기본값 */
  background: transparent;
}

.paper {
  height: 100%;
  background: var(--color-farm-paper);
  border: 1px solid rgba(78, 59, 42, 0.15);
  border-radius: 14px;
  padding: 18px;

  /* 종이 질감 느낌 */
  background-image:
    radial-gradient(rgba(78, 59, 42, 0.06) 1px, transparent 1px),
    linear-gradient(transparent, transparent);
  background-size: 18px 18px;
}

.diary__index {
  position: absolute;
  top: 0;
  /* 종이 영역을 침범하지 않도록 커버(나무) 쪽으로 더 빼줌 */
  right: -64px;
  width: 92px;
  height: 100%;
  pointer-events: none; /* 버튼만 포인터 받게 */
  /* 인덱스(테이프) 컬러: 미선택=연한 갈색, 선택=진한 올리브 */
  --tape-inactive: var(--color-farm-brown, #7A5C3E);
  --tape-active: var(--color-farm-olive, #4A4A29);
  --tape-edge: rgba(33, 24, 20, 0.28);
}

.diary__tab {
  position: absolute;
  right: 0;
  pointer-events: auto;
  width: 92px;
  height: 44px;
  /* 기본(미선택) 컬러/라벨 컬러 */
  --tape-base: var(--tape-inactive);
  --tab-label-color: rgba(255, 255, 255, 0.94);
  border-radius: 10px 18px 18px 10px;
  border: 1px solid var(--tape-edge);
  /* 질감 제거: 단색 테이프 */
  background: var(--tape-base);
  box-shadow:
    0 10px 18px rgba(0, 0, 0, 0.18),
    0 2px 0 rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.35);
  /* 기본(비활성)은 바깥쪽으로 더 나가게 */
  --tab-tx: 10px;
  --tab-rot: -0.6deg;
  transform: translateX(var(--tab-tx)) rotate(var(--tab-rot));
  transition: transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease, filter 180ms ease;
  overflow: hidden;

  /* 우측 가운데를 "<" 모양으로 잘라낸 노치 */
  clip-path: polygon(
    0% 0%,
    100% 0%,
    86% 50%,
    100% 100%,
    0% 100%
  );
}

.diary__tab:nth-child(even) {
  --tab-rot: 0.6deg;
}

.diary__tab:hover {
  /* hover 시 위치는 고정, 질감/명암만 살짝 */
  filter: saturate(1.05) brightness(1.02);
  box-shadow:
    0 12px 20px rgba(0, 0, 0, 0.20),
    0 2px 0 rgba(0, 0, 0, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.38);
}

.diary__tab.is-active {
  /* 선택된 탭은 "붙어있는" 느낌을 더 강하게 */
  border-color: rgba(33, 24, 20, 0.34);
  /* 선택된 탭만 안쪽(종이 쪽)으로 들어오게 */
  --tape-base: var(--tape-active);
  --tab-label-color: rgba(255, 255, 255, 0.96);
  --tab-tx: -10px;
  --tab-rot: 0deg;
  box-shadow:
    0 14px 22px rgba(0, 0, 0, 0.22),
    0 4px 0 rgba(0, 0, 0, 0.07),
    inset 0 1px 0 rgba(255, 255, 255, 0.42);
}

.diary__tabLabel {
  display: block;
  text-align: left;
  padding: 10px 12px;
  font-weight: 300;
  font-size: 12px;
  color: var(--tab-label-color);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-shadow: 0 1px 0 rgba(0, 0, 0, 0.18);
}

@media (max-width: 768px) {
  .diary__cover {
    padding: 16px;
  }

  .diary__spine {
    left: 12px;
    width: 18px;
  }

  .diary__title {
    margin-left: 38px;
  }

  .diary__content {
    margin-left: 38px;
    padding: 10px;
  }

  /* 좁은 화면에서는 인덱스를 더 바깥(나무 커버 영역)으로 빼고, 탭 크기도 줄임 */
  .diary__index {
    right: -72px;
    width: 78px;
  }

  .diary__tab {
    width: 78px;
    height: 40px;
  }

  .diary__tabLabel {
    padding: 9px 10px;
    font-size: 11px;
  }
}
</style>

