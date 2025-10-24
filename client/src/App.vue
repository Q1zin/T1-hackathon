<script setup>
import { ref, onMounted } from 'vue';
import ActivityHeatmap from './components/ActivityHeatmap.vue';
import apiClient from './api/client';

const activityData = ref([]);
const userEmail = ref('david.turner@elastic.co'); // Можно сделать динамическим
const loading = ref(true);
const error = ref(null);

onMounted(async () => {
  try {
    loading.value = true;
    error.value = null;

    // Получаем данные с API
    const response = await apiClient.getYearActivity(userEmail.value);

    // Преобразуем объект { "2025-01-10": 1 } в массив [{ date: "2025-01-10", count: 1 }]
    activityData.value = Object.entries(response.data).map(([date, count]) => ({
      date,
      count
    }));

    console.log('Loaded activity data:', activityData.value);
  } catch (err) {
    console.error('Failed to load activity data:', err);
    error.value = err.message;
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="app-container">
    <div v-if="loading" class="loading">
      Загрузка данных...
    </div>
    <div v-else-if="error" class="error">
      Ошибка: {{ error }}
    </div>
    <ActivityHeatmap v-else :data="activityData" />
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

.loading,
.error {
  color: #cbd5e1;
  font-size: 16px;
  text-align: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 16px;
  min-width: 300px;
}

.error {
  color: #fca5a5;
  border: 1px solid rgba(252, 165, 165, 0.3);
}

.loading {
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.6;
  }
}
</style>
