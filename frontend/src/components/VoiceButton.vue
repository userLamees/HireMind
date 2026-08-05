<script setup>
import { onBeforeUnmount, ref } from 'vue'

const emit = defineEmits(['transcript'])

// Web Speech API — Chrome/Edge/Safari only. When it is missing the button is
// not rendered at all, since voice input is optional.
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
const supported = Boolean(SpeechRecognition)

const listening = ref(false)
let recognition = null

function build() {
  const instance = new SpeechRecognition()
  instance.continuous = true
  instance.interimResults = false
  instance.lang = 'en-US'

  instance.onresult = (event) => {
    let text = ''
    for (let i = event.resultIndex; i < event.results.length; i += 1) {
      if (event.results[i].isFinal) text += event.results[i][0].transcript
    }
    if (text.trim()) emit('transcript', text.trim())
  }

  instance.onend = () => {
    listening.value = false
  }

  instance.onerror = () => {
    listening.value = false
  }

  return instance
}

function toggle() {
  if (listening.value) {
    recognition?.stop()
    listening.value = false
    return
  }

  recognition = recognition || build()
  try {
    recognition.start()
    listening.value = true
  } catch {
    // start() throws if it is already running; nothing useful to do here.
    listening.value = false
  }
}

onBeforeUnmount(() => recognition?.stop())
</script>

<template>
  <button
    v-if="supported"
    type="button"
    class="voice"
    :class="{ 'voice--on': listening }"
    :title="listening ? 'Stop recording' : 'Answer by voice'"
    :aria-pressed="listening"
    @click="toggle"
  >
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
      <rect x="9" y="3" width="6" height="11" rx="3" stroke="currentColor" stroke-width="2" />
      <path
        d="M5 11a7 7 0 0 0 14 0M12 18v3"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
      />
    </svg>
    <span>{{ listening ? 'Listening…' : 'Voice' }}</span>
  </button>
</template>

<style scoped>
.voice {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  background: transparent;
  color: var(--text-muted);
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
  transition: color 0.15s ease, border-color 0.15s ease;
}

.voice:hover {
  color: var(--accent);
  border-color: var(--border-strong);
}

.voice svg {
  width: 16px;
  height: 16px;
}

.voice--on {
  color: var(--danger);
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(248, 113, 113, 0.1);
}

.voice:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}
</style>
