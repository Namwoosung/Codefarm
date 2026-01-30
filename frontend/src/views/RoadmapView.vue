<template>
  <div class="bg-farm-cream">
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

    <main class="mx-auto max-w-7xl px-6 py-12">
      <PageTitle title="커리큘럼" />

      <section class="mt-8 relative">
        <div class="cf-panel">
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
              <div class="cf-roadmap-level-header">
                <span class="cf-roadmap-level-label">LEVEL {{ idx + 1 }}</span>
                <span class="cf-roadmap-level-topic">{{ levelTopics[idx] }}</span>
              </div>
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
                    :aria-label="`레벨 ${idx + 1} - ${n}`"
                    @click="onClickLevel(idx + 1, n)"
                    @mouseenter="onHoverLevel(idx + 1, n)"
                    @mouseleave="onLeaveLevel"
                  />
                </div>
              </div>
              <Transition name="cf-summary">
                <div
                  v-if="hoveredRoadmap === idx + 1 && hoveredLevel"
                  class="cf-level-summary"
                >
                  <p class="cf-level-summary-title">
                    {{
                      getStepProblem(idx, hoveredLevel)?.problem?.title ||
                        `LEVEL ${idx + 1} - STEP ${hoveredLevel}`
                    }}
                  </p>
                  <p class="cf-level-summary-desc">
                    {{
                      getStepSummary(idx, hoveredLevel) ||
                        '문제 요약 정보를 불러올 수 없습니다.'
                    }}
                  </p>
                </div>
              </Transition>

              <div
                v-if="idx === 3 || idx === 4"
                class="cf-roadmap-recommend"
              >
                <button
                  type="button"
                  class="cf-recommend-btn"
                  @click="onClickRecommend(idx)"
                >
                  추천 문제 보기
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <div
      v-if="modalContext"
      class="cf-modal-backdrop"
      @click="closeModal"
    >
      <div
        class="cf-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="cf-modal-title"
        @click.stop
      >
        <h2 id="cf-modal-title" class="cf-modal-title">
          {{ modalTitle }}
        </h2>
        <div class="cf-modal-body">
          <dl class="cf-modal-dl">
            <template v-if="modalContent">
              <div v-if="modalContent.problem?.difficulty" class="cf-modal-row">
                <dt>난이도</dt>
                <dd>{{ modalContent.problem.difficulty }}</dd>
              </div>
              <div v-if="modalContent.problem?.algorithm" class="cf-modal-row">
                <dt>알고리즘</dt>
                <dd>{{ modalContent.problem.algorithm }}</dd>
              </div>
              <div
                v-if="
                  modalContent.statistics?.submissionCount != null &&
                  modalContent.statistics?.successCount != null
                "
                class="cf-modal-row"
              >
                <dt>정답률</dt>
                <dd>
                  {{ formatSuccessRate(modalContent.statistics.successCount, modalContent.statistics.submissionCount) }}
                </dd>
              </div>
              <div
                v-if="
                  modalContext?.type === 'step' || modalContext?.type === 'recommend'
                "
                class="cf-modal-row"
              >
                <dt>내 상태</dt>
                <dd>
                  {{
                    modalContent.userStatus?.isSolved
                      ? '해결함'
                      : modalContent.userStatus?.isTried
                        ? '시도함'
                        : '미시도'
                  }}
                </dd>
              </div>
            </template>
            <p v-else class="cf-modal-no-data">문제 정보를 불러올 수 없습니다.</p>
          </dl>
        </div>
        <div class="cf-modal-actions">
          <button type="button" class="cf-modal-btn cf-modal-btn-close" @click="closeModal">
            닫기
          </button>
          <button
            type="button"
            class="cf-modal-btn cf-modal-btn-ide"
            :disabled="!modalProblemId"
            @click="goToIdeFromModal"
          >
            문제풀기
          </button>
        </div>
      </div>
    </div>
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
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const hoveredRoadmap = ref(null)
const hoveredLevel = ref(null)
const curriculums = ref([])
const modalContext = ref(null)
const recommendedErrorByLevel = ref({})

const roadmapImages = [
  roadmapImage1,
  roadmapImage2,
  roadmapImage3,
  roadmapImage4,
  roadmapImage5,
]

const levelTopics = [
  '입출력과 사칙연산',
  '조건문',
  '반복문',
  '스택과 큐',
  '완전탐색',
]

function normalizeCurriculumList(raw) {
  const list = Array.isArray(raw)
    ? raw
    : Array.isArray(raw?.curriculums)
      ? raw.curriculums
      : []
  return list.map((item) => {
    const c = item.curriculum ?? item
    const problems = Array.isArray(c?.problems) ? c.problems : []
    const normalizedProblems = problems.map((p) => {
      const order = p?.order ?? p?.orderNo ?? p?.order_no ?? 0
      const problem = p?.problem ?? p
      const problemId = problem?.problemId ?? problem?.id
      const statistics = p?.statistics ?? {}
      const userStatus = p?.userStatus ?? {}
      return {
        ...p,
        order,
        problem: problem ? { ...problem, problemId } : null,
        statistics: {
          successCount: statistics.successCount ?? statistics.success_count,
          submissionCount: statistics.submissionCount ?? statistics.submission_count,
        },
        userStatus: {
          isSolved: userStatus.isSolved ?? userStatus.is_solved,
          isTried: userStatus.isTried ?? userStatus.is_tried,
        },
      }
    })
    const recommended =
      item.recommendedProblem ??
      item.recommended_problem ??
      item.recommended ??
      item.recommend_problem ??
      c?.recommendedProblem ??
      c?.recommended_problem ??
      c?.recommended
    const isFlatProblem =
      recommended &&
      (recommended.problemId != null || recommended.id != null) &&
      !recommended.problem
    const recProblem = recommended?.problem ?? (isFlatProblem ? recommended : null) ?? recommended
    const recProblemId = recProblem?.problemId ?? recProblem?.id
    const recStats = recommended?.statistics ?? {}
    const normalizedRecommended = recommended
      ? {
          ...recommended,
          problem: recProblem ? { ...recProblem, problemId: recProblemId } : null,
          statistics: {
            successCount:
              recStats.successCount ?? recStats.success_count ?? 0,
            submissionCount:
              recStats.submissionCount ?? recStats.submission_count ?? 0,
          },
        }
      : null
    return {
      ...c,
      problems: normalizedProblems,
      recommendedProblem: normalizedRecommended,
    }
  })
}

async function fetchCurriculums() {
  try {
    const res = await api.get('/curriculums/lists', {
      params: { _t: Date.now() },
    })
    const data = res.data?.data ?? res.data
    const list = normalizeCurriculumList(data?.curriculums ?? data)
    const extraRecommended =
      data?.recommendedProblems ?? data?.recommended_problems
    if (Array.isArray(extraRecommended) && extraRecommended.length >= 2) {
      const norm = (rec) => {
        if (!rec) return null
        const problem = rec.problem ?? (rec.problemId != null || rec.id ? rec : null)
        const pid = problem?.problemId ?? problem?.id
        const stats = rec.statistics ?? {}
        return {
          problem: problem ? { ...problem, problemId: pid } : null,
          statistics: {
            successCount: stats.successCount ?? stats.success_count ?? 0,
            submissionCount: stats.submissionCount ?? stats.submission_count ?? 0,
          },
        }
      }
      list[3] = { ...list[3], recommendedProblem: norm(extraRecommended[0]) ?? list[3].recommendedProblem }
      list[4] = { ...list[4], recommendedProblem: norm(extraRecommended[1]) ?? list[4].recommendedProblem }
    }
    curriculums.value = list
    recommendedErrorByLevel.value = {}
    await Promise.all([
      fetchRecommendedForCurriculum(3),
      fetchRecommendedForCurriculum(4),
    ])
  } catch (error) {
    console.error('Failed to fetch curriculums', error)
    curriculums.value = []
  }
}

function normalizeRecommendedResponse(raw) {
  const payload = raw?.data?.data ?? raw?.data ?? raw
  if (!payload) return null
  // API: data.recommendedProblem = { problem, userStatus, statistics }
  const data =
    payload.recommendedProblem ??
    payload.recommended_problem ??
    payload
  if (!data) return null
  const problem = data.problem ?? (data.problemId != null || data.id ? data : null)
  const problemId = problem?.problemId ?? problem?.id
  const stats = data.statistics ?? problem?.statistics ?? {}
  const userStatus = data.userStatus ?? data.user_status ?? {}
  return {
    problem: problem ? { ...problem, problemId } : null,
    statistics: {
      successCount: stats.successCount ?? stats.success_count ?? 0,
      submissionCount: stats.submissionCount ?? stats.submission_count ?? 0,
    },
    userStatus: {
      isSolved: userStatus.isSolved ?? userStatus.is_solved ?? false,
      isTried: userStatus.isTried ?? userStatus.is_tried ?? false,
    },
  }
}

async function fetchRecommendedForCurriculum(curriculumIdx) {
  const curriculum = curriculums.value[curriculumIdx]
  const curriculumId =
    curriculum?.curriculumId ?? curriculum?.curriculum_id ?? curriculum?.id
  if (curriculumId == null) return
  try {
    const res = await api.get(`/curriculums/${curriculumId}/recommend`)
    const normalized = normalizeRecommendedResponse(res)
    const list = [...curriculums.value]
    list[curriculumIdx] = {
      ...list[curriculumIdx],
      recommendedProblem: normalized ?? list[curriculumIdx].recommendedProblem,
    }
    curriculums.value = list
    recommendedErrorByLevel.value = {
      ...recommendedErrorByLevel.value,
      [curriculumIdx]: null,
    }
  } catch (error) {
    const code = error.response?.data?.errorCode
    const isUnauthorized =
      error.response?.status === 401 || code === 'UNAUTHORIZED'
    if (isUnauthorized) {
      recommendedErrorByLevel.value = {
        ...recommendedErrorByLevel.value,
        [curriculumIdx]: 'UNAUTHORIZED',
      }
    } else {
      console.error(
        `Failed to fetch recommend for curriculum ${curriculumId}`,
        error
      )
    }
  }
}

onMounted(() => {
  fetchCurriculums()
})

watch(
  () => route.query.refresh,
  () => {
    fetchCurriculums()
  }
)

function formatSuccessRate(successCount, submissionCount) {
  const s = successCount ?? 0
  const t = submissionCount ?? 0
  if (t === 0) return '0%'
  return `${Math.round((s / t) * 100)}%`
}

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
    parts.push(
      `정답률 ${formatSuccessRate(statistics.successCount, statistics.submissionCount)}`
    )
  }
  if (userStatus?.isSolved) parts.push('내 상태: 해결함')
  else if (userStatus?.isTried) parts.push('내 상태: 시도함')
  else parts.push('내 상태: 미시도')

  return parts.join(' · ')
}

function getRecommendedForLevel(curriculumIdx) {
  return curriculums.value[curriculumIdx]?.recommendedProblem || null
}

const recommendedByLevel = computed(() =>
  curriculums.value.map((c) => c?.recommendedProblem ?? null)
)

const modalStep = computed(() => {
  const ctx = modalContext.value
  if (!ctx || ctx.type !== 'step') return null
  return getStepProblem(ctx.curriculumIdx, ctx.level)
})

const modalRecommended = computed(() => {
  const ctx = modalContext.value
  if (!ctx || ctx.type !== 'recommend') return null
  return getRecommendedForLevel(ctx.curriculumIdx)
})

const modalContent = computed(() => {
  if (modalContext.value?.type === 'step') return modalStep.value
  if (modalContext.value?.type === 'recommend') return modalRecommended.value
  return null
})

const modalTitle = computed(() => {
  const ctx = modalContext.value
  const title = modalContent.value?.problem?.title
  if (ctx?.type === 'recommend') {
    return title ? `추천문제: ${title}` : '추천문제'
  }
  return title || '문제 상세'
})

const modalProblemId = computed(() => modalContent.value?.problem?.problemId ?? null)

function onHoverLevel(roadmapIndex, level) {
  hoveredRoadmap.value = roadmapIndex
  hoveredLevel.value = level
}
function onLeaveLevel() {
  hoveredRoadmap.value = null
  hoveredLevel.value = null
}

function onClickLevel(roadmapIndex, level) {
  const curriculumIdx = roadmapIndex - 1
  const step = getStepProblem(curriculumIdx, level)
  if (!step) return
  modalContext.value = { type: 'step', curriculumIdx, level }
}

function onClickRecommend(curriculumIdx) {
  modalContext.value = { type: 'recommend', curriculumIdx }
}

function closeModal() {
  modalContext.value = null
}

function goToIdeFromModal() {
  const problemId = modalProblemId.value
  closeModal()
  if (problemId != null) {
    router.push({ name: 'ide', params: { id: String(problemId) } })
  }
}
</script>

<style scoped>
.cf-hero-title {
  font-size: clamp(2rem, 3.2vw, 3.25rem);
  font-weight: 900;
  letter-spacing: -0.02em;
  text-shadow: 0 4px 0 rgba(0, 0, 0, 0.18), 0 10px 22px rgba(0, 0, 0, 0.18);
}
.cf-hero-sub {
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.18);
}

.cf-banner-inner {
  height: 18rem;
}
@media (min-width: 768px) {
  .cf-banner-inner {
    height: 20rem;
  }
}

.cf-hero-char {
  pointer-events: none;
}
.cf-hero-char-img {
  transform: scale(1.65);
  transform-origin: top center;
}

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

.cf-roadmap-recommend {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 5;
}
.cf-recommend-desc {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.4;
}

.cf-roadmap {
  position: relative;
  width: 100%;
  max-width: 100%;
  height: 400px;
  max-height: 400px;
  border-radius: 22px;
  overflow: hidden;
  margin-bottom: 20px;
}
.cf-roadmap-img {
  width: 100%;
  height: 100%;
  min-height: 0;
  display: block;
  object-fit: cover;
  object-position: center center;
}
.cf-roadmap-level-header {
  position: absolute;
  top: 1rem;
  left: 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  z-index: 2;
  pointer-events: none;
}
.cf-roadmap-level-label {
  font-size: 1.125rem;
  font-weight: 800;
  color: #fff;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.05em;
}
.cf-roadmap-level-topic {
  font-size: 1rem;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 2px 6px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.02em;
}

.cf-summary-enter-active,
.cf-summary-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.cf-summary-enter-from,
.cf-summary-leave-to {
  opacity: 0;
  transform: translateY(6px);
}

.cf-level-summary {
  position: absolute;
  left: 6%;
  right: 6%;
  top: 50%;
  bottom: 10%;
  padding: 1rem 1.25rem;
  border-radius: 16px;
  background: #fff9e9;
  border: 5px solid #6f5338;
  box-shadow: 0 8px 24px rgba(111, 83, 56, 0.2), 0 4px 12px rgba(0, 0, 0, 0.08);
  z-index: 3;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 0.35rem;
}
.cf-level-summary-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #4e3b2a;
  letter-spacing: -0.02em;
  line-height: 1.35;
  margin: 0;
}
.cf-level-summary-desc {
  font-size: 1rem;
  color: #4e3b2a;
  line-height: 1.45;
  margin: 0;
  font-weight: 500;
}
.cf-roadmap-levels {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  transform: translateY(-150px);
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

/* 문제 상세 모달 */
.cf-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.4);
  cursor: pointer;
}
.cf-modal {
  width: 100%;
  max-width: 28rem;
  padding: 1.5rem;
  background: #fff9e9;
  border: 3px solid #7a5c3e;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  cursor: default;
}
.cf-modal-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #4e3b2a;
  margin: 0 0 1rem;
  line-height: 1.35;
}
.cf-modal-body {
  margin-bottom: 1.25rem;
}
.cf-modal-dl {
  margin: 0;
}
.cf-modal-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}
.cf-modal-row dt {
  flex-shrink: 0;
  font-weight: 600;
  color: #5c4a3a;
}
.cf-modal-row dd {
  margin: 0;
  color: #4e3b2a;
}
.cf-modal-no-data {
  margin: 0;
  font-size: 0.95rem;
  color: #7a6b5a;
}
.cf-modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}
.cf-modal-btn {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
  border-radius: 10px;
  cursor: pointer;
  transition: filter 0.15s ease, transform 0.15s ease;
}
.cf-modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.cf-modal-btn-close {
  background: #e8e0d0;
  color: #5c4a3a;
  border: 1px solid #c4b8a8;
}
.cf-modal-btn-close:hover:not(:disabled) {
  filter: brightness(0.96);
}
.cf-modal-btn-ide {
  background: #7a5c3e;
  color: #fff;
  border: 1px solid #6b4e32;
}
.cf-modal-btn-ide:hover:not(:disabled) {
  filter: brightness(1.08);
}
</style>