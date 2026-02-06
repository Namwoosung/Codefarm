<template>
  <div class="markdown-text" :class="contentClass" v-html="html" />
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  text: { type: String, default: '' },
  contentClass: { type: String, default: '' }
})

// marked 옵션: breaks=true → 단일 줄바꿈(\n)을 <br>로 변환
marked.setOptions({ breaks: true })

// 선생님 피드백 형식에 맞춰 줄바꿈 추가
// - ### 헤딩, "결과 - ", "앞으로 생각해볼 것 - ", "다음에 해볼 것 - " → 섹션 구분
// - ". - " → 문장 끝 뒤 새 리스트 항목
function normalizeMarkdown(text) {
  return text
    .replace(/\s+(#{1,6}\s)/g, '\n\n$1')
    .replace(/결과\s+-\s+/g, '결과\n\n- ')
    .replace(/앞으로 생각해볼 것\s+-\s+/g, '앞으로 생각해볼 것\n\n- ')
    .replace(/다음에 해볼 것\s+-\s+/g, '다음에 해볼 것\n\n- ')
    .replace(/\.\s+-\s+/g, '.\n- ')  // "체크해봐. - 같은 실수가" → 리스트 항목 분리
}

const html = computed(() => {
  const t = props.text
  if (!t || typeof t !== 'string') return ''
  try {
    const raw = marked(normalizeMarkdown(t))
    return DOMPurify.sanitize(raw, { ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'a', 'blockquote', 'code', 'pre'] })
  } catch {
    return ''
  }
})
</script>

<style scoped>
.markdown-text {
  word-break: keep-all; /* 한글 등 CJK 단어 중간 줄바꿈 방지 */
}
.markdown-text :deep(h3) {
  font-size: 1rem;
  font-weight: 700;
  color: var(--color-farm-green-dark);
  margin: 1rem 0 0.5rem;
}
.markdown-text :deep(h3:first-child) {
  margin-top: 0;
}
.markdown-text :deep(strong) {
  font-weight: 700;
  color: var(--color-farm-brown-dark);
}
.markdown-text :deep(ul) {
  margin: 0.5rem 0;
  padding-left: 1.25rem;
  list-style-type: disc;
}
.markdown-text :deep(li) {
  margin: 0.25rem 0;
}
.markdown-text :deep(p) {
  margin: 0.5rem 0;
}
.markdown-text :deep(p:first-child) {
  margin-top: 0;
}
</style>
