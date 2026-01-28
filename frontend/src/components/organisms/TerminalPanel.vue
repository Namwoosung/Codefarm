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

onMounted(async () => {
  await nextTick()
  
  // 1. 터미널 객체 생성
  term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    fontFamily: '"D2Coding", "Courier New", monospace',
    fontWeight: 'bold', /* 굵은 글씨로 변경 */
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
    
    // 4. 터미널 크기 조정
    fitAddon.fit()
    
    // 5. 잘 떴는지 확인용 글자 한 줄 써보기
    term.write('Hello World!\r\n')
    term.write('Loading...\r\n')
    
    // 6. 윈도우 리사이즈 시 크기 조정
    window.addEventListener('resize', () => {
      if (fitAddon) {
        fitAddon.fit()
      }
    })
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', () => {
    if (fitAddon) {
      fitAddon.fit()
    }
  })
  if (term) {
    term.dispose()
  }
})

// 외부에서 사용할 수 있도록 expose
defineExpose({
  write: (text) => {
    if (term) {
      term.write(text)
    }
  },
  clear: () => {
    if (term) {
      term.clear()
    }
  },
  terminal: term
})
</script>

<style scoped>
.terminal-panel {
  width: 100%;
  height: 200px;
  min-height: 200px;
  max-height: 300px;
  background-color: var(--color-farm-paper);
  border-top: 1px solid var(--color-farm-cream);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

#xterm-container {
  width: 100%;
  height: 100%;
  padding: 1rem;
}

/* xterm.js 스타일 오버라이드 */
:deep(.xterm) {
  height: 100%;
  font-family: "D2Coding", "Courier New", monospace !important;
  font-weight: bold !important;
}

:deep(.xterm-viewport) {
  background-color: var(--color-farm-paper) !important;
}

:deep(.xterm-screen) {
  background-color: var(--color-farm-paper) !important;
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
</style>
