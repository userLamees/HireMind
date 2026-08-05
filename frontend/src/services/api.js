const BASE = (import.meta.env.VITE_API_BASE || 'http://localhost:5000').replace(/\/$/, '')

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    // fetch only rejects on network-level failures, which here almost always
    // means the Flask API isn't running.
    throw new Error(`Cannot reach the API at ${BASE}. Is the Flask server running?`)
  }

  const payload = await response.json().catch(() => null)

  if (!response.ok || !payload?.success) {
    throw new Error(payload?.error || `Request failed (HTTP ${response.status})`)
  }

  return payload.data
}

export function fetchRandomQuestion({ category, difficulty, exclude = [] } = {}) {
  const params = new URLSearchParams()
  if (category) params.set('category', category)
  if (difficulty) params.set('difficulty', difficulty)
  exclude.forEach((id) => params.append('exclude', id))

  const query = params.toString()
  return request(`/api/questions/random${query ? `?${query}` : ''}`)
}

export function analyzeAnswer({ questionId, question, answer }) {
  return request('/api/analyze', {
    method: 'POST',
    body: JSON.stringify({ question_id: questionId, question, answer }),
  })
}

export const API_BASE = BASE
