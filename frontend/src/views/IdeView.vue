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
          <!-- 여기에 ProblemPanel 컴포넌트가 들어갈 영역 -->
          <slot name="problem-panel"></slot>
        </div>
      </aside>

      <!-- 오른쪽 패널: 에디터 영역 -->
      <main class="ide-panel-right">
        <div class="ide-editor-container">
          <!-- 여기에 MonacoEditor 컴포넌트가 들어갈 영역 -->
          <MonacoEditor />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import MonacoEditor from '@/components/organisms/MonacoEditor.vue'
import CarrotIcon from '@/components/atoms/CarrotIcon.vue'
import BellIcon from '@/components/atoms/BellIcon.vue'

const router = useRouter()

const handleBack = () => {
  router.back()
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
  overflow-y: auto;
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
  height: 100%;
  position: relative;
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
