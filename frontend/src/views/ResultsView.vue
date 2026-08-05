<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { clearResult, session } from '../stores/session'

const router = useRouter()

const result = computed(() => session.result)
const score = computed(() => result.value?.score ?? 0)

// Ring geometry: 54px radius circle, dash offset drives the fill.
const CIRCUMFERENCE = 2 * Math.PI * 54
const dashOffset = computed(() => CIRCUMFERENCE * (1 - score.value / 100))

const verdict = computed(() => {
  if (score.value >= 86) return 'Excellent'
  if (score.value >= 71) return 'Solid'
  if (score.value >= 41) return 'Needs work'
  return 'Keep practicing'
})

const usedModel = computed(() => result.value?.analysis_mode === 'model')

function practiceAgain() {
  clearResult()
  router.push('/interview')
}
</script>

<template>
  <main class="page">
    <div class="container">
      <header class="bar">
        <router-link to="/" class="brand">
          <span aria-hidden="true">🧠</span> HIREMIND
        </router-link>
      </header>

      <!-- Guarded: "Practice Again" clears the result, and this view re-renders
           once before the route change completes. -->
      <section v-if="result" class="card">
        <div class="score">
          <svg class="ring" viewBox="0 0 120 120" aria-hidden="true">
            <circle class="ring__track" cx="60" cy="60" r="54" />
            <circle
              class="ring__fill"
              cx="60"
              cy="60"
              r="54"
              :stroke-dasharray="CIRCUMFERENCE"
              :stroke-dashoffset="dashOffset"
            />
          </svg>
          <div class="score__text">
            <strong>{{ score }}</strong>
            <span>/ 100</span>
          </div>
        </div>

        <p class="verdict">{{ verdict }}</p>

        <p v-if="session.question" class="asked">{{ session.question.question }}</p>

        <div v-if="!usedModel" class="notice">
          Scored without the AI model — this is a rough estimate only. Start Ollama
          and try again for real feedback.
        </div>

        <div class="block">
          <h2>Feedback</h2>
          <p class="feedback">{{ result.feedback }}</p>
        </div>

        <div class="lists">
          <div v-if="result.strengths?.length" class="block">
            <h2>Strengths</h2>
            <ul class="list list--good">
              <li v-for="item in result.strengths" :key="item">{{ item }}</li>
            </ul>
          </div>

          <div v-if="result.improvements?.length" class="block">
            <h2>Improvements</h2>
            <ul class="list list--work">
              <li v-for="item in result.improvements" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>

        <button class="btn practice" type="button" @click="practiceAgain">
          Practice Again
        </button>
      </section>
    </div>
  </main>
</template>

<style scoped>
.bar {
  margin-bottom: 1.75rem;
}

.brand {
  font-weight: 800;
  letter-spacing: 0.14em;
  font-size: 0.95rem;
  color: var(--accent);
  text-decoration: none;
}

.score {
  position: relative;
  width: 160px;
  height: 160px;
  margin: 0 auto 0.75rem;
}

.ring {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.ring__track,
.ring__fill {
  fill: none;
  stroke-width: 9;
}

.ring__track {
  stroke: rgba(52, 196, 188, 0.14);
}

.ring__fill {
  stroke: var(--accent);
  stroke-linecap: round;
  transition: stroke-dashoffset 0.8s ease;
}

.score__text {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.1rem;
}

.score__text strong {
  font-size: 2.7rem;
  font-weight: 700;
  line-height: 1;
}

.score__text span {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.verdict {
  margin: 0 0 0.5rem;
  text-align: center;
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--accent);
}

.asked {
  margin: 0 0 1.5rem;
  text-align: center;
  font-size: 0.92rem;
  line-height: 1.6;
  color: var(--text-muted);
}

.block {
  margin-bottom: 1.5rem;
}

.block h2 {
  margin: 0 0 0.6rem;
  font-size: 0.8rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.feedback {
  margin: 0;
  line-height: 1.7;
}

.lists {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
}

.list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.list li {
  position: relative;
  padding: 0.35rem 0 0.35rem 1.4rem;
  line-height: 1.55;
  font-size: 0.95rem;
}

.list li::before {
  position: absolute;
  left: 0;
  top: 0.35rem;
}

.list--good li::before {
  content: '✓';
  color: var(--accent);
}

.list--work li::before {
  content: '→';
  color: var(--warning);
}

.practice {
  width: 100%;
  margin-top: 1.5rem;
}
</style>
