<template>
  <div class="markdown-text" :class="[contentClass, { 'markdown-text--concept': variant === 'concept' }]" v-html="html" />
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'

const props = defineProps({
  text: { type: String, default: '' },
  contentClass: { type: String, default: '' },
  /** 'concept': 커리큘럼 개념 스타일 */
  variant: { type: String, default: 'default' }
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
    const content = normalizeMarkdown(t)
    const raw = marked(content)
    return DOMPurify.sanitize(raw, {
      ALLOWED_TAGS: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'strong', 'em', 'ul', 'ol', 'li', 'br', 'hr', 'a', 'blockquote', 'code', 'pre'],
      ADD_ATTR: ['class']
    })
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

/* variant=concept: 커리큘럼 개념 스타일 (마크다운 기본) */
.markdown-text--concept :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4e3b2a;
  margin: 0 0 0.75rem;
}
.markdown-text--concept :deep(h2) {
  font-size: 1.125rem;
  font-weight: 700;
  color: #4e3b2a;
  margin: 1.25rem 0 0.5rem;
}
.markdown-text--concept :deep(h2:first-child),
.markdown-text--concept :deep(h3:first-child),
.markdown-text--concept :deep(h4:first-child),
.markdown-text--concept :deep(h5:first-child),
.markdown-text--concept :deep(h6:first-child) {
  margin-top: 0;
}
.markdown-text--concept :deep(h3) {
  font-size: 1rem;
  font-weight: 700;
  color: #4e3b2a;
  margin: 1rem 0 0.5rem;
}
.markdown-text--concept :deep(h4) {
  font-size: 0.9375rem;
  font-weight: 700;
  color: #4e3b2a;
  margin: 0.875rem 0 0.5rem;
}
.markdown-text--concept :deep(h5) {
  font-size: 0.875rem;
  font-weight: 700;
  color: #4e3b2a;
  margin: 0.75rem 0 0.5rem;
}
.markdown-text--concept :deep(h6) {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #4e3b2a;
  margin: 0.75rem 0 0.5rem;
}
.markdown-text--concept :deep(p) {
  color: #5a4a3a;
  line-height: 1.7;
  margin: 0 0 0.75rem;
}
.markdown-text--concept :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(122, 92, 62, 0.2), transparent);
  margin: 1rem 0;
}
.markdown-text--concept :deep(pre) {
  background: #f5f2e8;
  border: 1px solid #e0dbd0;
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
  margin: 0.75rem 0;
  overflow-x: auto;
}
.markdown-text--concept :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.875rem;
  color: #4e3b2a;
}
.markdown-text--concept :deep(blockquote) {
  background: linear-gradient(135deg, #fff9e6 0%, #fef3d0 100%);
  border-left: 4px solid #e8a945;
  border-radius: 0 0.75rem 0.75rem 0;
  padding: 0.875rem 1rem;
  margin: 0.75rem 0;
}
.markdown-text--concept :deep(blockquote p) {
  margin-bottom: 0;
  color: #5a4a3a;
}
</style>
