<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { MODES, reset, session, summary } from '../stores/session'

const router = useRouter()

const stats = computed(() => summary())

const verdict = computed(() => {
  const average = stats.value?.average ?? 0
  if (average >= 86) return 'Interview ready'
  if (average >= 71) return 'Nearly there'
  if (average >= 41) return 'Solid foundation'
  return 'Keep practicing'
})

function again() {
  reset()
  router.push('/')
}
</script>

<template>
  <main class="page">
    <div class="container">
      <header class="bar">
        <router-link to="/" class="brand">HIRE<span class="brand__accent">MIND</span></router-link>
      </header>

      <section v-if="stats" class="card">
        <p class="eyebrow">Interview complete</p>
        <div class="average">
          <strong>{{ stats.average }}</strong>
          <span>average across {{ stats.total }} questions</span>
        </div>
        <p class="verdict">{{ verdict }}</p>

        <p class="mode">
          {{ MODES[session.mode].label }} mode
        </p>

        <div v-if="!stats.modelUsed" class="notice">
          At least one answer was scored without the AI model, so this average is
          not a reliable measure.
        </div>

        <div class="block">
          <h2>Every question</h2>
          <ol class="rundown">
            <li v-for="(entry, i) in session.answered" :key="i">
              <span class="rundown__score" :class="{ 'rundown__score--low': entry.result.score < 50 }">
                {{ entry.result.score }}
              </span>
              <span class="rundown__text">
                <span class="rundown__q">{{ entry.question?.question }}</span>
                <span class="rundown__meta">
                  {{ entry.question?.category }} · {{ entry.question?.difficulty }}
                </span>
              </span>
            </li>
          </ol>
        </div>

        <div v-if="stats.total > 1" class="lists">
          <div class="block">
            <h2>Strongest answer</h2>
            <p class="highlight">{{ stats.strongest.question?.question }}</p>
            <p class="highlight__score">Scored {{ stats.strongest.result.score }}</p>
          </div>
          <div class="block">
            <h2>Weakest answer</h2>
            <p class="highlight">{{ stats.weakest.question?.question }}</p>
            <p class="highlight__score">Scored {{ stats.weakest.result.score }}</p>
          </div>
        </div>

        <button class="btn practice" type="button" @click="again">Practice Again</button>
      </section>
    </div>
  </main>
</template>

<style scoped>
.bar {
  margin-bottom: 1.75rem;
}

/* Matches the logo lockup: HIRE in white, MIND in the accent colour. */
.brand {
  font-weight: 800;
  letter-spacing: 0.14em;
  font-size: 0.95rem;
  color: var(--text);
  text-decoration: none;
}

.brand__accent {
  color: var(--accent);
}

.eyebrow {
  margin: 0 0 0.75rem;
  text-align: center;
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.average {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  margin-bottom: 0.5rem;
}

.average strong {
  font-size: 3.6rem;
  font-weight: 700;
  line-height: 1;
  color: var(--accent);
}

.average span {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.verdict {
  margin: 0 0 0.4rem;
  text-align: center;
  font-size: 1.15rem;
  font-weight: 600;
}

.mode {
  margin: 0 0 1.75rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.block {
  margin-bottom: 1.5rem;
}

.block h2 {
  margin: 0 0 0.7rem;
  font-size: 0.8rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.rundown {
  margin: 0;
  padding: 0;
  list-style: none;
}

.rundown li {
  display: flex;
  align-items: flex-start;
  gap: 0.85rem;
  padding: 0.7rem 0;
  border-top: 1px solid var(--border);
}

.rundown li:first-child {
  border-top: none;
}

.rundown__score {
  flex-shrink: 0;
  min-width: 2.6rem;
  padding: 0.2rem 0;
  border-radius: 8px;
  background: rgba(52, 196, 188, 0.12);
  color: var(--accent);
  font-weight: 700;
  font-variant-numeric: tabular-nums;
  text-align: center;
}

.rundown__score--low {
  background: rgba(248, 113, 113, 0.12);
  color: var(--danger);
}

.rundown__text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.rundown__q {
  line-height: 1.5;
  font-size: 0.95rem;
}

.rundown__meta {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.lists {
  display: grid;
  gap: 1.25rem;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
}

.highlight {
  margin: 0 0 0.35rem;
  line-height: 1.55;
  font-size: 0.95rem;
}

.highlight__score {
  margin: 0;
  font-size: 0.85rem;
  color: var(--accent);
}

.practice {
  width: 100%;
  margin-top: 1.5rem;
}
</style>
