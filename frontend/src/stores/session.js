import { reactive } from 'vue'

/**
 * Holds the last graded answer so ResultsView can render it after navigation.
 * A plain reactive module is enough here — there is no cross-page state worth
 * pulling in Pinia for.
 */
export const session = reactive({
  question: null,
  answer: '',
  result: null,
  answeredIds: [],
})

export function saveResult({ question, answer, result }) {
  session.question = question
  session.answer = answer
  session.result = result
  if (question?.id && !session.answeredIds.includes(question.id)) {
    session.answeredIds.push(question.id)
  }
}

export function hasResult() {
  return session.result !== null
}

export function clearResult() {
  session.result = null
}
