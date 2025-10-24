<script setup>
import ActivityHeatmap from './components/ActivityHeatmap.vue';
</script>

<template>
  <div class="app-container">
    <ActivityHeatmap />
  </div>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
  background: linear-gradient(to bottom, #020617, #0f172a);
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
