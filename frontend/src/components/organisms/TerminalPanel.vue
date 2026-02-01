<template>
  <div class="terminal-panel">
    <div id="xterm-container">
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { Terminal } from '@xterm/xterm'
import { FitAddon } from '@xterm/addon-fit'
import '@xterm/xterm/css/xterm.css'

/** 터미널 상태: READY(입력 가능) | RUNNING(API 대기 중, 입력 차단) */
const mode = ref('READY')
/** 현재 줄에 입력 중인 문자열 */
const inputBuffer = ref('')
/** 서버로 보낼 전체 입력 (여러 줄, 실행 시 한 번에 전송) */
const fullInput = ref('')

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
    cursorBlink: false,
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
    },
    allowProposedApi: true
  })
  
  // 2. FitAddon 추가 (크기 자동 조정)
  fitAddon = new FitAddon()
  term.loadAddon(fitAddon)
  
  // 3. 터미널 컨테이너에 붙이기
  const container = document.getElementById('xterm-container')
  if (container) {
    term.open(container)

    // stdin은 모달에서 받으므로 터미널 입력 비활성화 (출력 전용)
    term.onData(() => {})
    
    // 4. 터미널 크기 조정 (약간의 지연을 두어 DOM이 완전히 렌더링된 후)
    setTimeout(() => {
      try {
        fitAddon.fit()
        // 초기 안내 메시지 출력
        term.write('코드를 실행해보려면 \'실행하기\' 버튼을,\r\n')
        term.write('최종 코드를 제출하려면 \'제출하기\' 버튼을 눌러주세요.\r\n')
        term.write('그만 풀고 싶다면, \'탈주하기\' 버튼을 눌러주세요.\r\n')
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
    
    // 복사만 허용 (Ctrl+C), 붙여넣기·타이핑은 입력 막혀 있음
    term.attachCustomKeyEventHandler((e) => {
      if (e.ctrlKey && e.key === 'c') {
        const sel = term.getSelection()
        if (sel) {
          e.preventDefault()
          navigator.clipboard?.writeText(sel).catch(() => {})
        }
      }
      if (e.ctrlKey && e.key === 'v') {
        e.preventDefault()
      }
      return true
    })
    
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

/** xterm에 맞게 줄바꿈 정규화 (\n → \r\n) */
function normalizeLineEndings(text) {
  if (text == null || typeof text !== 'string') return ''
  return text.replace(/\r?\n/g, '\r\n')
}

defineExpose({
  /** 서버로 보낼 전체 입력 (현재 줄 포함). 실행 시 API input 필드에 전달 */
  getFullInput: () => {
    const line = inputBuffer.value
    return fullInput.value + (line ? line + '\n' : '')
  },
  /** 입력 버퍼 초기화 (실행 완료 후 호출, 프롬프트/커서 출력 없음) */
  clearInputAndShowPrompt: () => {
    fullInput.value = ''
    inputBuffer.value = ''
    if (term) term.write('\r\n')
    mode.value = 'READY'
  },
  /** RUNNING: 입력 차단, READY: 입력 가능 */
  setRunning: (running) => {
    mode.value = running ? 'RUNNING' : 'READY'
  },
  write: (text) => {
    if (term) term.write(normalizeLineEndings(text))
  },
  /** stderr 출력 (빨간색) */
  writeStderr: (text) => {
    if (term && text) term.write(ANSI_RED + normalizeLineEndings(text) + ANSI_RESET)
  },
  clear: () => {
    if (term) {
      term.clear()
      fullInput.value = ''
      inputBuffer.value = ''
      mode.value = 'READY'
    }
  },
  terminal: term
})
</script>

<style scoped>
.terminal-panel {
  width: 100%;
  height: 100%;
  min-height: 120px;
  background-color: var(--color-farm-paper);
  border-top: 1px solid var(--color-farm-cream);
  display: flex;
  flex-direction: column;
  flex: 1;
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
  user-select: text;
}

/* xterm.js 스타일 오버라이드 */
:deep(.xterm) {
  width: 100% !important;
  height: 100% !important;
  font-family: "D2Coding", "Courier New", monospace !important;
  font-weight: bold !important;
  padding: 0 !important;
  user-select: text;
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

/* 출력 전용 터미널: 커서 숨김 */
:deep(.xterm-cursor) {
  visibility: hidden;
}
</style>
