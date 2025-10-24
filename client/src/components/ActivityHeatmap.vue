<template>
  <div class="activity-heatmap">
    <div class="year-selector">
      <button @click="changeYear(-1)" class="year-button">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M10 12L6 8L10 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
      <span class="year-text">{{ selectedYear }}</span>
      <button @click="changeYear(1)" class="year-button">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path d="M6 12L10 8L6 4" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
    
    <div class="heatmap-container">
      <div class="days-labels">
        <div class="day-label">Пн</div>
        <div class="day-label"></div>
        <div class="day-label">Ср</div>
        <div class="day-label"></div>
        <div class="day-label">Пт</div>
        <div class="day-label"></div>
        <div class="day-label">Вс</div>
      </div>
      
      <div class="heatmap-content">
        <div class="months-labels">
          <div
            v-for="month in monthLabels"
            :key="month.name"
            class="month-label"
          >
            {{ month.name }}
          </div>
        </div>
        
        <div class="weeks-grid">
          <div
            v-for="(week, weekIndex) in weeks"
            :key="weekIndex"
            class="week-column"
          >
            <div
              v-for="(day, dayIndex) in week"
              :key="dayIndex"
              class="day-cell"
              :class="getIntensityClass(day.count)"
              @mouseenter="onDayHover($event, day)"
              @mouseleave="hoveredDay = null"
            >
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div 
      v-if="hoveredDay"
      class="tooltip"
      :style="tooltipStyle"
    >
      <div class="tooltip-date">{{ formatDate(hoveredDay.date) }}</div>
      <div class="tooltip-count">
        {{ hoveredDay.count }} {{ getCommitsWord(hoveredDay.count) }}
      </div>
    </div>
    
    <div class="legend">
      <span class="legend-text">Меньше</span>
      <div class="legend-scale">
        <div class="legend-cell intensity-0"></div>
        <div class="legend-cell intensity-1"></div>
        <div class="legend-cell intensity-2"></div>
        <div class="legend-cell intensity-3"></div>
        <div class="legend-cell intensity-4"></div>
      </div>
      <span class="legend-text">Больше</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  }
});

const hoveredDay = ref(null);
const tooltipStyle = ref({});
const selectedYear = ref(new Date().getFullYear());

const changeYear = (delta) => {
  const newYear = selectedYear.value + delta;
  if (newYear >= 2020 && newYear <= 2030) {
    selectedYear.value = newYear;
  }
};

// Генерация данных за год
const generateYearData = () => {
  const data = {};
  const today = new Date();
  
  // Используем переданные данные или генерируем случайные
  if (props.data && props.data.length > 0) {
    for (const item of props.data) {
      data[item.date] = item.count;
    }
  } else {
    // Генерация случайных данных для демонстрации
    const startDate = new Date(selectedYear.value, 0, 1);
    const endDate = new Date(selectedYear.value, 11, 31);
    const currentDate = new Date(startDate);
    
    // Если выбран текущий год, генерируем только до сегодня
    const maxDate = selectedYear.value === today.getFullYear() ? today : endDate;
    
    while (currentDate.getTime() <= maxDate.getTime()) {
      const dateStr = currentDate.toISOString().split('T')[0];
      data[dateStr] = Math.random() > 0.3 ? Math.floor(Math.random() * 20) : 0;
      currentDate.setDate(currentDate.getDate() + 1);
    }
  }
  
  return data;
};

const activityData = computed(() => generateYearData());

// Формирование недель - всегда 53 недели
const weeks = computed(() => {
  const result = [];
  const WEEKS_COUNT = 53; // Фиксированное количество недель
  
  // Начинаем с 1 января выбранного года
  const startDate = new Date(selectedYear.value, 0, 1);
  
  // Находим ближайший понедельник на или после 1 января
  const startDay = startDate.getDay();
  let daysToMonday = 0;
  if (startDay === 0) {
    daysToMonday = 1; // Воскресенье -> Понедельник
  } else if (startDay !== 1) {
    daysToMonday = 8 - startDay; // Вторник-Суббота -> следующий понедельник
  }
  startDate.setDate(startDate.getDate() + daysToMonday);
  
  let currentDate = new Date(startDate);
  
  // Генерируем всегда 53 недели
  for (let weekIndex = 0; weekIndex < WEEKS_COUNT; weekIndex++) {
    const week = [];
    for (let i = 0; i < 7; i++) {
      const dateStr = currentDate.toISOString().split('T')[0];
      week.push({
        date: dateStr,
        count: activityData.value[dateStr] || 0,
        dayOfWeek: i
      });
      currentDate.setDate(currentDate.getDate() + 1);
    }
    result.push(week);
  }
  
  return result;
});

// Формирование меток месяцев с фиксированными позициями
const monthLabels = computed(() => {
  // Фиксированная ширина для каждого месяца (примерно 4-5 недель)
  const monthNames = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
  
  return monthNames.map((name) => ({
    name,
    weeks: 4.33 // Среднее количество недель в месяце (52 / 12)
  }));
});

const getMonthName = (monthIndex) => {
  const months = ['Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн', 'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек'];
  return months[monthIndex];
};

const getIntensityClass = (count) => {
  if (count === 0) return 'intensity-0';
  if (count <= 3) return 'intensity-1';
  if (count <= 6) return 'intensity-2';
  if (count <= 9) return 'intensity-3';
  return 'intensity-4';
};

const getDayTitle = (day) => {
  const date = new Date(day.date);
  const formatted = date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
  return `${formatted}: ${day.count} ${getCommitsWord(day.count)}`;
};

const getCommitsWord = (count) => {
  if (count % 10 === 1 && count % 100 !== 11) return 'коммит';
  if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) return 'коммита';
  return 'коммитов';
};

const formatDate = (dateStr) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' });
};

const onDayHover = (event, day) => {
  hoveredDay.value = day;
  const rect = event.target.getBoundingClientRect();
  tooltipStyle.value = {
    left: `${rect.left + rect.width / 2}px`,
    top: `${rect.top - 10}px`
  };
};
</script>

<style scoped>
.activity-heatmap {
  padding: 20px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 16px;
  display: inline-block;
}

.year-selector {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 20px;
}

.year-button {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 8px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s ease;
}

.year-button:hover {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(96, 165, 250, 0.5);
  color: #60a5fa;
  transform: scale(1.05);
}

.year-button:active {
  transform: scale(0.95);
}

.year-text {
  font-size: 18px;
  font-weight: 600;
  color: #cbd5e1;
  min-width: 80px;
  text-align: center;
}

.heatmap-container {
  display: flex;
  gap: 8px;
}

.days-labels {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding-top: 26px;
}

.day-label {
  height: 12px;
  font-size: 10px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  line-height: 12px;
}

.heatmap-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.months-labels {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  width: 100%;
  height: 18px;
  margin-bottom: 4px;
}

.month-label {
  font-size: 10px;
  color: #94a3b8;
  text-align: center;
}

.weeks-grid {
  display: flex;
  gap: 3px;
}

.week-column {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.day-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  transition: all 0.2s ease;
  cursor: pointer;
}

.day-cell:hover {
  transform: scale(1.3);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

.intensity-0 {
  background: rgba(51, 65, 85, 0.3);
}

.intensity-1 {
  background: #0e4429;
}

.intensity-2 {
  background: #006d32;
}

.intensity-3 {
  background: #26a641;
}

.intensity-4 {
  background: #39d353;
}

.legend {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  justify-content: flex-end;
}

.legend-text {
  font-size: 10px;
  color: #94a3b8;
}

.legend-scale {
  display: flex;
  gap: 3px;
}

.legend-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.tooltip {
  position: fixed;
  transform: translate(-50%, -100%);
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 8px;
  padding: 8px 12px;
  pointer-events: none;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(10px);
  animation: tooltipFadeIn 0.2s ease-out;
}

@keyframes tooltipFadeIn {
  from {
    opacity: 0;
    transform: translate(-50%, -100%) translateY(5px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, -100%) translateY(0);
  }
}

.tooltip-date {
  font-size: 11px;
  color: #cbd5e1;
  font-weight: 500;
  margin-bottom: 2px;
}

.tooltip-count {
  font-size: 13px;
  color: #60a5fa;
  font-weight: 600;
}
</style>
