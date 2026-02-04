<template>
  <div class="min-h-screen p-10 flex flex-col">
    <div class="max-w-7xl mx-auto w-full flex flex-col flex-1 min-h-0">

      <div class="flex flex-col gap-6 md:flex-row flex-1 min-h-0">
        <aside class="w-full md:w-auto md:flex-[1] md:min-w-0 self-start">
          <div class="relative">
            <div
              class="pointer-events-none absolute left-3 top-3 z-10 h-3 w-3 rounded-full border border-farm-brown/25 bg-gradient-to-b from-farm-cream to-farm-brown/30 shadow-[0_1px_2px_rgba(0,0,0,0.25)] before:content-[''] before:absolute before:left-1/2 before:top-1/2 before:h-[1.5px] before:w-2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:rounded-full before:bg-farm-brown/60 after:content-[''] after:absolute after:left-1/2 after:top-1/2 after:h-[1.5px] after:w-2 after:-translate-x-1/2 after:-translate-y-1/2 after:-rotate-45 after:rounded-full after:bg-farm-brown/60"
            ></div>
            <div
              class="pointer-events-none absolute right-3 top-3 z-10 h-3 w-3 rounded-full border border-farm-brown/25 bg-gradient-to-b from-farm-cream to-farm-brown/30 shadow-[0_1px_2px_rgba(0,0,0,0.25)] before:content-[''] before:absolute before:left-1/2 before:top-1/2 before:h-[1.5px] before:w-2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:rounded-full before:bg-farm-brown/60 after:content-[''] after:absolute after:left-1/2 after:top-1/2 after:h-[1.5px] after:w-2 after:-translate-x-1/2 after:-translate-y-1/2 after:-rotate-45 after:rounded-full after:bg-farm-brown/60"
            ></div>
            <div
              class="pointer-events-none absolute bottom-3 left-3 z-10 h-3 w-3 rounded-full border border-farm-brown/25 bg-gradient-to-b from-farm-cream to-farm-brown/30 shadow-[0_1px_2px_rgba(0,0,0,0.25)] before:content-[''] before:absolute before:left-1/2 before:top-1/2 before:h-[1.5px] before:w-2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:rounded-full before:bg-farm-brown/60 after:content-[''] after:absolute after:left-1/2 after:top-1/2 after:h-[1.5px] after:w-2 after:-translate-x-1/2 after:-translate-y-1/2 after:-rotate-45 after:rounded-full after:bg-farm-brown/60"
            ></div>
            <div
              class="pointer-events-none absolute bottom-3 right-3 z-10 h-3 w-3 rounded-full border border-farm-brown/25 bg-gradient-to-b from-farm-cream to-farm-brown/30 shadow-[0_1px_2px_rgba(0,0,0,0.25)] before:content-[''] before:absolute before:left-1/2 before:top-1/2 before:h-[1.5px] before:w-2 before:-translate-x-1/2 before:-translate-y-1/2 before:rotate-45 before:rounded-full before:bg-farm-brown/60 after:content-[''] after:absolute after:left-1/2 after:top-1/2 after:h-[1.5px] after:w-2 after:-translate-x-1/2 after:-translate-y-1/2 after:-rotate-45 after:rounded-full after:bg-farm-brown/60"
            ></div>

            <div
              class="card rounded-2xl border border-farm-cream bg-farm-paper p-7 shadow-lg rotate-[-1.5deg] origin-top"
            >
              <p class="font-extrabold tracking-tight text-farm-brown-dark">{{ user?.nickname }}'s Farm</p>
              <div class="divider my-3 opacity-60"></div>
              <div class="flex flex-wrap gap-2">
                <span class="badge badge-lg border border-farm-brown/20 bg-farm-cream text-farm-brown-dark">
                  {{ user?.email }}
                </span>
                <span class="badge badge-lg border border-farm-brown/20 bg-farm-cream text-farm-brown-dark">
                  {{ user?.age }}살
                </span>
                <span class="badge badge-lg border border-farm-brown/20 bg-farm-cream text-farm-brown-dark">
                  Lv.{{ user?.codingLevel }}
                </span>
                <span class="badge badge-lg border border-farm-brown/20 bg-farm-cream text-farm-brown-dark">
                  {{ user?.point }}p
                </span>
              </div>
            <button
              type="button"
              class="btn btn-sm w-full my-6 rounded-xl bg-farm-olive text-farm-paper font-bold tracking-tight shadow-sm hover:brightness-110 active:brightness-95"
              @click="openEditModal"
            >
              프로필 수정
            </button>
            </div>
          </div>
        </aside>

        <main class="w-full md:w-auto md:flex-[3] md:min-w-0 h-full min-h-0">
          <NotebookFlip class="h-[calc(100vh-200px)] w-full" />
        </main>
      </div>
    </div>

    <ProfileEditModal
      :show="showEditModal"
      :user="user"
      :is-saving="isSaving"
      @close="showEditModal = false"
      @submit="handleSubmitEdit"
    />
  </div>
</template>

<script setup>
import { useProfileStore } from '@/stores/profile'
import { storeToRefs } from 'pinia'
import { onMounted, ref } from 'vue'
import NotebookFlip from '@/components/organisms/NotebookFlip.vue'
import ProfileEditModal from '@/components/organisms/ProfileEditModal.vue'

const profile = useProfileStore()
const { user } = storeToRefs(profile)
const showEditModal = ref(false)
const isSaving = ref(false)

onMounted(async () => {
  try {
    await profile.userinfo()
  } catch (err) {
    console.warn('[ProfileView] mounted fetch failed:', err)
  }
})

const openEditModal = () => {
  if (!user.value) return
  showEditModal.value = true
}

const handleSubmitEdit = async (payload) => {
  isSaving.value = true
  try {
    await profile.updateUser(payload)
    showEditModal.value = false
  } catch (err) {
    console.log(err)
  } finally {
    isSaving.value = false
  }
}

</script>

