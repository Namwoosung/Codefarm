<template>
  <div class="bg-farm-cream">
    <!-- Banner: 고정 높이 — 캐릭터 크기와 무관하게 배너 높이 유지 -->
    <section class="bg-[#7AA74E] overflow-hidden">
      <div
        class="mx-auto max-w-7xl px-6 py-16 md:py-20 relative flex flex-col justify-center overflow-hidden cf-banner-inner"
      >
        <div class="flex items-center gap-6 flex-nowrap pr-64 md:pr-72 lg:pr-80">
          <div class="text-white min-w-0 flex-1">
            <h1 class="cf-hero-title">커리큘럼을 따라 풀어보세요!</h1>
            <p class="mt-3 text-lg md:text-xl text-white/90 cf-hero-sub">
              다양한 문제를 풀고 작물 카드를 모아보세요.
            </p>
          </div>
        </div>

        <div
          class="cf-hero-char max-md:hidden absolute right-6 bottom-0 flex items-start overflow-hidden"
          style="width: 16rem; height: 14rem;"
        >
          <img
            class="cf-hero-char-img w-full min-h-[200%] object-contain object-top"
            :src="heroCharacter"
            alt="character"
          />
        </div>
      </div>
    </section>

    <!-- Content -->
    <main class="mx-auto max-w-7xl px-6 py-12">
      <PageTitle title="커리큘럼" />

      <!-- 추천 문제 버튼 -->
      <div class="mt-4 flex justify-end">
        <div class="cf-recommend-wrapper">
          <button type="button" class="cf-recommend-btn">
            추천 문제 보기
          </button>
          <div class="cf-recommend-tooltip">
            <p class="cf-recommend-title">
              {{ firstRecommended?.problem?.title || '추천 문제 요약' }}
            </p>
            <p v-if="firstRecommended" class="cf-recommend-desc">
              난이도 {{ firstRecommended.problem.difficulty }}
              · 알고리즘 {{ firstRecommended.problem.algorithm }}
              · 정답
              {{ firstRecommended.statistics.successCount }} /
              {{ firstRecommended.statistics.submissionCount }}
            </p>
            <p v-else class="cf-recommend-desc">
              추천 문제 정보를 불러오는 중입니다.
            </p>
          </div>
        </div>
      </div>

      <section class="mt-8 relative">
        <div class="cf-panel">
          <!-- 이미지 기반 로드맵 -->
          <div class="cf-panel-inner">
            <div
              v-for="(img, idx) in roadmapImages"
              :key="idx"
              class="cf-roadmap"
            >
              <img
                class="cf-roadmap-img"
                :src="img"
                :alt="`레벨 ${idx + 1} roadmap`"
              />
              <span class="cf-roadmap-level-label">LEVEL {{ idx + 1 }}</span>
              <div class="cf-roadmap-levels">
                <div
                  v-for="n in 5"
                  :key="n"
                  class="cf-level"
                >
                  <div class="cf-level-visual">
                    <span class="cf-level-num">STEP {{ n }}</span>
                    <img
                      class="cf-level-cloud"
                      :src="woodPanel1"
                      alt=""
                      aria-hidden="true"
                    />
                  </div>
                  <button
                    type="button"
                    class="cf-level-btn"
                    :aria-label="`레벨 ${idx + 1}-${n}`"
                    @click="onClickLevel(idx + 1, n)"
                    @mouseenter="onHoverLevel(idx + 1, n)"
                    @mouseleave="onLeaveLevel"
                  />
                </div>
              </div>
              <div
                v-if="hoveredRoadmap === idx + 1 && hoveredLevel"
                class="cf-level-summary"
              >
                <p class="cf-level-summary-title">
                  {{
                    getStepProblem(idx, hoveredLevel)?.problem?.title ||
                      `LEVEL ${idx + 1} · STEP ${hoveredLevel}`
                  }}
                </p>
                <p class="cf-level-summary-desc">
                  {{
                    getStepSummary(idx, hoveredLevel) ||
                      '문제 요약 정보를 불러올 수 없습니다.'
                  }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import PageTitle from '@/components/atoms/PageTitle.vue'
import heroCharacter from '@/assets/chicken.png'
import roadmapImage1 from '@/assets/pond.png'
import roadmapImage2 from '@/assets/fruits.png'
import roadmapImage3 from '@/assets/veg_field.png'
import roadmapImage4 from '@/assets/forest.png'
import roadmapImage5 from '@/assets/cowshed.png'
import woodPanel1 from '@/assets/wood_panel_1.png'
import api from '@/api'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const debug = ref(false)
const hoveredRoadmap = ref(null)
const hoveredLevel = ref(null)
const curriculums = ref([])

/**
 * 라우팅/동작은 프로젝트에 맞게 바꿔도 됨
 * 예) router.push({ name: 'curriculum', params: { level } })
 */
function onClickHelp() {
  // TODO: 힌트 모달 / 도움말 페이지
  // router.push({ name: 'help' })
  console.log('Help clicked')
}

const roadmapImages = [
  roadmapImage1,
  roadmapImage2,
  roadmapImage3,
  roadmapImage4,
  roadmapImage5,
]

async function fetchCurriculums() {
  try {
    const res = await api.get('/curriculums/lists')
    curriculums.value = res.data?.data?.curriculums || []
  } catch (error) {
    console.error('Failed to fetch curriculums', error)
  }
}

onMounted(() => {
  fetchCurriculums()
})

function getStepProblem(curriculumIdx, level) {
  const curriculum = curriculums.value[curriculumIdx]
  if (!curriculum || !Array.isArray(curriculum.problems)) return null
  return (
    curriculum.problems.find((p) => p.order === level) ||
    curriculum.problems[level - 1] ||
    null
  )
}

function getStepSummary(curriculumIdx, level) {
  const step = getStepProblem(curriculumIdx, level)
  if (!step) return ''

  const { problem, statistics, userStatus } = step
  const parts = []

  if (problem?.difficulty) parts.push(`난이도 ${problem.difficulty}`)
  if (problem?.algorithm) parts.push(`알고리즘 ${problem.algorithm}`)
  if (statistics?.submissionCount != null && statistics?.successCount != null) {
    parts.push(`정답 ${statistics.successCount}/${statistics.submissionCount}`)
  }
  if (userStatus?.isSolved) parts.push('내 상태: 해결함')
  else if (userStatus?.isTried) parts.push('내 상태: 시도함')
  else parts.push('내 상태: 미시도')

  return parts.join(' · ')
}

const firstRecommended = computed(() => {
  return curriculums.value[0]?.recommendedProblem || null
})

function onHoverLevel(roadmapIndex, level) {
  hoveredRoadmap.value = roadmapIndex
  hoveredLevel.value = level
}
function onLeaveLevel() {
  hoveredRoadmap.value = null
  hoveredLevel.value = null
}

function onClickLevel(roadmapIndex, level) {
  // TODO: 레벨별 커리큘럼 라우팅 (기능 나중에 연결)
  // router.push({ name: 'curriculum', query: { roadmap: roadmapIndex, level } })
  console.log('Level clicked:', roadmapIndex, level)
}
</script>

<style scoped>
/* Banner typography */
.cf-hero-title {
  font-size: clamp(2rem, 3.2vw, 3.25rem);
  font-weight: 900;
  letter-spacing: -0.02em;
  text-shadow: 0 4px 0 rgba(0, 0, 0, 0.18), 0 10px 22px rgba(0, 0, 0, 0.18);
}
.cf-hero-sub {
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
}

/* Banner: 이미지 크기와 무관하게 고정 높이 */
.cf-banner-inner {
  height: 18rem;
}
@media (min-width: 768px) {
  .cf-banner-inner {
    height: 20rem;
  }
}

/* Hero character: scaled up, lower body clipped */
.cf-hero-char {
  pointer-events: none;
}
.cf-hero-char-img {
  transform: scale(1.65);
  transform-origin: top center;
}

/* Panel */
.cf-panel {
  border-radius: 28px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 18px 30px rgba(0, 0, 0, 0.16);
  overflow: hidden;
}
.cf-panel-inner {
  padding: 26px;
}

/* 추천 문제 버튼 */
.cf-recommend-wrapper {
  position: relative;
  display: inline-block;
}
.cf-recommend-btn {
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  border: 1px solid rgba(0, 0, 0, 0.08);
  background: linear-gradient(135deg, #ffeb3b, #ffb300);
  color: #3b2b00;
  font-size: 0.9rem;
  font-weight: 700;
  box-shadow: 0 6px 14px rgba(0, 0, 0, 0.16);
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease, filter 0.15s ease;
}
.cf-recommend-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
  filter: brightness(1.05);
}
.cf-recommend-btn:active {
  transform: translateY(0);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.18);
}
.cf-recommend-tooltip {
  position: absolute;
  right: 0;
  top: 110%;
  margin-top: 0.4rem;
  width: 260px;
  max-width: 80vw;
  padding: 0.75rem 0.9rem;
  border-radius: 14px;
  background: #ffffff;
  box-shadow: 0 14px 30px rgba(0, 0, 0, 0.16);
  border: 1px solid rgba(0, 0, 0, 0.06);
  opacity: 0;
  transform: translateY(4px);
  pointer-events: none;
  transition: opacity 0.18s ease, transform 0.18s ease;
  z-index: 10;
}
.cf-recommend-wrapper:hover .cf-recommend-tooltip {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.cf-recommend-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: #333;
  margin-bottom: 0.25rem;
}
.cf-recommend-desc {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.4;
}

/* Roadmap image area */
.cf-roadmap {
  position: relative;
  width: 100%;
  max-width: 100%;
  border-radius: 22px;
  overflow: hidden;
  margin-bottom: 20px;
}
.cf-roadmap-img {
  width: 100%;
  height: auto;
  display: block;
  object-fit: cover;
  max-height: calc(100% - 50px);
  object-position: center top;
}
.cf-roadmap-level-label {
  position: absolute;
  top: 1rem;
  left: 1rem;
  font-size: 1.125rem;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.05em;
  z-index: 2;
  pointer-events: none;
}

.cf-level-summary {
  position: absolute;
  left: 6%;
  right: 6%;
  top: 50%;
  bottom: 10%;
  padding: 0.85rem 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 18px 28px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(0, 0, 0, 0.06);
  z-index: 3;
}
.cf-level-summary-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: #333;
  margin-bottom: 0.25rem;
}
.cf-level-summary-desc {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.4;
}

/* 레벨 오버레이: 구름 + 번호 + 투명 버튼 */
.cf-roadmap-levels {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  transform: translateY(-250px);
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding: 0 6% 8%;
  gap: 2%;
  z-index: 2;
  pointer-events: none;
}
.cf-roadmap-levels > * {
  pointer-events: auto;
}
.cf-level {
  flex: 1;
  flex-basis: 0;
  max-width: 22%;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}
.cf-level-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  transition: transform 0.25s ease;
  transform-origin: center center;
}
.cf-level:hover .cf-level-visual {
  transform: scale(1.2);
}
.cf-level-num {
  position: absolute;
  top: 50%;
  left: calc(50% + 10px);
  transform: translate(-50%, -50%);
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
  line-height: 1.2;
  z-index: 1;
  transition: color 0.25s ease, text-shadow 0.25s ease;
  white-space: nowrap;
  text-align: center;
}
.cf-level:hover .cf-level-num {
  transform: translate(-50%, -50%);
}
.cf-level:hover .cf-level-num {
  color: #ffeb3b;
  text-shadow: 0 0 12px rgba(255, 235, 59, 0.7), 0 2px 4px rgba(0, 0, 0, 0.4);
}
.cf-level-cloud {
  width: 7rem;
  height: auto;
  object-fit: contain;
  display: block;
  transition: filter 0.25s ease;
}
.cf-level:hover .cf-level-cloud {
  filter: brightness(1.2) drop-shadow(0 0 10px rgba(255, 235, 59, 0.4));
}
.cf-level-btn {
  position: absolute;
  inset: 0;
  padding: 0;
  margin: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  border-radius: 12px;
  outline: none;
}
.cf-level-btn:focus-visible {
  outline: 2px solid rgba(255, 235, 59, 0.9);
  outline-offset: 2px;
}

@media (min-width: 768px) {
  .cf-level-num { font-size: 1.5rem; }
  .cf-level-cloud { width: 9rem; }
}

/* Transparent clickable hotspots */
.cf-hotspot {
  position: absolute;
  background: transparent;
  border: 0;
  padding: 0;
  cursor: pointer;
  border-radius: 9999px;
  /* 클릭/탭 하이라이트 최소화 */
  outline: none;
}
.cf-hotspot:focus-visible {
  outline: 2px solid rgba(255, 255, 255, 0.9);
  outline-offset: 4px;
}

/* 디버그용: 영역 확인 */
.cf-hotspot-debug {
  background: rgba(255, 0, 0, 0.14);
  box-shadow: inset 0 0 0 2px rgba(255, 0, 0, 0.55);
}
</style>