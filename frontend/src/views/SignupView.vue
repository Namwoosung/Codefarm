<template>
  <div class="signup-page">
    <h1>코드팜 회원가입 🌱</h1>
    <SignupForm />
  </div>
</template>

<script setup>
import SignupForm from '@/components/organisms/SignupForm.vue'
</script>

<style scoped>
.signup-page {
  max-width: 500px;
  margin: 50px auto;
  padding: 20px;
}
</style>
