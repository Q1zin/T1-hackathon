<template>
  <div class="team-productivity-stats">
    <div class="stats-header">
      <div class="year-selector">
        <button 
          class="year-button" 
          @click="changeYear(-1)"
          :disabled="selectedYear <= 2015"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <div class="year-display">{{ selectedYear }}</div>
        <button 
          class="year-button" 
          @click="changeYear(1)"
          :disabled="selectedYear >= 2025"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M6 4L10 8L6 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
    
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
import { ref, watch } from 'vue';
import ProductivityZones from './ProductivityZones.vue';

const selectedYear = ref(new Date().getFullYear());

const generateRandomZones = () => {
  return Array.from({ length: 10 }, () => Math.random());
};

const generateMonthsData = () => {
  return [
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
  ];
};

const monthsData = ref(generateMonthsData());

const changeYear = (delta) => {
  selectedYear.value += delta;
  monthsData.value = generateMonthsData();
};

watch(selectedYear, () => {
  monthsData.value = generateMonthsData();
});
</script>

<style scoped>
.team-productivity-stats {
  padding: 24px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.stats-header {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.year-selector {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 8px 16px;
  background: rgba(30, 41, 59, 0.4);
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.1);
}

.year-display {
  font-size: 18px;
  font-weight: 600;
  color: #cbd5e1;
  min-width: 60px;
  text-align: center;
}

.year-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: rgba(51, 65, 85, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.3s ease;
}

.year-button:hover:not(:disabled) {
  background: rgba(59, 130, 246, 0.3);
  border-color: rgba(59, 130, 246, 0.5);
  color: #60a5fa;
  transform: scale(1.05);
}

.year-button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
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
  color: #cbd5e1;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  transition: all 0.3s ease;
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
