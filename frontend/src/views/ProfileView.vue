<template>
  <div class="min-h-screen p-10 flex flex-col">
    <div class="max-w-7xl mx-auto w-full flex flex-col flex-1 min-h-0">
      <PageTitle title="프로필" />

      <div class="flex flex-col gap-6 md:flex-row flex-1 min-h-0">
        <!-- 좌측 사이드바 (1) -->
        <aside class="w-full md:w-auto md:flex-[1] md:min-w-0 md:sticky md:top-10 self-start">
          <div class="card bg-base-100 border border-base-200 rounded-2xl p-5">
            <p class="mb-4 text-sm font-semibold text-slate-600">Sidebar</p>
            <p>{{ user?.nickname }}'s Farm</p>
            <p>Lv.{{ user?.codingLevel }}</p>
            <button
              type="button"
              class="btn w-full mt-2 rounded-xl border border-base-300 bg-gradient-to-b from-white to-base-200 text-base-content font-bold tracking-tight shadow-sm hover:-translate-y-0.5 active:translate-y-0"
              @click="profile.reportList?.()"
            >
              내 리포트
            </button>

            <button
              type="button"
              class="btn w-full mt-2 rounded-xl border border-base-300 bg-gradient-to-b from-white to-base-200 text-base-content font-bold tracking-tight shadow-sm hover:-translate-y-0.5 active:translate-y-0"
              @click="profile.reportList?.()"
            >
              프로필 수정
            </button>
          </div>
        </aside>

        <!-- 우측 메인 (3) -->
        <main class="w-full md:w-auto md:flex-[3] md:min-w-0 h-full min-h-0">
          <div class="mb-4 h-[calc(100vh-200px)] border border-base-200 bg-base-100 p-6 overflow-y-auto rounded-2xl relative">
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useProfileStore } from '@/stores/profile'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'
import PageTitle from '@/components/atoms/PageTitle.vue'

const profile = useProfileStore()
const { user } = storeToRefs(profile)

onMounted(async () => {
  try {
    await profile.userinfo()
  } catch (err) {
    console.warn('[ProfileView] mounted fetch failed:', err)
  }
})
</script>
<style scoped>
/* 가로 스크롤바 숨기기 (선택 사항) */
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>

