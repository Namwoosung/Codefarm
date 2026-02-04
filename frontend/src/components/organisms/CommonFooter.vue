<template>
  <footer class="footer-with-pattern bg-farm-brown-dark py-8 mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
      <div class="flex flex-col items-center space-y-4 text-farm-cream">
        <!-- 링크 영역 -->
        <div class="flex flex-wrap justify-center gap-4 text-sm">
          <a href="#" class="text-farm-cream hover:text-farm-yellow transition-colors">개인 정보 처리 방침</a>
          <span class="text-farm-cream/50">|</span>
          <a href="#" class="text-farm-cream hover:text-farm-yellow transition-colors">사이트 이용 약관</a>
          <span class="text-farm-cream/50">|</span>
          <a href="#" class="text-farm-cream hover:text-farm-yellow transition-colors">쿠키 기본 설정</a>
        </div>
        
        <!-- 저작권 문구 -->
        <p class="text-sm text-farm-cream">© 2026 All rights reserved.</p>
        
        <!-- 팀 정보 -->
        <p class="text-sm text-farm-cream">team 아이디어니까</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
</script>

<style scoped>
.footer-with-pattern {
  position: relative;
}
.footer-with-pattern::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: url('../../assets/common/patterns/brick-wall.svg');
  background-repeat: repeat;
  background-size: 42px 44px;
  opacity: 0.12;
  pointer-events: none;
  z-index: 0;
}
</style>
