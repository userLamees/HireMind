<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <main class="page home">
    <div class="container home__inner">
      <div class="logo">
        <span class="logo__icon" aria-hidden="true">🧠</span>
        <span class="logo__text">HIREMIND</span>
      </div>

      <h1 class="title">Master Your Interview Skills</h1>

      <p class="subtitle">
        This app is built for <strong>Software Development</strong> engineers.
        Answer real interview questions and get an instant score with feedback.
      </p>

      <button class="btn btn--lg" type="button" @click="router.push('/interview')">
        Start Interview Practice
      </button>
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

.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: 2.5rem;
}

.logo__icon {
  font-size: 2.6rem;
  line-height: 1;
}

.logo__text {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: 0.18em;
  color: var(--accent);
}

.title {
  margin: 0 0 1.1rem;
  font-size: clamp(2rem, 6vw, 3rem);
  line-height: 1.12;
  letter-spacing: -0.03em;
  font-weight: 700;
}

.subtitle {
  margin: 0 auto 2.5rem;
  max-width: 30rem;
  font-size: 1.05rem;
  line-height: 1.7;
  color: var(--text-muted);
}

.subtitle strong {
  color: var(--accent);
  font-weight: 600;
}

@media (max-width: 520px) {
  .btn--lg {
    width: 100%;
  }
}
</style>
