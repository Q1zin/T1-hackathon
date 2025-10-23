<template>
  <div class="productivity-zones">
    <div
      v-for="(value, index) in zones"
      :key="index"
      class="zone-bar"
      :style="{ opacity: value }"
    ></div>
  </div>
</template>

<script setup>
defineProps({
  zones: {
    type: Array,
    default: () => [0.1, 0.3, 0.5, 0.7, 0.9, 0.8, 0.6, 0.4, 0.2, 0.1],
    validator: (value) => {
      return value.length === 10 && value.every(v => v >= 0 && v <= 1);
    }
  }
});
</script>

<style scoped>
.productivity-zones {
  display: inline-flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
  border-radius: 16px;
  box-shadow: 
    0 4px 6px -1px rgba(0, 0, 0, 0.3),
    0 2px 4px -1px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 0 rgba(148, 163, 184, 0.1);
}

.zone-bar {
  width: 120px;
  height: 8px;
  background: linear-gradient(
    90deg,
    #60a5fa 0%,
    #3b82f6 50%,
    #2563eb 100%
  );
  border-radius: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 0 15px rgba(59, 130, 246, 0.4),
    inset 0 1px 2px rgba(255, 255, 255, 0.2),
    inset 0 -1px 2px rgba(0, 0, 0, 0.2);
  position: relative;
}

.zone-bar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 50%;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.3) 0%,
    rgba(255, 255, 255, 0) 100%
  );
  border-radius: 6px 0 0 6px;
  pointer-events: none;
}

.zone-bar:hover {
  transform: translateX(4px) scale(1.05);
  box-shadow: 
    0 6px 12px rgba(59, 130, 246, 0.5),
    inset 0 1px 2px rgba(255, 255, 255, 0.3);
}
</style>
