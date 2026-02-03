<template>
  <div class="bg-farm-cream min-h-screen">
    <main :class="[!selectedLevel ? 'mx-auto max-w-7xl px-6 py-12' : 'w-full h-screen overflow-hidden']">
      <!-- 메인 로드맵 이미지 영역 (레벨 미선택 시) -->
      <section v-if="!selectedLevel" class="relative w-full flex flex-col items-center">
        <div class="mb-12 text-center">
          <h2 class="text-4xl font-dnf text-farm-brown-dark mb-4 tracking-tight">Welcome to Code Farm!</h2>
          <p class="text-lg text-farm-brown opacity-75 font-medium">길을 따라 모험을 시작할 레벨을 선택하세요.</p>
        </div>
        
        <div class="relative w-full flex flex-col items-center">
        <div class="relative w-[50%] max-w-[600px]">
          <!-- 상단 블러 마스크: z-20으로 높여 지도 위를 덮음 -->
          <div class="absolute top-0 left-0 w-full h-24 bg-gradient-to-b from-farm-cream via-farm-cream/80 to-transparent z-20 pointer-events-none"></div>
          
          <!-- 캐릭터와 툴팁: z-30으로 높여 가장 앞으로 배치 (클릭 통과 유지) -->
          <div class="absolute left-[-220px] top-[28%] -translate-y-1/2 w-72 h-72 z-30 hidden lg:block pointer-events-none">
            <div class="tooltip tooltip-open tooltip-top [--tooltip-tail:0px] [--tooltip-color:rgba(255,255,50,1)] [--tooltip-text-color:#4e3b2a] [--tooltip-offset:-20px]" data-tip="다양한 문제를 풀고 포인트를 모아보세요!">
              <img
                class="w-full h-full object-contain"
                :src="heroCharacter"
                alt="character"
              />
            </div>
          </div>

            <!-- RoadmapMap: z-10으로 설정하여 캐릭터와 마스크 뒤로 보냄 -->
            <RoadmapMap
              :background-image="roadmapMainImage"
              @select-level="(id) => selectedLevel = id"
              class="w-full relative z-10"
            />

            <!-- 오리 캐릭터와 툴팁: z-30으로 상향 -->
            <div class="absolute right-[-140px] top-[58%] -translate-y-1/2 w-52 h-52 z-30 hidden lg:block pointer-events-none">
              <div class="tooltip tooltip-open tooltip-top [--tooltip-tail:0px] [--tooltip-color:rgba(74,74,41,0.9)] [--tooltip-text-color:#ffffff] [--tooltip-offset:-20px]" data-tip="100포인트로 카드뽑기를 할 수 있어요!">
                <img
                  class="w-full h-full object-contain"
                  :src="duckCharacter"
                  alt="duck"
                />
              </div>
            </div>

          <!-- 하단 블러 마스크: z-20으로 상향 -->
          <div class="absolute bottom-0 left-0 w-full h-24 bg-gradient-to-t from-farm-cream via-farm-cream/80 to-transparent z-20 pointer-events-none"></div>

          <!-- 좌측 하단 메가크루 이미지: 위치 고정 및 좌측 정렬된 툴팁 추가 -->
          <div class="absolute left-[-260px] bottom-[-240px] w-[620px] h-[630px] z-30 hidden lg:block pointer-events-none">
            <!-- 가장 좌측 캐릭터 위쪽에 위치하도록 조정 (위치 하향) -->
            <div 
              class="absolute left-[220px] top-[160px] tooltip tooltip-open tooltip-top [--tooltip-tail:0px] [--tooltip-color:rgba(255,235,59,0.9)] [--tooltip-text-color:#4e3b2a]" 
              data-tip="문제가 잘 안풀리나요? 추천 문제로 보충해보아요"
            ></div>
            <img
              class="w-full h-full object-contain opacity-90"
              :src="megacrewImage"
              alt="megacrew"
            />
          </div>
        </div>
        </div>
      </section>

      <!-- 선택된 레벨의 커리큘럼 영역 -->
      <section v-else class="relative w-full h-full">
        <div class="cf-panel-inner !p-0 h-full">
          <div class="cf-roadmap !h-full !max-h-none !mb-0 !rounded-none">
            <!-- 돌아가기 버튼: 좌측 전체 높이 사이드바 형태 -->
            <div class="absolute left-0 top-0 h-full z-30 flex items-center">
              <button 
                @click="selectedLevel = null"
                class="group relative flex items-center w-8 hover:w-24 h-full bg-white/5 hover:bg-white/90 backdrop-blur-md text-farm-olive transition-all duration-500 ease-in-out overflow-hidden border-r border-white/10 pointer-events-auto"
              >
                <!-- 평상시 및 호버 시 공통 아이콘 영역 -->
                <div class="absolute left-0 w-8 flex justify-center items-center h-full z-10">
                  <iconify-icon 
                    icon="mdi:chevron-left" 
                    class="text-xl font-black transition-transform duration-500 group-hover:-translate-x-1"
                  ></iconify-icon>
                </div>

                <!-- 호버 시 나타나는 텍스트 영역 -->
                <div class="pl-8 pr-3 whitespace-nowrap transform translate-x-2 group-hover:translate-x-0 opacity-0 group-hover:opacity-100 transition-all duration-500 ease-out">
                  <span class="font-bold text-sm tracking-tight">Back</span>
                </div>
                
                <!-- 평상시 보여줄 우측 가이드 라인 -->
                <div class="absolute inset-y-0 right-0 w-[1px] bg-white/30 group-hover:opacity-0 transition-opacity"></div>
              </button>
            </div>

            <!-- 타이틀 영역: 이미지 위에 절대 위치로 배치 -->
            <div class="absolute top-24 left-0 w-full z-20 pointer-events-none">
              <div class="text-center relative">
                <h2 class="text-sm font-bold text-farm-olive/80 tracking-[0.3em] uppercase mb-1">Curriculum</h2>
                <h1 class="text-6xl font-dnf text-farm-olive mb-2 relative inline-block">
                  LEVEL {{ selectedLevel }}
                </h1>
                <p class="text-2xl text-farm-olive font-bold tracking-tight">
                  {{ levelTopics[selectedLevel - 1] }}
                </p>
              </div>
            </div>

            <img
              class="cf-roadmap-img"
              :src="roadmapImages[selectedLevel - 1]"
              :alt="`레벨 ${selectedLevel} roadmap`"
            />
            <div class="cf-roadmap-levels">
              <div
                v-for="n in 5"
                :key="n"
                class="cf-level group/level"
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
                  :aria-label="`레벨 ${selectedLevel} - ${n}`"
                  @click="onClickLevel(selectedLevel, n)"
                  @mouseenter="onHoverLevel(selectedLevel, n)"
                  @mouseleave="onLeaveLevel"
                />
                
                <!-- 문제 정보: 표지판 바로 아래에 노출 -->
                <Transition name="cf-summary-vertical">
                  <div
                    v-if="hoveredRoadmap === selectedLevel && hoveredLevel === n"
                    class="cf-level-summary-vertical"
                  >
                    <div class="flex flex-col gap-2">
                      <div class="flex items-center justify-center gap-1.5">
                        <span class="px-2 py-0.5 rounded-md bg-farm-olive/10 text-[10px] font-bold text-farm-olive uppercase tracking-wider">Step {{ n }}</span>
                        <div class="h-1 w-1 rounded-full bg-farm-brown/30"></div>
                        <span class="text-[10px] font-bold text-farm-brown/60 uppercase tracking-wider">Problem</span>
                      </div>
                      
                      <p class="cf-level-summary-title">
                        {{
                          getStepProblem(selectedLevel - 1, n)?.problem?.title ||
                            `STEP ${n}`
                        }}
                      </p>
                      
                      <div class="h-[1px] w-full bg-gradient-to-r from-transparent via-farm-brown/20 to-transparent my-1"></div>
                      
                      <div class="flex flex-wrap justify-center gap-x-3 gap-y-1">
                        <div v-if="getStepProblem(selectedLevel - 1, n)?.problem?.difficulty" class="flex items-center gap-1">
                          <span class="text-[10px] text-farm-brown/50 font-bold">난이도</span>
                          <span class="text-[11px] text-farm-brown font-bold">{{ getStepProblem(selectedLevel - 1, n).problem.difficulty }}</span>
                        </div>
                        <div v-if="getStepProblem(selectedLevel - 1, n)?.statistics?.successCount != null" class="flex items-center gap-1">
                          <span class="text-[10px] text-farm-brown/50 font-bold">정답률</span>
                          <span class="text-[11px] text-farm-brown font-bold">{{ formatSuccessRate(getStepProblem(selectedLevel - 1, n).statistics.successCount, getStepProblem(selectedLevel - 1, n).statistics.submissionCount) }}</span>
                        </div>
                      </div>

                      <div class="mt-1">
                        <span 
                          :class="[
                            'px-3 py-1 rounded-full text-[10px] font-black shadow-sm border',
                            getStepProblem(selectedLevel - 1, n)?.userStatus?.isSolved 
                              ? 'bg-green-100 text-green-700 border-green-200' 
                              : getStepProblem(selectedLevel - 1, n)?.userStatus?.isTried 
                                ? 'bg-orange-100 text-orange-700 border-orange-200' 
                                : 'bg-gray-100 text-gray-600 border-gray-200'
                          ]"
                        >
                          {{ 
                            getStepProblem(selectedLevel - 1, n)?.userStatus?.isSolved 
                              ? 'COMPLETED' 
                              : getStepProblem(selectedLevel - 1, n)?.userStatus?.isTried 
                                ? 'IN PROGRESS' 
                                : 'NOT STARTED' 
                          }}
                        </span>
                      </div>
                    </div>
                  </div>
                </Transition>
              </div>
            </div>

            <div
              v-if="selectedLevel === 4 || selectedLevel === 5"
              class="cf-roadmap-recommend"
            >
              <button
                type="button"
                class="cf-sun-btn"
                aria-label="추천 문제 보기"
                @click="onClickRecommend(selectedLevel - 1)"
              >
                <span class="cf-sun-text">추천문제</span>
              </button>
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
        <div class="cf-modal-header">
          <span class="cf-modal-label">{{ modalContext.type === 'recommend' ? 'Recommended' : `Step ${modalContext.level}` }}</span>
          <h2 id="cf-modal-title" class="cf-modal-title">
            {{ modalContent?.problem?.title || '문제 상세' }}
          </h2>
        </div>

        <div class="cf-modal-body">
          <div v-if="modalContent" class="cf-modal-content">
            <div class="cf-modal-info-grid">
              <div v-if="modalContent.problem?.difficulty" class="cf-modal-info-card">
                <dt>난이도</dt>
                <dd>{{ modalContent.problem.difficulty }}</dd>
              </div>
              <div v-if="modalContent.problem?.algorithm" class="cf-modal-info-card">
                <dt>알고리즘</dt>
                <dd>{{ modalContent.problem.algorithm }}</dd>
              </div>
              <div
                v-if="modalContent.statistics?.submissionCount != null"
                class="cf-modal-info-card"
              >
                <dt>정답률</dt>
                <dd>{{ formatSuccessRate(modalContent.statistics.successCount, modalContent.statistics.submissionCount) }}</dd>
              </div>
              <div class="cf-modal-info-card">
                <dt>제출 횟수</dt>
                <dd>{{ modalContent.statistics?.submissionCount || 0 }}회</dd>
              </div>
            </div>

            <div class="cf-modal-status-banner">
              <span class="cf-modal-status-label">나의 진행 상태</span>
              <span 
                :class="[
                  'cf-modal-status-value',
                  modalContent.userStatus?.isSolved ? 'cf-modal-status-solved' : 
                  modalContent.userStatus?.isTried ? 'cf-modal-status-tried' : 'cf-modal-status-none'
                ]"
              >
                {{
                  modalContent.userStatus?.isSolved
                    ? '해결 완료'
                    : modalContent.userStatus?.isTried
                      ? '도전 중'
                      : '미시도'
                }}
              </span>
            </div>
          </div>
          <p v-else class="cf-modal-no-data">문제 정보를 불러올 수 없습니다.</p>
        </div>

        <div class="cf-modal-actions">
          <button type="button" class="cf-modal-btn cf-modal-btn-close" @click="closeModal">
            나중에 하기
          </button>
          <button
            type="button"
            class="cf-modal-btn cf-modal-btn-ide"
            :disabled="!modalProblemId"
            @click="goToIdeFromModal"
          >
            <span>문제 풀러 가기</span>
            <span class="text-xl">→</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 풀고 있는 문제가 있을 때 다른 문제 클릭 시 확인 모달 -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="showActiveSessionModal && activeSessionPayload" class="fixed inset-0 flex items-center justify-center bg-black/40 z-[9999]">
          <div class="card bg-base-100 shadow-2xl rounded-xl p-6 min-w-[320px] max-w-[90vw] border border-base-300">
            <p class="text-lg font-semibold text-[var(--color-farm-brown-dark)] mb-4">
              풀고 있는 문제가 있습니다. (현재 {{ activeSessionPayload.otherProblemId }}번 문제)
            </p>
            <div class="flex justify-end gap-3">
              <button
                type="button"
                class="btn btn-sm btn-ghost border border-base-300"
                @click="goToExistingProblem"
              >
                기존 문제로
              </button>
              <button
                type="button"
                class="btn btn-sm bg-[var(--color-farm-green)] text-white border-none hover:bg-[var(--color-farm-green-dark)]"
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
  </div>
</template>

<script setup>
import heroCharacter from '@/assets/roadmap/chicken.png'
import duckCharacter from '@/assets/roadmap/duck.png'
import megacrewImage from '@/assets/roadmap/megacrew.png'
import roadmapMainImage from '@/assets/roadmap/Roadmap.png'
import roadmapImage1 from '@/assets/roadmap/pond.png'
import roadmapImage2 from '@/assets/roadmap/fruits.png'
import roadmapImage3 from '@/assets/roadmap/veg_field.png'
import roadmapImage4 from '@/assets/roadmap/forest.png'
import roadmapImage5 from '@/assets/roadmap/cowshed.png'
import woodPanel1 from '@/assets/roadmap/wood_panel_1.png'
import RoadmapMap from '@/components/organisms/RoadmapMap.vue'
import api from '@/api'
import * as sessionApi from '@/api/session'
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const hoveredRoadmap = ref(null)
const hoveredLevel = ref(null)
const curriculums = ref([])
const modalContext = ref(null)
const recommendedErrorByLevel = ref({})
const selectedLevel = ref(null)

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

// 쿼리 파라미터에서 레벨 복원
watch(
  () => route.query.level,
  (level) => {
    if (level != null) {
      const levelNum = Number(level)
      if (!isNaN(levelNum) && levelNum >= 1 && levelNum <= 5) {
        selectedLevel.value = levelNum
      }
    }
  },
  { immediate: true }
)

// 레벨 페이지 진입 시 스크롤을 맨 위로
watch(selectedLevel, async (level) => {
  if (level != null) {
    await nextTick()
    window.scrollTo(0, 0)
    document.documentElement.scrollTop = 0
    document.body.scrollTop = 0
  }
})

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

watch(modalContext, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
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

/** 풀고 있는 문제가 있을 때 다른 문제 클릭 시 모달 */
const showActiveSessionModal = ref(false)
const activeSessionPayload = ref(null)
const activeSessionLoading = ref(false)

async function goToIdeFromModal() {
  const problemId = modalProblemId.value != null ? Number(modalProblemId.value) : null
  if (problemId == null) return
  try {
    const { data: res } = await sessionApi.getActiveSession()
    const session = res?.data
    if (session && session.problemId !== problemId) {
      closeModal()
      activeSessionPayload.value = {
        otherSessionId: session.sessionId,
        otherProblemId: session.problemId,
        targetProblemId: problemId,
      }
      showActiveSessionModal.value = true
      return
    }
  } catch (_) {}
  closeModal()
  const query = { from: 'roadmap' }
  if (selectedLevel.value != null) {
    query.level = String(selectedLevel.value)
  }
  router.push({ name: 'ide', params: { id: String(problemId) }, query })
}

function goToExistingProblem() {
  const payload = activeSessionPayload.value
  if (!payload) return
  showActiveSessionModal.value = false
  activeSessionPayload.value = null
  const query = { from: 'roadmap' }
  if (selectedLevel.value != null) {
    query.level = String(selectedLevel.value)
  }
  router.push({ name: 'ide', params: { id: String(payload.otherProblemId) }, query })
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
  const query = { from: 'roadmap' }
  if (selectedLevel.value != null) {
    query.level = String(selectedLevel.value)
  }
  router.push({ name: 'ide', params: { id: String(payload.targetProblemId) }, query })
}
</script>

<style scoped>
/* 툴팁 커스텀 스타일 */
:deep(.tooltip) {
  --tooltip-tail: 8px;
}
:deep(.tooltip:before) {
  background-color: #faea92 !important; /* farm 테마 노란색 */
  color: #4e3b2a !important;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 700;
  padding: 10px 32px; /* 너비와 높이를 키우기 위해 패딩 증가 */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px dashed #4E3B2A !important; /* 가장 어두운 브라운색 점선 테두리 */
  max-width: none !important; /* 가로 길이 제한 해제 */
  width: max-content !important; /* 텍스트 길이에 맞춤 */
}
:deep(.tooltip:after) {
  display: none !important;
}

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
  height: 9rem;
}
@media (min-width: 768px) {
  .cf-banner-inner {
    height: 10rem;
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
  right: 5.25rem;
  top: 3.25rem;
  bottom: auto;
  z-index: 5;
}

.cf-sun-btn {
  position: relative;
  width: 66px;
  height: 66px;
  border-radius: 9999px;
  border: none;
  cursor: pointer;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 30% 30%, #fff7cc 0%, #ffe082 35%, #ffb300 100%);
  box-shadow:
    0 10px 22px rgba(255, 179, 0, 0.35),
    0 2px 8px rgba(0, 0, 0, 0.12);
  transition: transform 0.15s ease, filter 0.15s ease, box-shadow 0.15s ease;
}

/* 빛살(레이) */
.cf-sun-btn::before {
  content: '';
  position: absolute;
  inset: -14px;
  border-radius: 9999px;
  background: repeating-conic-gradient(
    from 0deg,
    rgba(255, 224, 130, 0.95) 0 10deg,
    rgba(255, 224, 130, 0) 10deg 20deg
  );
  opacity: 0.9;
  /* 가운데는 비우고 바깥만 보이게 */
  -webkit-mask: radial-gradient(circle, transparent 0 58%, #000 59% 100%);
  mask: radial-gradient(circle, transparent 0 58%, #000 59% 100%);
  pointer-events: none;
}

/* 은은한 글로우 */
.cf-sun-btn::after {
  content: '';
  position: absolute;
  inset: -26px;
  border-radius: 9999px;
  background: radial-gradient(circle, rgba(255, 224, 130, 0.55), transparent 60%);
  pointer-events: none;
}

.cf-sun-btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
  box-shadow:
    0 14px 28px rgba(255, 179, 0, 0.38),
    0 3px 10px rgba(0, 0, 0, 0.12);
}
.cf-sun-btn:active {
  transform: translateY(0);
  filter: brightness(0.98);
}
.cf-sun-btn:focus-visible {
  outline: 3px solid rgba(255, 224, 130, 0.85);
  outline-offset: 3px;
}

.cf-sun-text {
  font-size: 13px;
  font-weight: 900;
  letter-spacing: -0.02em;
  color: rgba(78, 59, 42, 0.92); /* farm-brown-dark 계열 */
  text-shadow: 0 1px 0 rgba(255, 255, 255, 0.55);
  line-height: 1;
  user-select: none;
}
.cf-recommend-desc {
  font-size: 0.8rem;
  color: #555;
  line-height: 1.4;
}

.cf-roadmap {
  position: relative;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  height: 400px;
  max-height: 400px;
  border-radius: 22px;
  overflow: hidden;
  margin-bottom: 20px;
}
.cf-roadmap::after {
  content: '';
  position: absolute;
  inset: -2px; /* 이미지 경계선을 완전히 덮기 위해 살짝 바깥으로 확장 */
  /* 더 강력하고 넓은 그림자로 경계선을 완전히 지움 */
  box-shadow: 
    inset 0 0 80px 45px #FFF9E9,
    inset 0 0 120px 20px #FFF9E9;
  pointer-events: none;
  z-index: 1;
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
  transform: translateY(-200px);
  display: flex;
  justify-content: center;
  align-items: flex-end;
  padding: 0 10% 8%;
  gap: -2rem; /* 음수 간격을 주어 표지판들이 서로 겹치도록 설정 */
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
  color: var(--color-farm-yellow);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);
  line-height: 1.2;
  z-index: 1;
  transition: color 0.25s ease, text-shadow 0.25s ease;
  white-space: nowrap;
  text-align: center;
}
.cf-level:hover .cf-level-num {
  transform: translate(-50%, -50%);
  color: #ffeb3b; /* 원래의 노란색으로 복구 */
  text-shadow: 0 0 12px rgba(255, 235, 59, 0.7), 0 2px 4px rgba(0, 0, 0, 0.4);
}
.cf-level-cloud {
  width: 9rem;
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
  top: 0;
  left: 0;
  width: 100%;
  height: 9rem; /* 표지판 이미지 높이에 맞춤 */
  padding: 0;
  margin: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  border-radius: 12px;
  outline: none;
  z-index: 2;
}
.cf-level-btn:focus-visible {
  outline: 2px solid rgba(255, 235, 59, 0.9);
  outline-offset: 2px;
}

/* 세로형 문제 요약 정보 */
.cf-summary-vertical-enter-active,
.cf-summary-vertical-leave-active {
  transition: all 0.3s ease;
}
.cf-summary-vertical-enter-from,
.cf-summary-vertical-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px);
}

.cf-level-summary-vertical {
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  margin-top: 0.75rem;
  padding: 1rem;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(4px);
  width: 220px;
  text-align: center;
  z-index: 10;
  pointer-events: none;
}
.cf-level-summary-title {
  font-size: 1rem;
  font-weight: 900;
  color: #4e3b2a;
  margin: 0;
  line-height: 1.3;
}
.cf-level-summary-desc {
  font-size: 0.75rem;
  color: #6f5338;
  font-weight: 600;
}

@media (min-width: 768px) {
  .cf-level-num { font-size: 1.75rem; }
  .cf-level-cloud { width: 11rem; }
  .cf-level-btn { height: 11rem; }
  .cf-level-summary-vertical { width: 220px; }
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
  max-width: 26rem;
  /* 더 밝은 페이퍼 톤 */
  background: rgba(255, 253, 245, 0.97);
  /* 테두리 두께 줄임 */
  border: 2px solid rgba(74, 74, 41, 0.35);
  border-radius: 24px;
  /* 배경이 투명하므로 블러로 유리 느낌 */
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 10px 0 rgba(74, 74, 41, 0.08); /* 올리브색 계열 그림자 */
  cursor: default;
  overflow: hidden;
  position: relative;
}
.cf-modal-header {
  padding: 1.5rem 1.5rem 1rem;
  background: rgba(255, 253, 245, 0.85);
  border-bottom: 1px solid rgba(122, 92, 62, 0.18);
}
.cf-modal-label {
  display: inline-block;
  font-size: 0.75rem;
  font-weight: 900;
  color: #6B6B3A;
  background: rgba(245, 242, 232, 0.95);
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}
.cf-modal-title {
  font-size: 1.5rem;
  font-weight: 900;
  color: #4e3b2a;
  margin: 0;
  line-height: 1.2;
}
.cf-modal-body {
  padding: 1.25rem 1.5rem;
}
.cf-modal-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}
.cf-modal-info-card {
  background: #ffffff;
  padding: 0.75rem 1rem;
  border-radius: 16px;
  border: 2px solid rgba(245, 242, 232, 0.95);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  box-shadow: inset 0 -3px 0 #f0f0f0;
}
.cf-modal-info-card dt {
  font-size: 0.65rem;
  font-weight: 800;
  color: #a39485;
  text-transform: uppercase;
}
.cf-modal-info-card dd {
  margin: 0;
  font-size: 1rem;
  font-weight: 900;
  color: #4e3b2a;
}
.cf-modal-status-banner {
  margin-top: 1.25rem;
  padding: 0.85rem 1rem;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255, 253, 245, 0.9);
  border: 1px solid rgba(122, 92, 62, 0.18);
}
.cf-modal-status-label {
  font-size: 0.85rem;
  font-weight: 900;
  color: #6B6B3A;
}
.cf-modal-status-value {
  font-size: 0.85rem;
  font-weight: 900;
  padding: 0.35rem 0.75rem;
  border-radius: 10px;
}
.cf-modal-status-solved { background: #4ade80; color: white; border-bottom: 2px solid #16a34a; }
.cf-modal-status-tried { background: #fb923c; color: white; border-bottom: 2px solid #ea580c; }
.cf-modal-status-none { background: #94a3b8; color: white; border-bottom: 2px solid #475569; }

.cf-modal-actions {
  padding: 1rem 1.5rem 1.5rem;
  display: flex;
  gap: 0.75rem;
  background: rgba(255, 253, 245, 0.85);
  border-top: 1px solid rgba(122, 92, 62, 0.18);
}
.cf-modal-btn {
  flex: 1;
  padding: 0.75rem;
  font-size: 0.95rem;
  font-weight: 900;
  border-radius: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
}
.cf-modal-btn-close {
  background: #ffffff;
  color: #6B6B3A;
  border: 2px solid #6B6B3A;
  box-shadow: 0 3px 0 #6B6B3A;
}
.cf-modal-btn-close:hover {
  background: #fdf4e3;
  transform: translateY(-1px);
  box-shadow: 0 4px 0 #6B6B3A;
}
.cf-modal-btn-ide {
  background: #6B6B3A;
  color: white;
  border: none;
  box-shadow: 0 4px 0 #4A4A29;
}
.cf-modal-btn-ide:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 5px 0 #4A4A29;
}
.cf-modal-btn-ide:active:not(:disabled) {
  transform: translateY(1px);
  box-shadow: 0 1px 0 #4A4A29;
}
.cf-modal-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 애니메이션 효과 */
@keyframes bounce-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-15px); }
}
.animate-bounce-slow {
  animation: bounce-slow 3s infinite ease-in-out;
}
</style>
