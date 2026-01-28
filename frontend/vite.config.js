import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import tailwindcss from '@tailwindcss/vite'
import monacoEditorPlugin from 'vite-plugin-monaco-editor'

export default defineConfig({
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag === 'iconify-icon'
        }
      }
    }),
    vueDevTools(),
    tailwindcss(),
    // 플러그인이 워커 생성을 자동으로 처리합니다.
    (monacoEditorPlugin.default || monacoEditorPlugin)({
      languages: ['python'] // 필요한 언어만 설정
    }),
  ],
  server: {
    proxy: {
      '/api/v1/': {
        target: 'http://i14b109.p.ssafy.io:80',
        changeOrigin: true,
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // 수동 optimizeDeps와 manualChunks는 삭제했습니다. 
  // Vite가 기본적으로 처리하는 방식이 현재 프로젝트 상황에서 가장 빠릅니다.
})