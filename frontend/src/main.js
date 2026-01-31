import { createApp } from 'vue'
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'
import App from './App.vue'
import router from './router'
import { useIdeStore } from '@/stores/ide'

// UI 라이브러리
import './assets/style.css'
import PrimeVue from 'primevue/config'
import Aura from '@primeuix/themes/aura'
import Button from 'primevue/button'

// Iconify Web Component (<iconify-icon />)
import 'iconify-icon'

const app = createApp(App)
app.use(PrimeVue, {
  theme: {
    preset: Aura
  }
})
app.component('Button', Button)

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

app.use(pinia)
app.use(router)

app.mount('#app')

// persist 복원 후 IDE 로딩 플래그 초기화 (메인/기타 페이지에서 로딩 창 안 뜨게)
const ideStore = useIdeStore()
if (!router.currentRoute.value.path.startsWith('/ide/')) {
  ideStore.ideRouteLoading = false
}
