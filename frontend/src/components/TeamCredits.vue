<script setup>
/**
 * Add a `linkedin` URL to any member and their name becomes a link; leave it
 * off and the name renders as plain text. Nothing else needs changing.
 */
const team = [
  { name: 'Lamis Alharbi', linkedin: '' },
  { name: 'Renad Bin Shdied', linkedin: '' },
  { name: 'Sara Aleidan', linkedin: '' },
  { name: 'Lama Alkhamsy', linkedin: '' },
]
</script>

<template>
  <footer class="credits">
    <p class="credits__label">Built by</p>
    <ul class="credits__list">
      <li v-for="member in team" :key="member.name">
        <a
          v-if="member.linkedin"
          class="credits__link"
          :href="member.linkedin"
          target="_blank"
          rel="noopener noreferrer"
        >
          {{ member.name }}
          <svg viewBox="0 0 24 24" class="credits__icon" aria-hidden="true">
            <path
              d="M6.94 5a2 2 0 1 1-4 0 2 2 0 0 1 4 0ZM7 8.48H3V21h4V8.48Zm6.32 0H9.34V21h3.94v-6.57c0-3.66 4.77-4 4.77 0V21H22v-7.93c0-6.17-7.06-5.94-8.72-2.91V8.48Z"
              fill="currentColor"
            />
          </svg>
          <span class="visually-hidden">LinkedIn profile</span>
        </a>
        <span v-else class="credits__name">{{ member.name }}</span>
      </li>
    </ul>
  </footer>
</template>

<style scoped>
.credits {
  margin-top: 3.5rem;
  text-align: center;
}

.credits__label {
  margin: 0 0 0.7rem;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text-muted);
  opacity: 0.75;
}

.credits__list {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0.4rem 0.5rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.credits__link,
.credits__name {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  border: 1px solid transparent;
  border-radius: 999px;
  font-size: 0.85rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.15s ease, border-color 0.15s ease, background 0.15s ease;
}

.credits__link:hover,
.credits__link:focus-visible {
  color: var(--accent);
  border-color: var(--border);
  background: rgba(52, 196, 188, 0.08);
  outline: none;
}

.credits__icon {
  width: 13px;
  height: 13px;
  opacity: 0.8;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
  white-space: nowrap;
  border: 0;
}
</style>
