<template>
  <div style="height: 400px;">
    <CodeEditor
      v-model:value="code"
      language="python"
      theme="vs"
      :options="editorOptions"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { CodeEditor } from 'monaco-editor-vue3';

const code = ref(`function hello() {
  console.log('Hello, Monaco Editor Vue3!');
}`);

const editorOptions = {
  fontSize: 14,
  minimap: { enabled: true },
  automaticLayout: true
};
</script>