<template>
  <div class="flex flex-col items-center justify-center min-h-screen gap-10 p-10">
    <div class="text-center">
      <h1 class="text-2xl font-mono mb-2">CODE FARM D2Coding 폰트 테스트12345</h1>
      <h1 class="font-sans text-xl">CODE FARM Toss Product Sans 폰트 테스트12345</h1>
      <p class="font-sans text-xl max-w-2xl mx-auto mt-4">
        퍼센트, 쉼표, 더하기, 빼기, 화살표 등 UI 요소로 활용되는 기호들의 가독성을 높여, 넓은 여백으로 디자인했죠. 또한 다른 글자와의 균형과 일관성을 고려.
      </p>
      <router-link to="/login">로그인</router-link>
      <div class="mt-6">
        <Button label="D2Coding 버튼" icon="pi pi-check" />
      </div>
    </div>

    <!-- 컬러 팔레트 섹션 -->
    <div class="w-full max-w-4xl p-8 bg-white rounded-2xl shadow-lg">
      <h2 class="text-2xl font-bold mb-6 text-gray-800">Theme Color Palette</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div v-for="color in themeColors" :key="color.name" class="flex flex-col gap-2">
          <div 
            :class="`h-24 w-full rounded-xl border border-gray-100 shadow-sm ${color.class}`"
          ></div>
          <div class="px-1">
            <p class="font-bold text-sm text-gray-700">{{ color.name }}</p>
            <p class="text-xs text-gray-500 font-mono">{{ color.hex }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Button from 'primevue/button';

const themeColors = [
  { name: 'Farm Cream', hex: '#F5F2E8', class: 'bg-farm-cream' },
  { name: 'Farm Paper', hex: '#FFFDF5', class: 'bg-farm-paper' },
  { name: 'Farm Yellow', hex: '#FFE082', class: 'bg-farm-yellow' },
  { name: 'Farm Point', hex: '#E07A5F', class: 'bg-farm-point' },
  { name: 'Farm Green Light', hex: '#B5D99C', class: 'bg-farm-green-light' },
  { name: 'Farm Green', hex: '#7BAE5F', class: 'bg-farm-green' },
  { name: 'Farm Green Dark', hex: '#5E8D48', class: 'bg-farm-green-dark' },
  { name: 'Farm Olive', hex: '#4A4A29', class: 'bg-farm-olive' },
  { name: 'Farm Brown', hex: '#7A5C3E', class: 'bg-farm-brown' },
  { name: 'Farm Brown Dark', hex: '#4E3B2A', class: 'bg-farm-brown-dark' },
];
</script>

<style scoped>
</style>
