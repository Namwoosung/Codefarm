<template>
  <div class="ide-container">
    <!-- 기능 바: Navbar 밑 -->
    <div class="ide-toolbar">
      <!-- 왼쪽: 뒤로가기 -->
      <button class="ide-back-button" @click="handleBack">
        <i class="pi pi-arrow-left"></i>
        <span>뒤로가기</span>
      </button>

      <!-- 오른쪽: 당근 3개 + 종 아이콘 -->
      <div class="ide-toolbar-right">
        <!-- 당근 아이콘 3개 -->
        <button
          v-for="i in 3"
          :key="i"
          class="ide-carrot-button"
          aria-label="당근"
        >
          <CarrotIcon />
        </button>
        <!-- 종 아이콘 -->
        <button class="ide-bell-button" aria-label="알림">
          <BellIcon />
        </button>
      </div>
    </div>

    <!-- 좌우 분할 레이아웃 -->
    <div class="ide-layout">
      <!-- 왼쪽 패널: 문제 설명 영역 -->
      <aside class="ide-panel-left">
        <div class="ide-panel-content">
          <ProblemPanel />
        </div>
      </aside>

      <!-- 오른쪽 패널: 에디터 영역 -->
      <main class="ide-panel-right">
        <div class="ide-editor-container">
          <MonacoEditor />
        </div>
        
        <!-- 실행/제출 버튼 영역 -->
        <div class="ide-action-buttons">
          <button class="ide-submit-button" @click="handleSubmit">
            <span class="play-icon">▷</span>
            <span>제출하기</span>
          </button>
          <button class="ide-run-button" @click="handleRun">
            <span class="play-icon">▷</span>
            <span>실행하기</span>
          </button>
          <button class="ide-escape-button" @click="handleEscape">
            <EscapeIcon :size="20" />
            <span>탈주하기</span>
          </button>
        </div>
        
        <TerminalPanel ref="terminalPanel" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import MonacoEditor from '@/components/organisms/MonacoEditor.vue'
import ProblemPanel from '@/components/organisms/ProblemPanel.vue'
import TerminalPanel from '@/components/organisms/TerminalPanel.vue'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'
import BellIcon from '@/components/atoms/BellIcon.vue'
import EscapeIcon from '@/components/atoms/EscapeIcon.vue'

const router = useRouter()
const terminalPanel = ref(null)

const handleBack = () => {
  if (confirm('진짜 이 페이지를 벗어나시겠습니까?')) {
    router.push('/')
  }
}

const handleSubmit = () => {
  // TODO: 제출 기능 구현
  console.log('제출하기')
}

const handleRun = () => {
  // TODO: 실행 기능 구현
  if (terminalPanel.value) {
    terminalPanel.value.write('코드를 실행합니다...\r\n')
  }
  console.log('실행하기')
}

const handleEscape = () => {
  // TODO: 탈주 기능 구현
  if (confirm('정말 탈주하시겠습니까?')) {
    router.push('/')
  }
}
</script>

<style scoped>
.ide-container {
  width: 100%;
  height: calc(100vh - 4rem); /* 헤더 높이 제외 */
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background-color: var(--color-farm-paper);
}

/* 기능 바 스타일 */
.ide-toolbar {
  width: 100%;
  height: 3.5rem; /* 56px */
  background-color: var(--color-farm-paper);
  border-bottom: 1px solid var(--color-farm-cream);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  flex-shrink: 0;
}

.ide-back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  color: var(--color-farm-brown-dark);
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 0.2s;
}

.ide-back-button:hover {
  color: var(--color-farm-green);
}

.ide-back-button i {
  font-size: 1rem;
}

.ide-toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.ide-carrot-button,
.ide-bell-button {
  padding: 0.5rem;
  color: var(--color-farm-brown-dark);
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}


.ide-carrot-button:hover,
.ide-bell-button:hover {
  color: var(--color-farm-green);
  background-color: var(--color-farm-cream);
}

.ide-layout {
  display: flex;
  flex-direction: column;
  width: 100%;
  flex: 1;
  overflow: hidden;
}

/* 데스크톱: 좌우 분할 */
@media (min-width: 768px) {
  .ide-layout {
    flex-direction: row;
  }
}

.ide-panel-left {
  width: 100%;
  height: 50%;
  background-color: var(--color-farm-paper);
  border-right: 1px solid var(--color-farm-cream);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 데스크톱: 왼쪽 패널 너비 - 정확히 50% */
@media (min-width: 768px) {
  .ide-panel-left {
    width: 50%;
    height: 100%;
    flex: 0 0 50%;
    flex-shrink: 0;
  }
}

.ide-panel-content {
  width: 100%;
  height: 100%;
  padding: 1.5rem;
}

.ide-panel-right {
  width: 100%;
  height: 50%;
  background-color: var(--color-farm-paper);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 데스크톱: 오른쪽 패널 너비 - 정확히 50% */
@media (min-width: 768px) {
  .ide-panel-right {
    width: 50%;
    height: 100%;
    flex: 0 0 50%;
    flex-shrink: 0;
  }
}

.ide-editor-container {
  width: 100%;
  flex: 1;
  position: relative;
  min-height: 0; /* flexbox에서 overflow를 위해 필요 */
}

/* 실행/제출 버튼 영역 */
.ide-action-buttons {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background-color: var(--color-farm-paper);
  border-top: 1px solid var(--color-farm-cream);
  border-bottom: 1px solid var(--color-farm-cream);
  flex-shrink: 0;
  justify-content: flex-start; /* 왼쪽 정렬 */
}

.ide-submit-button {
  width: 119px; /* 디자인 목업 기준 */
  padding: 0.5rem 1.25rem;
  background: linear-gradient(90deg, #7A5C3E 0%, #CDFF86 100%);
  color: white;
  border: none;
  border-radius: 18px; /* 매우 둥근 모서리 */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 36px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  flex-shrink: 0;
}

.ide-submit-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
}

.ide-submit-button .play-icon {
  font-size: 0.875rem;
  color: white;
  font-weight: bold;
  line-height: 1;
}

.ide-run-button {
  width: 119px; /* 제출하기와 동일한 크기 */
  padding: 0.5rem 1.25rem;
  background-color: white;
  color: var(--color-farm-brown-dark);
  border: 1px solid #E0E0E0;
  border-radius: 18px; /* 매우 둥근 모서리 */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 36px;
  flex-shrink: 0;
}

.ide-run-button:hover {
  background-color: #FAFAFA;
  border-color: var(--color-farm-green);
}

.ide-run-button .play-icon {
  font-size: 0.875rem;
  color: var(--color-farm-brown-dark);
  font-weight: bold;
  line-height: 1;
}

.ide-escape-button {
  width: auto;
  min-width: 100px;
  padding: 0.5rem 1rem;
  background-color: white;
  color: var(--color-farm-brown-dark);
  border: 1px solid #E0E0E0;
  border-radius: 18px; /* 매우 둥근 모서리 */
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  height: 36px;
  flex-shrink: 0;
}

.ide-escape-button:hover {
  background-color: #FAFAFA;
  border-color: var(--color-farm-point);
  color: var(--color-farm-point);
}


/* 스크롤바 스타일링 */
.ide-panel-content::-webkit-scrollbar {
  width: 8px;
}

.ide-panel-content::-webkit-scrollbar-track {
  background: var(--color-farm-cream);
}

.ide-panel-content::-webkit-scrollbar-thumb {
  background: var(--color-farm-green-light);
  border-radius: 4px;
}

.ide-panel-content::-webkit-scrollbar-thumb:hover {
  background: var(--color-farm-green);
}
</style>
