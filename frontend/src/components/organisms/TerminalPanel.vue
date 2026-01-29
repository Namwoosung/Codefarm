<template>
  <div class="terminal-panel">
    <div id="xterm-container">
    </div>
  </div>
</template>

<script setup>
import { onMounted, onUnmounted, nextTick } from 'vue'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'

let term = null
let fitAddon = null

const resizeHandler = () => {
  if (fitAddon) {
    setTimeout(() => {
      fitAddon.fit()
    }, 100)
  }
}

onMounted(async () => {
  await nextTick()
  
  // 1. 터미널 객체 생성
  term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    fontFamily: '"D2Coding", "Courier New", monospace',
    fontWeight: 'bold',
    letterSpacing: 0,
    lineHeight: 1.2,
    theme: {
      background: '#F5F2E8',
      foreground: '#4E3B2A',
      cursor: '#7BAE5F',
      cursorAccent: '#7BAE5F'
    }
  })
  
  // 2. FitAddon 추가 (크기 자동 조정)
  fitAddon = new FitAddon()
  term.loadAddon(fitAddon)
  
  // 3. 터미널 컨테이너에 붙이기
  const container = document.getElementById('xterm-container')
  if (container) {
    term.open(container)
    
    // 4. 터미널 크기 조정 (약간의 지연을 두어 DOM이 완전히 렌더링된 후)
    setTimeout(() => {
      try {
        fitAddon.fit()
      } catch (error) {
        console.error('Terminal fit error:', error)
      }
    }, 200)
    
    // 6. 윈도우 리사이즈 시 크기 조정
    window.addEventListener('resize', resizeHandler)
    
    // 7. ResizeObserver로 컨테이너 크기 변경 감지
    const resizeObserver = new ResizeObserver(() => {
      if (fitAddon) {
        setTimeout(() => {
          fitAddon.fit()
        }, 50)
      }
    })
    resizeObserver.observe(container)
    
    // cleanup을 위해 저장
    container._resizeObserver = resizeObserver
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', resizeHandler)
  const container = document.getElementById('xterm-container')
  if (container && container._resizeObserver) {
    container._resizeObserver.disconnect()
  }
  if (term) {
    term.dispose()
  }
})

// FR-CODE-005-1: stderr는 빨간색으로 표시 (ANSI)
const ANSI_RED = '\x1b[31m'
const ANSI_RESET = '\x1b[0m'

defineExpose({
  write: (text) => {
    if (term) term.write(text)
  },
  /** stderr 출력 (빨간색) */
  writeStderr: (text) => {
    if (term && text) term.write(ANSI_RED + text + ANSI_RESET)
  },
  clear: () => {
    if (term) term.clear()
  },
  terminal: term
})
</script>

<style scoped>
.terminal-panel {
  width: 100%;
  height: 250px;
  min-height: 200px;
  background-color: var(--color-farm-paper);
  border-top: 1px solid var(--color-farm-cream);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: relative;
}

#xterm-container {
  width: 100%;
  height: 100%;
  padding: 1rem;
  box-sizing: border-box;
  overflow: hidden;
  position: relative;
  display: block;
}

/* xterm.js 스타일 오버라이드 */
:deep(.xterm) {
  width: 100% !important;
  height: 100% !important;
  font-family: "D2Coding", "Courier New", monospace !important;
  font-weight: bold !important;
  padding: 0 !important;
}

:deep(.xterm-viewport) {
  background-color: var(--color-farm-paper) !important;
  overflow-y: auto !important;
}

:deep(.xterm-screen) {
  background-color: var(--color-farm-paper) !important;
  width: 100% !important;
}

:deep(.xterm-scroll-area) {
  overflow: hidden !important;
}

:deep(.xterm .xterm-viewport) {
  font-family: "D2Coding", "Courier New", monospace !important;
  font-weight: bold !important;
}

:deep(.xterm .xterm-rows) {
  font-family: "D2Coding", "Courier New", monospace !important;
  font-weight: bold !important;
}

:deep(.xterm .xterm-rows > div) {
  font-weight: bold !important;
}

:deep(.xterm-cursor-layer) {
  z-index: 2;
}
</style>
