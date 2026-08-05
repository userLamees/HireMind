import { reactive } from 'vue'

export const MODES = {
  normal: { label: 'Normal', hint: 'Steady medium-difficulty questions' },
  adaptive: { label: 'Adaptive', hint: 'Gets harder as you score well' },
}

export const LENGTHS = [
  { total: 3, label: 'Short', hint: '~5 min' },
  { total: 5, label: 'Medium', hint: '~10 min' },
  { total: 8, label: 'Long', hint: '~20 min' },
]

// The bank holds 92 Medium and 76 Hard questions but only 6 Easy ones, so
// Adaptive moves between Medium and Hard — dropping to Easy would exhaust the
// pool within a single interview and start repeating.
const START_DIFFICULTY = 'Medium'
const PROMOTE_AT = 80
const DEMOTE_AT = 50

function blank() {
  return {
    // `started` is what the route guards key off — `total` always has a
    // default, so it can never signal "no interview configured".
    started: false,
    mode: 'normal',
    total: 5,
    index: 0,
    difficulty: START_DIFFICULTY,
    answered: [],
    finished: false,
  }
}

export const session = reactive(blank())

export function startInterview({ mode, total }) {
  Object.assign(session, blank(), { mode, total, started: true })
}

/** The result of the question just submitted — what ResultsView renders. */
export function currentResult() {
  return session.answered[session.answered.length - 1] || null
}

export function recordAnswer({ question, answer, result }) {
  session.answered.push({ question, answer, result })

  if (session.mode === 'adaptive') {
    if (result.score >= PROMOTE_AT) session.difficulty = 'Hard'
    else if (result.score <= DEMOTE_AT) session.difficulty = START_DIFFICULTY
  }

  session.finished = session.answered.length >= session.total
}

/** Moves to the next question. Returns false when the interview is over. */
export function advance() {
  if (session.finished) return false
  session.index += 1
  return true
}

export function askedIds() {
  return session.answered.map((a) => a.question?.id).filter(Boolean)
}

export function summary() {
  const scores = session.answered.map((a) => a.result.score)
  if (!scores.length) return null

  const average = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
  const sorted = [...session.answered].sort((a, b) => a.result.score - b.result.score)

  return {
    average,
    total: session.answered.length,
    weakest: sorted[0],
    strongest: sorted[sorted.length - 1],
    // Any question graded without the model makes the average unreliable.
    modelUsed: session.answered.every((a) => a.result.analysis_mode === 'model'),
  }
}

export function hasResult() {
  return session.answered.length > 0
}

export function reset() {
  Object.assign(session, blank())
}
