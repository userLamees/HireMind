<p align="center">
  <img src="frontend/src/assets/logo-full.svg" alt="HireMind" width="260">
</p>

# HireMind

Mock interview practice for **Software Development** engineers. You get a real
interview question, write your answer, and a local AI model scores it with
feedback.

- **Frontend** — Vue 3 + Vite (`frontend/`)
- **API** — Flask (`api/`)
- **Model** — served locally through [Ollama](https://ollama.com)
- **Questions** — 174 unique questions loaded from `Software_Questions.csv`,
  across 20 categories (System Design, DevOps, Front-end, Back-end, Security, …)

## How an interview works

Pick a **mode** and a **length** on the home page, answer that many questions,
then get a summary with your average and a per-question breakdown.

| Mode | Behaviour |
|---|---|
| **Normal** | Every question stays at Medium difficulty |
| **Adaptive** | Starts at Medium; scoring 80+ moves you to Hard, scoring 50 or below moves you back to Medium |

Adaptive deliberately moves between **Medium and Hard only**. The bank holds 92
Medium and 76 Hard questions but just 6 Easy ones — an Easy tier would exhaust
its pool and start repeating within a single interview.

Lengths are Short (3 questions), Medium (5), and Long (8).

---

## Running it

You need three things running: Ollama, the API, and the frontend.

### 1. Ollama (the model)

```bash
ollama serve                    # starts on http://localhost:11434
ollama pull mistral:7b-instruct # or whichever model you want to use
```

### 2. API

```bash
cd api
pip install -r requirements.txt
python app.py                   # http://localhost:5001
```

Check that the model was found:

```bash
curl http://localhost:5001/api/health
# {"status":"ok","questions_loaded":174,"model_available":true, ...}
```

The API listens on **5001**, not 5000, because macOS reserves port 5000 for
AirPlay Receiver. Override with `PORT=... python app.py` if 5001 is taken too.

If `model_available` is `false`, the API still works — it falls back to a rough
word-count estimate and **says so in the response and in the UI**. It never
passes off a fake score as AI analysis.

### 3. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev                     # http://localhost:5173
```

---

## Configuration

### API (environment variables)

| Variable | Default | What it does |
|---|---|---|
| `MODEL_PROVIDER` | `ollama` | `ollama` (local) or `groq` / `openai_compatible` (hosted) |
| `OLLAMA_URL` | `http://localhost:11434` | Where Ollama is listening |
| `OLLAMA_MODEL` | `mistral:7b-instruct` | Model name — **set this to your own model** |
| `MODEL_TIMEOUT` | `120` | Seconds to wait for the model |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins |
| `PORT` |  `5001` | API port |

To use your own trained model, register it with Ollama and point `OLLAMA_MODEL`
at it:

```bash
OLLAMA_MODEL=my-interview-grader python app.py
```

### Running deployed (no Ollama)

Ollama needs several GB of RAM and cannot run on a free hosting tier, so a
deployed instance needs a hosted model. Any OpenAI-compatible endpoint works —
Groq, OpenRouter, Together — through the same provider:

| Variable | Default | What it does |
|---|---|---|
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` | Endpoint base |
| `LLM_API_KEY` | *(empty)* | Your key — without it the API falls back to the heuristic |
| `LLM_MODEL` | `llama-3.3-70b-versatile` | Model name — **check the provider's current list** |

```bash
MODEL_PROVIDER=groq LLM_API_KEY=gsk_... python app.py
```

Switching providers is two variables (`LLM_BASE_URL`, `LLM_MODEL`) and no code
change.

### Frontend (`.env`)

| Variable | Default | What it does |
|---|---|---|
| `VITE_API_BASE` | `http://localhost:5001` | API address |
| `VITE_TIMER_SECONDS` | `180` | Time per question before auto-submit |

---

## Publishing a public link

Ollama cannot run on a free host, so a public deploy swaps it for a hosted
model. Three free pieces: **Render** for the API, **Render Static Site** for the
frontend, **Groq** for the model.

Deploy in this order — each step needs a URL from the one before it.

### 1. Groq API key

Create an account at [console.groq.com](https://console.groq.com) and generate a
key (starts with `gsk_`). Check the current model list there too — names change,
and `LLM_MODEL` must match one of them exactly.

### 2. API → Render Web Service

New → Web Service → this repo. Settings:

| Field | Value |
|---|---|
| Root Directory | *(leave blank)* |
| Build Command | `pip install -r requirements.txt` |
| Start Command | *(leave blank — the `Procfile` handles it)* |

Environment variables:

```
MODEL_PROVIDER = groq
LLM_API_KEY    = gsk_...
LLM_MODEL      = llama-3.3-70b-versatile
```

Deploy, then check `https://<your-api>.onrender.com/api/health` — it should
report `"model_available": true`. Copy that base URL.

### 3. Frontend → Render Static Site

New → Static Site → this repo. Settings:

| Field | Value |
|---|---|
| Root Directory | `frontend` |
| Build Command | `npm ci && npm run build` |
| Publish Directory | `dist` |

Environment variable — **set this before the first build**:

```
VITE_API_BASE = https://<your-api>.onrender.com
```

> ⚠️ Vite bakes `VITE_*` variables into the bundle at **build** time, not at
> runtime. Add it after deploying and the site will keep calling
> `http://localhost:5001` until you trigger a rebuild.

### 4. Lock down CORS

Back on the API service, set `ALLOWED_ORIGINS` to the static site's URL and
redeploy. The default `*` works but lets any site call your API.

### What to expect

- **Cold starts.** Render's free tier sleeps after inactivity; the first request
  after a quiet period takes roughly a minute. Later requests are fast.
- **Rate limits.** Groq's free tier is capped — fine for a demo or portfolio
  link, not for real traffic.
- **If the model fails**, the API still answers, labelled
  `analysis_mode: "heuristic"`, and the UI shows a warning banner. Users get a
  degraded experience rather than an error page.

---

## API reference

| Method | Path | Returns |
|---|---|---|
| `GET` | `/api/health` | Status, question count, whether the model is reachable |
| `GET` | `/api/categories` | All categories and difficulty levels |
| `GET` | `/api/questions/random` | One question. Filters: `category`, `difficulty`, `exclude` (repeatable) |
| `POST` | `/api/analyze` | `{question_id, answer}` → `{score, feedback, strengths[], improvements[], analysis_mode}` |

`analysis_mode` is `"model"` when a real model graded the answer, `"heuristic"`
when it fell back. The results page shows a warning banner for `"heuristic"`.

`/api/questions/random` never returns `ideal_answer` — the reference answer stays
server-side so the browser can't read the answer key.

---

## Project layout

```
api/
  app.py          Flask routes
  questions.py    CSV → in-memory question bank
  analyzer.py     model calls + fallback  ← the only file to edit to swap models
  data/Software_Questions.csv
frontend/
  src/views/      HomeView, InterviewView, ResultsView
  src/components/ TimerBadge, VoiceButton
  src/services/   api.js
  src/stores/     session.js
generate_synthetic_data.py   Training-data generator (not used at runtime)
synthetic_data_ollama.json   Its output
```

## Notes

- **Voice input** uses the Web Speech API, so it works in Chrome, Edge and
  Safari. The button hides itself in browsers without support — it is optional.
- **The timer** counts down from 3 minutes and auto-submits whatever is written.
  An empty box just stops the clock.
