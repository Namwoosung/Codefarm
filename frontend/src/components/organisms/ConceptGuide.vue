<template>
  <div class="concept-guide">
    <!-- 헤더 -->
    <div class="flex items-center gap-2 mb-4 pb-3 border-b border-farm-brown/15">
      <iconify-icon icon="mdi:book-open-variant" class="text-2xl text-farm-olive"></iconify-icon>
      <h3 class="text-lg font-bold text-farm-brown-dark">문제 개념</h3>
    </div>
    
    <!-- 마크다운 콘텐츠 -->
    <div 
      class="markdown-content prose prose-sm max-w-none"
      v-html="renderedContent"
    ></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  content: {
    type: String,
    default: ''
  }
})

// marked 옵션 설정
marked.setOptions({
  breaks: true,
  gfm: true
})

const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked.parse(props.content)
})
</script>

<style scoped>
.concept-guide {
  background: linear-gradient(135deg, #fdfcfa 0%, #f9f7f2 100%);
  border: 1px solid rgba(122, 92, 62, 0.15);
  border-radius: 1rem;
  padding: 1.25rem;
}

/* 마크다운 스타일 */
.markdown-content :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: #4e3b2a;
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.markdown-content :deep(h2) {
  font-size: 1.125rem;
  font-weight: 700;
  color: #4e3b2a;
  margin-top: 1.25rem;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.markdown-content :deep(p) {
  color: #5a4a3a;
  line-height: 1.7;
  margin-bottom: 0.75rem;
}

.markdown-content :deep(strong) {
  color: #4e3b2a;
  font-weight: 600;
}

.markdown-content :deep(em) {
  color: #6b5b4b;
  font-style: italic;
}

.markdown-content :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(to right, transparent, rgba(122, 92, 62, 0.2), transparent);
  margin: 1rem 0;
}

.markdown-content :deep(pre) {
  background: #f5f2e8;
  border: 1px solid #e0dbd0;
  border-radius: 0.75rem;
  padding: 0.875rem 1rem;
  margin: 0.75rem 0;
  overflow-x: auto;
}

.markdown-content :deep(code) {
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 0.875rem;
  color: #4e3b2a;
}

.markdown-content :deep(blockquote) {
  background: linear-gradient(135deg, #fff9e6 0%, #fef3d0 100%);
  border-left: 4px solid #e8a945;
  border-radius: 0 0.75rem 0.75rem 0;
  padding: 0.875rem 1rem;
  margin: 0.75rem 0;
}

.markdown-content :deep(blockquote p) {
  margin-bottom: 0;
  color: #5a4a3a;
}

.markdown-content :deep(iconify-icon) {
  vertical-align: middle;
}
</style>
