<template>
  <div style="height: 400px;">
    <CodeEditor
      v-model:value="code"
      language="python"
      theme="vs-custom"
      :options="editorOptions"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { CodeEditor } from 'monaco-editor-vue3';
import * as monaco from 'monaco-editor';

const code = ref(`function hello() {
  console.log('Hello, Monaco Editor Vue3!');
}`);

const editorOptions = {
  fontSize: 14,
  minimap: { enabled: false },
  automaticLayout: true
};

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