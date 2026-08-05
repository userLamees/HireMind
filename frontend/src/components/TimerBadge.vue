<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  seconds: { type: Number, default: 180 },
})

const emit = defineEmits(['expired'])

const remaining = ref(props.seconds)
let handle = null

const label = computed(() => {
  const safe = Math.max(0, remaining.value)
  const mins = String(Math.floor(safe / 60)).padStart(2, '0')
  const secs = String(safe % 60).padStart(2, '0')
  return `${mins}:${secs}`
})

// Under a minute left is worth flagging visually.
const urgent = computed(() => remaining.value <= 60)

function stop() {
  if (handle) {
    clearInterval(handle)
    handle = null
  }
}

onMounted(() => {
  handle = setInterval(() => {
    remaining.value -= 1
    if (remaining.value <= 0) {
      stop()
      emit('expired')
    }
  }, 1000)
})

onBeforeUnmount(stop)

defineExpose({ stop, remaining })
</script>

<template>
  <div class="timer" :class="{ 'timer--urgent': urgent }" role="timer" aria-live="off">
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <circle cx="12" cy="13" r="8" stroke="currentColor" stroke-width="2" />
      <path d="M12 9v4l2.5 2M9 2h6" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
    <span class="timer__value">{{ label }}</span>
  </div>
</template>

<style scoped>
.timer {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: rgba(52, 196, 188, 0.08);
  color: var(--accent);
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  font-size: 0.95rem;
  transition: color 0.2s ease, border-color 0.2s ease;
}

.timer svg {
  width: 17px;
  height: 17px;
}

.timer--urgent {
  color: var(--danger);
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(248, 113, 113, 0.1);
  animation: pulse 1.4s ease-in-out infinite;
}

@keyframes pulse {
  50% {
    opacity: 0.6;
  }
}

@media (prefers-reduced-motion: reduce) {
  .timer--urgent {
    animation: none;
  }
}
</style>
