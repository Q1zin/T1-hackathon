<template>
  <div class="team-productivity-stats">
    <div class="months-grid">
      <div
        v-for="(month, index) in monthsData"
        :key="index"
        class="month-item"
      >
        <ProductivityZones :zones="month.zones" />
        <div class="month-label">{{ month.name }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import ProductivityZones from './ProductivityZones.vue';

const generateRandomZones = () => {
  return Array.from({ length: 10 }, () => Math.random());
};

const monthsData = ref([
  { name: 'Январь', zones: generateRandomZones() },
  { name: 'Февраль', zones: generateRandomZones() },
  { name: 'Март', zones: generateRandomZones() },
  { name: 'Апрель', zones: generateRandomZones() },
  { name: 'Май', zones: generateRandomZones() },
  { name: 'Июнь', zones: generateRandomZones() },
  { name: 'Июль', zones: generateRandomZones() },
  { name: 'Август', zones: generateRandomZones() },
  { name: 'Сентябрь', zones: generateRandomZones() },
  { name: 'Октябрь', zones: generateRandomZones() },
  { name: 'Ноябрь', zones: generateRandomZones() },
  { name: 'Декабрь', zones: generateRandomZones() }
]);
</script>

<style scoped>
.team-productivity-stats {
  padding: 24px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.months-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

.month-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.3);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.month-item:hover {
  background: rgba(30, 41, 59, 0.5);
  transform: translateY(-2px);
}

.month-label {
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.month-item:hover .month-label {
  color: #cbd5e1;
}

@media (max-width: 768px) {
  .months-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }
}

@media (max-width: 480px) {
  .months-grid {
    grid-template-columns: 1fr;
  }
}
</style>
