<template>
  <div class="language-chart">
    <div class="chart-container">
      <svg class="donut-chart" :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
        <g :transform="`translate(${size / 2}, ${size / 2}) rotate(-90)`">
          <path
            v-for="(segment, index) in segments"
            :key="index"
            :d="segment.path"
            fill="transparent"
            :stroke="segment.color"
            :stroke-width="strokeWidth"
            class="chart-segment"
            @mouseenter="hoveredIndex = index"
            @mouseleave="hoveredIndex = null"
            :class="{ 'hovered': hoveredIndex === index }"
          />
        </g>
      </svg>
      
    </div>
    
    <div class="legend">
      <div
        v-for="(lang, index) in languages"
        :key="index"
        class="legend-item"
        @mouseenter="hoveredIndex = index"
        @mouseleave="hoveredIndex = null"
        :class="{ 'hovered': hoveredIndex === index }"
      >
        <div class="legend-color" :style="{ background: lang.color }"></div>
        <div class="legend-name">{{ lang.name }}</div>
        <div class="legend-percentage">{{ lang.percentage }}%</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  size: {
    type: Number,
    default: 280
  }
});

const languageData = [
  { name: 'JavaScript', lines: 15420, color: '#f7df1e' },
  { name: 'Python', lines: 12380, color: '#3776ab' },
  { name: 'TypeScript', lines: 9850, color: '#3178c6' },
  { name: 'Java', lines: 7200, color: '#007396' },
  { name: 'Go', lines: 5100, color: '#00add8' },
  { name: 'Rust', lines: 3050, color: '#ce422b' },
  { name: 'Остальное', lines: 8000, color: '#64748b' }
];

const hoveredIndex = ref(null);
const strokeWidth = 60;
const radius = (props.size / 2) - (strokeWidth / 2) - 10;
const circumference = 2 * Math.PI * radius;

const totalLines = computed(() => {
  return languageData.reduce((sum, lang) => sum + lang.lines, 0);
});

const languagesWithPercentage = computed(() => {
  return languageData.map(lang => ({
    ...lang,
    percentage: ((lang.lines / totalLines.value) * 100).toFixed(1)
  }));
});

const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
  const angleInRadians = (angleInDegrees * Math.PI) / 180;
  return {
    x: centerX + (radius * Math.cos(angleInRadians)),
    y: centerY + (radius * Math.sin(angleInRadians))
  };
};

const describeArc = (x, y, radius, startAngle, endAngle) => {
  const start = polarToCartesian(x, y, radius, endAngle);
  const end = polarToCartesian(x, y, radius, startAngle);
  const largeArcFlag = endAngle - startAngle <= 180 ? '0' : '1';
  
  return [
    'M', start.x, start.y,
    'A', radius, radius, 0, largeArcFlag, 0, end.x, end.y
  ].join(' ');
};

const segments = computed(() => {
  let currentAngle = 0;
  
  return languagesWithPercentage.value.map(lang => {
    const percentage = Number.parseFloat(lang.percentage);
    const angle = (percentage / 100) * 360;
    const path = describeArc(0, 0, radius, currentAngle, currentAngle + angle);
    
    const segment = {
      path,
      color: lang.color,
      startAngle: currentAngle,
      endAngle: currentAngle + angle
    };
    
    currentAngle += angle;
    return segment;
  });
});

const languages = languagesWithPercentage;
</script>

<style scoped>
.language-chart {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 16px;
  align-items: center;
  max-width: 600px;
}

.chart-container {
  position: relative;
  flex-shrink: 0;
}

.donut-chart {
  transform: rotate(0deg);
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
}

.chart-segment {
  transition: all 0.3s ease;
  cursor: pointer;
}

.chart-segment.hovered {
  filter: brightness(2) drop-shadow(0 0 8px currentColor);
  stroke-width: 80;
}

.legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  background: rgba(30, 41, 59, 0.3);
  border-radius: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
}

.legend-item:hover,
.legend-item.hovered {
  background: rgba(30, 41, 59, 0.6);
  transform: translateX(2px);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
  box-shadow: 0 0 6px currentColor;
}

.legend-name {
  font-size: 13px;
  font-weight: 500;
  color: #cbd5e1;
  flex: 1;
}

.legend-percentage {
  font-size: 14px;
  font-weight: 600;
  color: #60a5fa;
}

@media (max-width: 768px) {
  .language-chart {
    flex-direction: column;
    gap: 24px;
  }
}
</style>
