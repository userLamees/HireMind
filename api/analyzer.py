"""Scoring layer.

Everything that talks to a model lives here, behind one function: `analyze()`.
Swapping in a different model means editing this file only.
"""
import json
import os

import requests

MODEL_PROVIDER = os.environ.get('MODEL_PROVIDER', 'ollama')
OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'mistral:7b-instruct')
MODEL_TIMEOUT = float(os.environ.get('MODEL_TIMEOUT', '120'))

# Hosted fallback for a deployed instance, where Ollama can't run. Any
# OpenAI-compatible endpoint works — Groq, OpenRouter, Together — so switching
# providers is a matter of changing LLM_BASE_URL and LLM_MODEL.
LLM_BASE_URL = os.environ.get('LLM_BASE_URL', 'https://api.groq.com/openai/v1')
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_MODEL = os.environ.get('LLM_MODEL', 'llama-3.3-70b-versatile')

PROMPT_TEMPLATE = """You are a senior software engineering interviewer.
Grade the candidate's answer against the reference answer.

Question: {question}
Difficulty: {difficulty}
Reference answer: {ideal_answer}

Candidate's answer:
{answer}

Reply with JSON only, in exactly this shape:
{{
  "score": <integer 0-100>,
  "feedback": "<2-3 sentences addressed to the candidate>",
  "strengths": ["<what they did well>", "..."],
  "improvements": ["<what to fix>", "..."]
}}

Score honestly: 0-40 wrong or empty, 41-70 partially correct,
71-85 solid, 86-100 complete and precise."""


class ModelUnavailable(Exception):
    """Raised when the model backend cannot be reached or gave junk."""


def _clean_list(value, limit=4):
    """Coerce whatever the model returned into a list of short strings."""
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return []
    out = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text[:300])
    return out[:limit]


def _normalize(payload):
    """Validate the model's JSON. Raises ModelUnavailable if it is unusable."""
    if not isinstance(payload, dict):
        raise ModelUnavailable('model did not return a JSON object')

    try:
        score = int(round(float(payload.get('score'))))
    except (TypeError, ValueError):
        raise ModelUnavailable('model did not return a numeric score')

    feedback = str(payload.get('feedback', '')).strip()
    if not feedback:
        raise ModelUnavailable('model returned no feedback')

    return {
        'score': max(0, min(100, score)),
        'feedback': feedback,
        'strengths': _clean_list(payload.get('strengths')),
        'improvements': _clean_list(payload.get('improvements')),
        'analysis_mode': 'model',
        'model': OLLAMA_MODEL,
    }


def _analyze_with_ollama(question, ideal_answer, answer, difficulty=''):
    prompt = PROMPT_TEMPLATE.format(
        question=question,
        difficulty=difficulty or 'Unknown',
        ideal_answer=ideal_answer or '(none provided)',
        answer=answer,
    )

    try:
        response = requests.post(
            f'{OLLAMA_URL.rstrip("/")}/api/generate',
            json={
                'model': OLLAMA_MODEL,
                'prompt': prompt,
                'stream': False,
                # Ollama constrains the sampler to emit valid JSON.
                'format': 'json',
                'options': {'temperature': 0.2},
            },
            timeout=MODEL_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise ModelUnavailable(f'cannot reach Ollama at {OLLAMA_URL}: {exc}')

    if response.status_code != 200:
        raise ModelUnavailable(f'Ollama returned HTTP {response.status_code}')

    try:
        raw = response.json()['response']
    except (ValueError, KeyError) as exc:
        raise ModelUnavailable(f'unexpected Ollama envelope: {exc}')

    try:
        return _normalize(json.loads(raw))
    except json.JSONDecodeError as exc:
        raise ModelUnavailable(f'model output was not valid JSON: {exc}')


def _analyze_with_openai_compatible(question, ideal_answer, answer, difficulty=''):
    """Grade via any OpenAI-compatible chat endpoint (Groq by default)."""
    if not LLM_API_KEY:
        raise ModelUnavailable('LLM_API_KEY is not set')

    prompt = PROMPT_TEMPLATE.format(
        question=question,
        difficulty=difficulty or 'Unknown',
        ideal_answer=ideal_answer or '(none provided)',
        answer=answer,
    )

    try:
        response = requests.post(
            f'{LLM_BASE_URL.rstrip("/")}/chat/completions',
            headers={'Authorization': f'Bearer {LLM_API_KEY}'},
            json={
                'model': LLM_MODEL,
                'messages': [{'role': 'user', 'content': prompt}],
                # The prompt already says "Reply with JSON only", which JSON
                # mode requires the request to mention.
                'response_format': {'type': 'json_object'},
                'temperature': 0.2,
            },
            timeout=MODEL_TIMEOUT,
        )
    except requests.RequestException as exc:
        raise ModelUnavailable(f'cannot reach {LLM_BASE_URL}: {exc}')

    if response.status_code != 200:
        # The body carries the real reason (bad model name, quota, bad key).
        raise ModelUnavailable(f'HTTP {response.status_code}: {response.text[:200]}')

    try:
        raw = response.json()['choices'][0]['message']['content']
    except (ValueError, KeyError, IndexError) as exc:
        raise ModelUnavailable(f'unexpected response envelope: {exc}')

    try:
        result = _normalize(json.loads(raw))
    except json.JSONDecodeError as exc:
        raise ModelUnavailable(f'model output was not valid JSON: {exc}')

    result['model'] = LLM_MODEL
    return result


def _heuristic(answer, reason=''):
    """Fallback used when no model is reachable.

    This is NOT AI analysis. The response says so via `analysis_mode` so the UI
    can tell the user their score did not come from a model.
    """
    word_count = len(answer.split())
    has_detail = len(answer) > 200
    has_structure = any(
        marker in answer.lower()
        for marker in ('first', 'second', 'however', 'therefore', 'because', 'for example')
    )

    score = min(70, 20 + word_count)
    if has_detail:
        score += 5
    if has_structure:
        score += 5

    # The remedy differs by deployment: locally you start Ollama, on a hosted
    # instance you fix the API key — so the message stays neutral.
    return {
        'score': max(0, min(75, score)),
        'feedback': (
            'The AI model is unavailable, so this is a rough word-count estimate '
            'rather than a real evaluation.'
        ),
        'strengths': ['Answer submitted'] if word_count else [],
        'improvements': ['Run the model to receive real feedback'],
        'analysis_mode': 'heuristic',
        'reason': reason,
    }


def active_model():
    """The model name that will actually be used, for the health endpoint."""
    if MODEL_PROVIDER in ('groq', 'openai_compatible'):
        return LLM_MODEL
    if MODEL_PROVIDER == 'ollama':
        return OLLAMA_MODEL
    return None


def model_available():
    """Probe the configured backend. Reports reachability, not just config —
    a present-but-invalid API key must not read as available."""
    if MODEL_PROVIDER in ('groq', 'openai_compatible'):
        if not LLM_API_KEY:
            return False
        try:
            response = requests.get(
                f'{LLM_BASE_URL.rstrip("/")}/models',
                headers={'Authorization': f'Bearer {LLM_API_KEY}'},
                timeout=5,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    if MODEL_PROVIDER != 'ollama':
        return False

    try:
        response = requests.get(f'{OLLAMA_URL.rstrip("/")}/api/tags', timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False


PROVIDERS = {
    'ollama': _analyze_with_ollama,
    'groq': _analyze_with_openai_compatible,
    'openai_compatible': _analyze_with_openai_compatible,
}


def analyze(question, ideal_answer, answer, difficulty=''):
    """Grade one answer. Always returns a dict; never raises."""
    provider = PROVIDERS.get(MODEL_PROVIDER)
    if provider is None:
        return _heuristic(answer, reason=f'unknown MODEL_PROVIDER: {MODEL_PROVIDER}')

    try:
        return provider(question, ideal_answer, answer, difficulty)
    except ModelUnavailable as exc:
        return _heuristic(answer, reason=str(exc))
