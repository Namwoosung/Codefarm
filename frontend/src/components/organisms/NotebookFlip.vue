<template>
  <div class="w-full h-full">
    <!-- Diary wrapper -->
    <div class="diary h-full">
      <div class="diary__cover">
        <div class="diary__spine" aria-hidden="true"></div>

        <!-- <div class="diary__title">
          <div class="diary__badge">MY DIARY</div>
          <div class="diary__subtitle">프로필</div>
        </div> -->

        <div class="diary__content">
          <!-- Book -->
          <div class="book-shell">
            <div ref="bookEl" class="pageflip" aria-label="다이어리 페이지">
              <div v-for="page in pages" :key="page.key" class="page">
                <div class="paper">
                  <template v-if="page.key === 'blank0'">
                    <h1>info</h1>
                    <!-- 2페이지 스프레드에서 첫 펼침의 "왼쪽 페이지"를 쓰기 위한 더미 페이지 -->
                  </template>
                  <template v-else-if="page.key === 'p1' || page.key === 'm1'">
                    
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
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { PageFlip } from 'page-flip'

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
  { key: 'info', label: '학습 기록' },
  { key: 'record', label: '학습 기록' },
  // { key: 'settings', label: '설정' },
]

// PageFlip은 넓은 화면에서 2페이지 스프레드가 자연스럽고,
// 좁은 화면(포트레이트 모드)에서는 1페이지씩 넘기는 UX가 자연스럽습니다.
const pages = computed(() => {
  // mobile(1page): 탭 1개당 1페이지
  if (isCompact.value) {
    return [
      { key: 'm1', title: '내 정보', body: '닉네임/레벨/뱃지 등 프로필 정보를 여기에 배치' },
      { key: 'm2', title: '학습 기록', body: '최근 푼 문제, 성공률, streak 등을 타임라인처럼' },
      { key: 'm3', title: '설정', body: '테마, 알림, 계정 관리 등 설정 항목' },
    ]
  }

  // desktop(2page spread):
  // PageFlip(showCover:false)에서는 "첫 펼침의 왼쪽"이 비어보이는 것이 정상입니다.
  // (첫 페이지가 오른쪽에만 놓임) → 더미 1장을 앞에 끼워서 p1이 왼쪽에 오도록 맞춥니다.
  return [
    { key: 'blank0', title: '', body: '' },
    { key: 'p1', title: '내 정보', body: '닉네임/레벨/뱃지 등 프로필 정보를 여기에 배치' },
    { key: 'p2', title: '내 정보(2)', body: '자기소개/관심 알고리즘/링크 등을 종이 레이아웃으로' },
    { key: 'p3', title: '학습 기록', body: '최근 푼 문제, 성공률, streak 등을 타임라인처럼' },
    { key: 'p4', title: '학습 기록(2)', body: '언어별 통계/난이도 분포 등을 차트/표로' },
    { key: 'p5', title: '설정', body: '테마, 알림, 계정 관리 등 설정 항목' },
    { key: 'p6', title: '설정(2)', body: '로그아웃/탈퇴 같은 위험 액션은 하단에' },
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

  // 이미 인스턴스가 있으면 resize는 update()로만 처리 (destroy 금지: destroy가 root DOM을 제거함)
  if (flip.value) {
    scheduleUpdate()
    return
  }

  const instance = new PageFlip(bookEl.value, {
    // 첫 렌더링에서 한 화면에 들어오도록 살짝 축소
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
    // desktop은 blank0(0번)을 끼워 넣었으므로 탭 매핑에 오프셋 반영
    activeTabIndex.value = isCompact.value ? pageIndex : Math.max(0, Math.floor((pageIndex - 1) / 2))
  })

  flip.value = instance

  // desktop(스프레드)에서는 p1이 왼쪽에 오도록 1번 페이지에서 시작
  if (!isCompact.value) {
    try {
      instance.turnToPage(1)
    } catch {
      // ignore
    }
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

  // desktop(스프레드)에서는 0번(blank0)에 머무르지 않게 보정
  if (!isCompact.value && flip.value.getPageCount() > 1 && flip.value.getCurrentPageIndex() === 0) {
    flip.value.turnToPage(1)
  }
}

const goToTab = (idx) => {
  activeTabIndex.value = idx
  // 넓은 화면: 스프레드(2p) 기준, 좁은 화면: 1p 기준
  // desktop은 blank0(0번) 때문에 1번이 첫 탭 시작점
  const pageIndex = isCompact.value ? idx : idx * 2 + 1
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

