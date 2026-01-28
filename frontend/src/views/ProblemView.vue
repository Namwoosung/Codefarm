<template>
  <div class="min-h-screen bg-farm-cream">
    <div class="flex h-screen">
      <!-- 왼쪽: 문제 설명 영역 -->
      <div class="w-1/2 bg-farm-paper border-r border-farm-cream flex flex-col">
        <!-- 뒤로가기 버튼 -->
        <div class="p-4 border-b border-farm-cream">
          <button
            @click="$router.back()"
            class="flex items-center space-x-2 text-farm-brown-dark hover:text-farm-green transition-colors"
          >
            <iconify-icon icon="mdi:arrow-left" class="text-xl"></iconify-icon>
            <span>뒤로가기</span>
          </button>
        </div>

        <!-- 문제 설명 영역 (스크롤 가능) -->
        <div class="flex-1 overflow-y-auto p-6">
          <!-- 문제 번호 -->
          <div class="mb-4">
            <span class="text-farm-brown text-lg font-medium"># {{ problem?.problemId || '로딩 중...' }}</span>
          </div>

          <!-- 문제 제목 -->
          <h2 class="text-2xl font-bold text-farm-brown-dark mb-6">
            {{ problem?.title || '로딩 중...' }}
          </h2>

          <!-- 문제 정보 (점수, 시간 제한, 메모리 제한) -->
          <div class="space-y-3 mb-6">
            <div class="flex items-center space-x-2 text-farm-brown-dark">
              <iconify-icon icon="mdi:chart-line" class="text-xl text-farm-green"></iconify-icon>
              <span>획득 점수 {{ getDifficultyScore(problem?.difficulty) }}점</span>
            </div>
            <div class="flex items-center space-x-2 text-farm-brown-dark">
              <iconify-icon icon="mdi:clock-outline" class="text-xl text-farm-green"></iconify-icon>
              <span>실행 제한 시간 {{ problem?.timeLimit || 0 }}초</span>
            </div>
            <div class="flex items-center space-x-2 text-farm-brown-dark">
              <iconify-icon icon="mdi:harddisk" class="text-xl text-farm-green"></iconify-icon>
              <span>메모리 제한 {{ formatMemory(problem?.memoryLimit) }}</span>
            </div>
          </div>

          <!-- 문제 설명 -->
          <div class="mb-6">
            <div class="text-farm-brown-dark whitespace-pre-wrap leading-relaxed">
              {{ problem?.description || '문제 설명을 불러오는 중...' }}
            </div>
          </div>

          <!-- 예제 입출력 (있는 경우) -->
          <div v-if="problem?.exampleInput || problem?.exampleOutput" class="mb-6 space-y-4">
            <div>
              <h3 class="text-lg font-semibold text-farm-brown-dark mb-2">예제 입력</h3>
              <div class="bg-farm-cream p-4 rounded-lg font-mono text-sm text-farm-brown-dark">
                {{ problem.exampleInput }}
              </div>
            </div>
            <div>
              <h3 class="text-lg font-semibold text-farm-brown-dark mb-2">예제 출력</h3>
              <div class="bg-farm-cream p-4 rounded-lg font-mono text-sm text-farm-brown-dark">
                {{ problem.exampleOutput }}
              </div>
            </div>
          </div>
        </div>

        <!-- AI 선생님 채팅창 틀 -->
        <div class="border-t border-farm-cream p-6 bg-farm-paper">
          <div class="flex items-start space-x-3 mb-4">
            <div class="w-10 h-10 bg-farm-yellow rounded-full flex items-center justify-center flex-shrink-0">
              <iconify-icon icon="mdi:robot" class="text-xl text-farm-brown-dark"></iconify-icon>
            </div>
            <div class="flex-1">
              <p class="text-farm-brown-dark text-sm">
                도움이 필요하신가요? 어떤 부분에서 어렵다고 느끼셨나요?
              </p>
            </div>
          </div>
          
          <div class="relative">
            <textarea
              v-model="chatInput"
              placeholder="어떤 부분에서 어려움을 느꼈는지 적어주세요..."
              class="w-full p-3 border border-farm-cream rounded-lg bg-white text-farm-brown-dark placeholder-farm-brown resize-none focus:outline-none focus:ring-2 focus:ring-farm-green focus:border-transparent"
              rows="3"
            ></textarea>
            
            <div class="flex items-center justify-between mt-2">
              <span class="text-sm text-farm-brown">당근 수: {{ carrotCount }}/3</span>
              <button
                class="p-2 bg-farm-green text-white rounded-lg hover:bg-farm-green-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="!chatInput.trim() || carrotCount <= 0"
              >
                <iconify-icon icon="mdi:send" class="text-xl"></iconify-icon>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 오른쪽: 코드 에디터 영역 (Monaco Editor가 여기에 표시됨) -->
      <div class="w-1/2 bg-farm-paper">
        <!-- Monaco Editor는 기존 코드가 여기에 렌더링됩니다 -->
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getProblemDetail } from '@/api/problem'

const route = useRoute()
const problem = ref(null)
const chatInput = ref('')
const carrotCount = ref(3) // 당근 수는 나중에 API에서 가져올 예정

// 난이도에 따른 점수 계산 (임시)
const getDifficultyScore = (difficulty) => {
  const scoreMap = {
    'LEVEL1': 30,
    'LEVEL2': 50,
    'LEVEL3': 70,
    'LEVEL4': 100,
    'LEVEL5': 150
  }
  return scoreMap[difficulty] || 30
}

// 메모리 포맷팅
const formatMemory = (memoryMB) => {
  if (!memoryMB) return '0MiB'
  return `${memoryMB.toLocaleString()}MiB`
}

// 문제 상세 정보 로드
const loadProblem = async () => {
  try {
    const problemId = route.params.id
    const data = await getProblemDetail(problemId)
    problem.value = data.problem
    // TODO: userStatus, statistics도 필요시 사용
    // userStatus = data.userStatus
    // statistics = data.statistics
  } catch (error) {
    console.error('문제를 불러오는 중 오류가 발생했습니다:', error)
    // TODO: 에러 처리 UI 추가
  }
}

onMounted(() => {
  loadProblem()
})
</script>

<style scoped>
/* 스크롤바 스타일링 */
.overflow-y-auto::-webkit-scrollbar {
  width: 8px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: var(--color-farm-cream);
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: var(--color-farm-green-light);
  border-radius: 4px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: var(--color-farm-green);
}
</style>
