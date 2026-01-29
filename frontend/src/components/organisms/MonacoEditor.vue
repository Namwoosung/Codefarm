<template>
  <div class="h-full">
    <CodeEditor
      v-model:value="code"
      language="python"
      theme="vs-custom"
      :options="editorOptions"
      @change="handleCodeChange"
    />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { CodeEditor } from 'monaco-editor-vue3'
import * as monaco from 'monaco-editor'
import { useIdeStore } from '@/stores/ide'

const route = useRoute()
const ideStore = useIdeStore()

// 현재 문제 ID 기준으로 코드 표시/저장 (문제마다 다른 코드 유지)
const code = computed({
  get: () => ideStore.getCode(route.params.id),
  set: (v) => ideStore.updateCode(route.params.id, v)
})

const editorOptions = {
  fontSize: 14,
  minimap: { enabled: false },
  automaticLayout: true,
  wordWrap: 'on',
  wrappingIndent: 'indent'
}

const handleCodeChange = (value) => {
  ideStore.updateCode(route.params.id, value)
}

onMounted(() => {
  // vs 테마를 기반으로 배경색만 변경
  monaco.editor.defineTheme('vs-custom', {
    base: 'vs',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#F5F2E8' // 원하는 배경색으로 변경
    }
  });
});
</script>