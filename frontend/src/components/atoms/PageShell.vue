<template>
  <div ref="rootEl" class="page-shell">
    <!-- 실제 페이지는 먼저 마운트하되, 준비 전에는 숨김 -->
    <div :style="contentStyle">
      <component :is="component" />
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  component: { type: [Object, Function], required: true },
  routeKey: { type: String, required: true },
  revealMode: { type: String, default: 'default' }, // default | fast
})

const emit = defineEmits(['ready'])

const rootEl = ref(null)
const revealed = ref(false)

const contentStyle = computed(() => {
  // 레이아웃 계산은 하되 시각적으로는 숨김 -> "완성본"으로 한 번에 공개
  return revealed.value
    ? {}
    : {
        visibility: 'hidden',
        pointerEvents: 'none',
      }
})

const sleepRaf = () => new Promise((resolve) => requestAnimationFrame(() => resolve()))

const withTimeout = (p, ms) =>
  Promise.race([
    p,
    new Promise((resolve) => setTimeout(resolve, ms)),
  ])

async function waitForFonts(maxMs = 180) {
  // eslint-disable-next-line no-undef
  const fonts = typeof document !== 'undefined' ? document.fonts : null
  if (!fonts || !fonts.ready) return
  await withTimeout(fonts.ready, maxMs)
}

async function waitForDomQuiet(el, quietMs = 90, maxMs = 450) {
  if (!el) return

  let lastMutationAt = Date.now()
  let done = false
  const obs = new MutationObserver(() => {
    lastMutationAt = Date.now()
  })
  obs.observe(el, { subtree: true, childList: true, attributes: true, characterData: true })

  const start = Date.now()
  while (!done) {
    await withTimeout(Promise.resolve(), 0)
    const now = Date.now()
    if (now - lastMutationAt >= quietMs) done = true
    if (now - start >= maxMs) done = true
    // 너무 바쁘지 않게 양보
    await sleepRaf()
  }

  obs.disconnect()
}

async function waitForImages(el, maxMs = 650) {
  if (!el) return
  const imgs = Array.from(el.querySelectorAll('img'))
    // lazy 로딩은 "첫 완성본" 기준에서 제외(스크롤/노출 시 로드)
    .filter((img) => (img.getAttribute('loading') ?? '').toLowerCase() !== 'lazy')

  if (imgs.length === 0) return

  const start = Date.now()
  await Promise.all(
    imgs.map(async (img) => {
      const remain = Math.max(0, maxMs - (Date.now() - start))
      if (remain <= 0) return

      // 이미 로드된 경우 decode 시도
      if (img.complete && img.naturalWidth > 0) {
        if (typeof img.decode === 'function') {
          try {
            await withTimeout(img.decode(), remain)
          } catch {
            // ignore
          }
        }
        return
      }

      // 로드 대기 (error도 완료로 간주)
      await withTimeout(
        new Promise((resolve) => {
          const onDone = () => {
            img.removeEventListener('load', onDone)
            img.removeEventListener('error', onDone)
            resolve()
          }
          img.addEventListener('load', onDone, { once: true })
          img.addEventListener('error', onDone, { once: true })
        }),
        remain
      )
    })
  )
}

async function prepareAndReveal() {
  revealed.value = false
  await nextTick()

  // 초기 마운트/스타일 계산 안정화
  await sleepRaf()
  await sleepRaf()

  // 빠른 모드: 완성본 대기(폰트/DOM quiet/이미지)를 최소화해서 즉시 노출
  if (props.revealMode === 'fast') {
    revealed.value = true
    emit('ready')
    return
  }

  const el = rootEl.value
  await waitForFonts(180)
  await waitForDomQuiet(el, 90, 450)
  await waitForImages(el, 650)

  revealed.value = true
  emit('ready')
}

onMounted(() => {
  prepareAndReveal()
})

watch(
  () => props.routeKey,
  () => {
    prepareAndReveal()
  }
)

onBeforeUnmount(() => {
  // safety: nothing to cleanup (observers are local)
})
</script>

<style scoped>
.page-shell {
  width: 100%;
  height: 100%;
}
</style>

