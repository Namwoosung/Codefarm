<template>
  <div class="min-h-screen flex flex-col bg-farm-cream font-sans text-farm-brown-dark">
    <!-- Navigation Bar -->
    <header class="sticky top-0 z-50 bg-farm-cream/80 backdrop-blur-md border-b border-farm-brown/10 px-6 py-4">
      <div class="max-w-7xl mx-auto flex items-center justify-between">
        <!-- Logo: CODE FARM in wooden bubbles -->
        <div class="flex items-center gap-1">
          <div v-for="char in 'CODEFARM'" :key="char" 
               class="w-10 h-10 flex items-center justify-center bg-farm-yellow rounded-full border-2 border-farm-brown shadow-[0_4px_0_#7A5C3E] text-farm-brown font-bold text-xl first:ml-0"
               :class="{ 'ml-4': char === 'F' }">
            {{ char }}
          </div>
        </div>

        <!-- Navigation Links -->
        <nav class="hidden md:flex items-center gap-8">
          <router-link to="/" class="font-bold hover:text-farm-green transition-colors">메인페이지</router-link>
          <router-link to="/curriculum" class="font-bold hover:text-farm-green transition-colors">커리큘럼</router-link>
        </nav>

        <!-- Auth Buttons -->
        <div class="flex items-center gap-4">
          <router-link to="/signup" class="text-sm font-bold hover:underline">회원가입</router-link>
          <button class="wood-sign text-sm px-6 py-2">로그인</button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-grow">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-farm-brown-dark text-farm-cream/60 py-10 px-6">
      <div class="max-w-7xl mx-auto text-center">
        <div class="flex flex-wrap justify-center gap-6 mb-6 text-xs font-bold">
          <a href="#" class="hover:text-farm-cream">개인정보 처리방침</a>
          <a href="#" class="hover:text-farm-cream">서비스 이용약관</a>
          <a href="#" class="hover:text-farm-cream">쿠키 기본 설정</a>
        </div>
        <p class="text-xs mb-2">© 2026 CODE FARM. All rights reserved.</p>
        <p class="text-xs">Team: 디버그파이터스</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>

<style scoped>
.wood-sign {
  background-color: var(--color-farm-wood);
  color: white;
  padding: 8px 16px;
  border-radius: 8px;
  box-shadow: 0 4px 0 var(--color-farm-wood-dark);
  font-weight: bold;
  transition: all 0.1s;
}

.wood-sign:active {
  transform: translateY(2px);
  box-shadow: 0 2px 0 var(--color-farm-wood-dark);
}
</style>
