<template>
  <div>
    <p>{{ card.cardId }}</p>
    <p>{{ card.cardName }}</p>
  </div>
</template>

<script setup>
const props = defineProps({
  card: {
    type: Object,
    required: true
  }
})
</script>

<style lang="css" scoped>
.card {
  width: 100%;
  height: 100%;
  background-color: #fff;
  border-radius: 10px;
  box-shadow: 0 0 10px 0 rgba(0, 0, 0, 0.1);
}
</style>