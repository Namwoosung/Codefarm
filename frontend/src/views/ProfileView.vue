<template>
  <div class="min-h-screen p-10 flex flex-col">
    <div class="max-w-7xl mx-auto w-full flex flex-col flex-1 min-h-0">
      <PageTitle title="프로필" />

      <div class="flex flex-col gap-6 md:flex-row flex-1 min-h-0">
        <!-- 좌측 사이드바 (1) -->
        <aside class="w-full md:basis-1/4 md:shrink-0 md:sticky md:top-10 self-start">
          <div class="rounded-2xl border border-slate-200 bg-white p-5 ">
            <p class="mb-4 text-sm font-semibold text-slate-600">Sidebar</p>
            <p>{{ user?.nickname }}'s Farm</p>
            <p>Lv.{{ user?.codingLevel }}</p>
            <button class="sidebar-btn w-full" @click="profile.reportList">
              내 카드
            </button>
            <button class="sidebar-btn w-full" @click="profile.reportList">
              카드뽑기
            </button>
            <button class="sidebar-btn w-full" @click="profile.reportList">
              내 리포트
            </button>
          </div>
        </aside>

        <!-- 우측 메인 (3) -->
        <main class="w-full md:basis-3/4 h-full min-h-0">
          <div class="main border border-slate-200 bg-white p-6 h-full overflow-auto">
            <p>CardList</p>
            <div v-for="card in cards.cards" :key="card.cardId">
              <hr />
              <p>{{ card.length }}</p>
              <p>{{ card.cardId }}</p>
              <CardDetail :card="card" />
            </div>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useProfileStore } from '@/stores/profile'
import { storeToRefs } from 'pinia'
import { onMounted, ref } from 'vue'
import PageTitle from '@/components/atoms/PageTitle.vue'
import CardDetail from '@/components/organisms/CardDetail.vue'

const profile = useProfileStore()
const { user, cards, reports } = storeToRefs(profile)

onMounted(async () => {
  try {
    await profile.userinfo()
    await profile.cardList()
    // await profile.reportList()
  } catch (err) {
    console.warn('[ProfileView] mounted fetch failed:', err)
  }
})

// const showCard = async (id) => {
//   await profile.cardDetail(id)
// }
</script>

<style scoped>
.main {
  margin-bottom: 1rem;
  height: 50vh;
}

.sidebar-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0.5rem 0;
  gap: 0.5rem;

  padding: 0.75rem 1rem;
  border-radius: 12px;
  border: 1px solid rgba(15, 23, 42, 0.12);

  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
  color: #0f172a;
  font-weight: 700;
  letter-spacing: -0.01em;

  transition:
    transform 120ms ease,
    box-shadow 120ms ease,
    background 120ms ease,
    border-color 120ms ease;
}

.sidebar-btn:hover {
  transform: translateY(-1px);
}

.sidebar-btn:active {
  transform: translateY(0);
  box-shadow:
    0 1px 0 rgba(15, 23, 42, 0.05),
    0 10px 22px rgba(15, 23, 42, 0.12);
}

.sidebar-btn:focus-visible {
  outline: none;
  border-color: rgba(79, 70, 229, 0.55);
  box-shadow:
    0 0 0 4px rgba(99, 102, 241, 0.25),
    0 14px 28px rgba(15, 23, 42, 0.14);
}

.sidebar-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow:
    0 1px 0 rgba(15, 23, 42, 0.04),
    0 6px 14px rgba(15, 23, 42, 0.06);
}
</style>
