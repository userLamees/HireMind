<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import TimerBadge from '../components/TimerBadge.vue'
import VoiceButton from '../components/VoiceButton.vue'
import { analyzeAnswer, fetchRandomQuestion } from '../services/api'
import { askedIds, recordAnswer, session } from '../stores/session'

const router = useRouter()

const TIMER_SECONDS = Number(import.meta.env.VITE_TIMER_SECONDS) || 180

const question = ref(null)
const answer = ref('')
const loading = ref(true)
const submitting = ref(false)
const error = ref('')
const timer = ref(null)

const position = computed(() => `Question ${session.answered.length + 1} of ${session.total}`)
const progress = computed(() => (session.answered.length / session.total) * 100)
const canSubmit = computed(() => answer.value.trim().length > 0 && !submitting.value)
const wordCount = computed(() => answer.value.trim().split(/\s+/).filter(Boolean).length)

async function loadQuestion() {
  loading.value = true
  error.value = ''
  try {
    question.value = await fetchRandomQuestion({
      // Normal mode holds at Medium; adaptive mode moves this after each score.
      difficulty: session.difficulty,
      exclude: askedIds(),
    })
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

function appendTranscript(text) {
  answer.value = answer.value ? `${answer.value.trimEnd()} ${text}` : text
}

async function submit() {
  if (!answer.value.trim() || submitting.value) return

  submitting.value = true
  error.value = ''
  timer.value?.stop()

  try {
    const result = await analyzeAnswer({
      questionId: question.value?.id,
      question: question.value?.question,
      answer: answer.value.trim(),
    })
    recordAnswer({ question: question.value, answer: answer.value.trim(), result })
    router.push('/results')
  } catch (err) {
    error.value = err.message
    submitting.value = false
  }
}

// Time is up: submit whatever is written. An empty box just stops the clock.
function onExpired() {
  if (answer.value.trim()) submit()
}

onMounted(() => {
  // Reaching /interview without starting from home leaves no config to run on.
  if (!session.started) router.replace('/')
  else loadQuestion()
})
</script>

<template>
  <main class="page">
    <div class="container">
      <header class="bar">
        <router-link to="/" class="brand">
          <span aria-hidden="true">🧠</span> HIREMIND
        </router-link>
        <div class="bar__right">
          <span class="position">{{ position }}</span>
          <TimerBadge
            v-if="question && !submitting"
            ref="timer"
            :seconds="TIMER_SECONDS"
            @expired="onExpired"
          />
        </div>
      </header>

      <div class="progress" role="progressbar" :aria-valuenow="Math.round(progress)">
        <div class="progress__bar" :style="{ width: `${progress}%` }"></div>
      </div>

      <p v-if="loading" class="state">Loading your question…</p>

      <div v-else-if="error && !question" class="notice notice--error">
        {{ error }}
        <button class="btn btn--ghost retry" type="button" @click="loadQuestion">Retry</button>
      </div>

      <section v-else-if="question" class="card">
        <div class="meta">
          <span class="tag">{{ question.category }}</span>
          <span class="tag">{{ question.difficulty }}</span>
          <span v-if="session.mode === 'adaptive'" class="tag tag--mode">Adaptive</span>
        </div>

        <h1 class="question">{{ question.question }}</h1>

        <div class="answer-head">
          <label for="answer" class="label">Your answer</label>
          <VoiceButton @transcript="appendTranscript" />
        </div>

        <textarea
          id="answer"
          v-model="answer"
          class="answer"
          rows="9"
          placeholder="Type your answer here…"
          :disabled="submitting"
        ></textarea>

        <div class="foot">
          <span class="count">{{ wordCount }} {{ wordCount === 1 ? 'word' : 'words' }}</span>
          <button class="btn" type="button" :disabled="!canSubmit" @click="submit">
            {{ submitting ? 'Analyzing…' : 'Submit Answer' }}
          </button>
        </div>

        <p v-if="error" class="notice notice--error">{{ error }}</p>
      </section>
    </div>
  </main>
</template>

<style scoped>
.bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.9rem;
}

.bar__right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand {
  font-weight: 800;
  letter-spacing: 0.14em;
  font-size: 0.95rem;
  color: var(--accent);
  text-decoration: none;
}

.position {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.progress {
  height: 4px;
  margin-bottom: 1.75rem;
  border-radius: 999px;
  background: rgba(52, 196, 188, 0.14);
  overflow: hidden;
}

.progress__bar {
  height: 100%;
  background: var(--accent);
  transition: width 0.4s ease;
}

.state {
  color: var(--text-muted);
  text-align: center;
  padding: 3rem 0;
}

.meta {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.1rem;
}

.tag--mode {
  color: var(--warning);
  border-color: rgba(251, 191, 36, 0.35);
  background: rgba(251, 191, 36, 0.09);
}

.question {
  margin: 0 0 1.75rem;
  font-size: clamp(1.25rem, 3.4vw, 1.65rem);
  line-height: 1.4;
  font-weight: 650;
}

.answer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
}

.label {
  font-size: 0.88rem;
  color: var(--text-muted);
}

.answer {
  width: 100%;
  padding: 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--border);
  background: rgba(6, 3, 26, 0.6);
  color: var(--text);
  font: inherit;
  line-height: 1.6;
  resize: vertical;
}

.answer:focus {
  outline: none;
  border-color: var(--accent);
}

.answer:disabled {
  opacity: 0.6;
}

.foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-top: 1.1rem;
}

.count {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.retry {
  display: block;
  margin-top: 0.9rem;
}

@media (max-width: 520px) {
  .foot {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .count {
    text-align: center;
  }
}
</style>
