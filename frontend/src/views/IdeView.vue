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
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="24" 
            height="24" 
            viewBox="0 0 14 14"
            class="carrot-icon"
          >
            <path 
              fill="currentColor" 
              fill-rule="evenodd" 
              d="M7.611.31c.348-.246.793-.406 1.27-.247c.491.164.774.52.9.92c.047.146.072.297.083.446a2.8 2.8 0 0 1 .871-.395c.58-.138 1.2-.023 1.728.505s.642 1.148.504 1.727c-.074.314-.22.608-.395.871q.226.014.446.083c.4.127.756.41.92.9c.16.478-.006.921-.254 1.263c-.245.338-.61.641-1 .904c-.653.44-1.469.826-2.185 1.115c.021.942-.342 1.924-1.27 2.852c-2.492 2.492-5.664 2.879-7.478 2.712a1.885 1.885 0 0 1-1.717-1.717c-.167-1.814.22-4.987 2.712-7.48c.918-.917 1.889-1.282 2.822-1.268c.288-.725.68-1.544 1.126-2.197c.267-.39.574-.753.917-.995M4.156 5.208c.662-.46 1.28-.523 1.831-.41c.743.153 1.451.647 2.009 1.205S9.048 7.269 9.2 8.013c.142.694.005 1.496-.855 2.357a8 8 0 0 1-1.892 1.4a5.27 5.27 0 0 0-1.98-1.84a.75.75 0 1 0-.723 1.313c.541.298.953.651 1.291 1.117a8.4 8.4 0 0 1-3.176.361a.635.635 0 0 1-.588-.587c-.13-1.418.138-3.811 1.784-5.849A4 4 0 0 1 4.519 7.8a.75.75 0 0 0 1.304-.74a5.5 5.5 0 0 0-1.667-1.851" 
              clip-rule="evenodd"
            />
          </svg>
        </button>
        <!-- 종 아이콘 -->
        <button class="ide-bell-button" aria-label="알림">
          <svg 
            xmlns="http://www.w3.org/2000/svg" 
            width="28" 
            height="28" 
            viewBox="0 0 24 24"
            class="bell-icon"
          >
            <path 
              fill="currentColor" 
              d="M17.133 12.632v-1.8a5.406 5.406 0 0 0-4.154-5.262A1 1 0 0 0 13 5.464V3.1a1 1 0 0 0-2 0v2.364a1 1 0 0 0 .021.106a5.406 5.406 0 0 0-4.154 5.262v1.8C6.867 15.018 5 15.614 5 16.807C5 17.4 5 18 5.538 18h12.924C19 18 19 17.4 19 16.807c0-1.193-1.867-1.789-1.867-4.175M8.823 19a3.453 3.453 0 0 0 6.354 0z"
            />
          </svg>
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
import MonacoEditor from '@/components/organisms/MonacoEditor.vue';

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

.carrot-icon {
  width: 1.5rem;
  height: 1.5rem;
  color: #FF8C42; /* 당근색 (주황색) */
  display: block;
}

.bell-icon {
  width: 1.75rem;
  height: 1.75rem;
  color: var(--color-farm-brown-dark);
  display: block;
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
