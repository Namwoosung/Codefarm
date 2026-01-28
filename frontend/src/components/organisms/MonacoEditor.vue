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
import { ref, onMounted, watch } from 'vue';
import { CodeEditor } from 'monaco-editor-vue3';
import * as monaco from 'monaco-editor';
import { useIdeStore } from '@/stores/ide';

const ideStore = useIdeStore();

// store에서 초기 코드 가져오기 (저장된 코드가 있으면 사용, 없으면 기본값)
const code = ref(ideStore.code || `function hello() {
  console.log('Welcome to CodeFarm!');
}`);

const editorOptions = {
  fontSize: 14,
  minimap: { enabled: false },
  automaticLayout: true,
  wordWrap: 'on', // 가로 스크롤 방지 - 긴 줄은 자동으로 다음 줄로
  wrappingIndent: 'indent' // 줄바꿈 시 들여쓰기 유지
};

// 코드 변경 시 store에 실시간 업데이트
const handleCodeChange = (value) => {
  ideStore.updateCode(value);
};

// code ref 변경 시에도 store 업데이트 (v-model과 동기화)
watch(code, (newValue) => {
  ideStore.updateCode(newValue);
}, { immediate: true });

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