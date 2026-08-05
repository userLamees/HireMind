<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import TeamCredits from '../components/TeamCredits.vue'
import logoUrl from '../assets/logo.svg'
import { LENGTHS, MODES, startInterview } from '../stores/session'

const router = useRouter()

const mode = ref('normal')
const total = ref(5)

function begin() {
  startInterview({ mode: mode.value, total: total.value })
  router.push('/interview')
}
</script>

<template>
  <main class="page home">
    <div class="container home__inner">
      <div class="logo rise">
        <span class="logo__aura" aria-hidden="true"></span>
        <img class="logo__img" :src="logoUrl" alt="HireMind" width="260" height="325" />
      </div>

      <h1 class="title rise" style="animation-delay: 90ms">Master Your Interview Skills</h1>

      <p class="subtitle rise" style="animation-delay: 170ms">
        This app is built for <strong>Software Development</strong> engineers.
        Answer real interview questions and get an instant score with feedback.
      </p>

      <fieldset class="choice rise" style="animation-delay: 250ms">
        <legend class="choice__legend">Mode</legend>
        <div class="choice__row">
          <button
            v-for="(config, key) in MODES"
            :key="key"
            type="button"
            class="option"
            :class="{ 'option--on': mode === key }"
            :aria-pressed="mode === key"
            @click="mode = key"
          >
            <span class="option__label">
              <span class="option__dot" aria-hidden="true"></span>{{ config.label }}
            </span>
            <span class="option__hint">{{ config.hint }}</span>
          </button>
        </div>
      </fieldset>

      <fieldset class="choice rise" style="animation-delay: 320ms">
        <legend class="choice__legend">Interview length</legend>
        <div class="choice__row">
          <button
            v-for="option in LENGTHS"
            :key="option.total"
            type="button"
            class="option"
            :class="{ 'option--on': total === option.total }"
            :aria-pressed="total === option.total"
            @click="total = option.total"
          >
            <span class="option__label">
              <span class="option__dot" aria-hidden="true"></span>{{ option.label }}
            </span>
            <span class="option__hint">{{ option.total }} questions · {{ option.hint }}</span>
          </button>
        </div>
      </fieldset>

      <button class="btn btn--lg start rise" style="animation-delay: 400ms" type="button" @click="begin">
        Start Interview Practice
      </button>

      <TeamCredits class="rise" style="animation-delay: 480ms" />
    </div>
  </main>
</template>

<style scoped>
.home {
  justify-content: center;
}

.home__inner {
  text-align: center;
  max-width: 620px;
}

/* Positioning context so the aura can glow behind the mark. */
.logo {
  position: relative;
  display: inline-block;
  margin-bottom: 1.75rem;
}

.logo__img {
  position: relative;
  display: block;
  width: min(240px, 58vw);
  height: auto;
  animation: bob 6s ease-in-out infinite;
}

/* Sits over the brain only (the top ~60%), not the wordmark below it. */
.logo__aura {
  position: absolute;
  top: 4%;
  left: 50%;
  width: 78%;
  aspect-ratio: 1;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(52, 196, 188, 0.28), transparent 66%);
  animation: breathe 6s ease-in-out infinite;
  pointer-events: none;
}

@keyframes bob {
  50% {
    transform: translateY(-6px);
  }
}

@keyframes breathe {
  0%,
  100% {
    opacity: 0.45;
    transform: translateX(-50%) scale(0.88);
  }
  50% {
    opacity: 1;
    transform: translateX(-50%) scale(1.1);
  }
}

.title {
  margin: 0 0 1.1rem;
  font-size: clamp(2rem, 6vw, 3rem);
  line-height: 1.12;
  letter-spacing: -0.03em;
  font-weight: 700;
}

.subtitle {
  margin: 0 auto 2.25rem;
  max-width: 30rem;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--text-muted);
}

.subtitle strong {
  color: var(--accent);
  font-weight: 600;
}

.choice {
  margin: 0 0 1.5rem;
  padding: 0;
  border: none;
}

.choice__legend {
  padding: 0 0 0.6rem;
  font-size: 0.78rem;
  letter-spacing: 0.11em;
  text-transform: uppercase;
  color: var(--text-muted);
}

.choice__row {
  display: grid;
  gap: 0.6rem;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
}

.option {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.85rem 1rem;
  border: 2px solid transparent;
  border-radius: var(--radius);
  background: rgba(148, 163, 184, 0.06);
  color: var(--text-muted);
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.15s ease, background 0.15s ease, color 0.15s ease;
}

.option:hover {
  border-color: var(--border-strong);
  color: var(--text);
}

/* Selected state has to survive a dark background: a filled dot, a solid
   2px ring, a brighter surface, and full-strength text — not just a border. */
.option--on {
  border-color: var(--accent);
  background: rgba(52, 196, 188, 0.18);
  color: var(--text);
}

.option__label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  font-size: 0.98rem;
}

.option__dot {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  border: 2px solid var(--text-muted);
  border-radius: 50%;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

.option--on .option__dot {
  border-color: var(--accent);
  /* Inset shadow fills the ring — reads as a selected radio button. */
  box-shadow: inset 0 0 0 3px var(--accent);
}

.option__hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.option:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

.start {
  margin-top: 0.75rem;
}

@media (max-width: 520px) {
  .start {
    width: 100%;
  }
}
</style>
