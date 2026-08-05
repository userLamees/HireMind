# 🧠 HireMind

Mock interview practice for **Software Development** engineers. You get a real
interview question, write your answer, and a local AI model scores it with
feedback.

- **Frontend** — Vue 3 + Vite (`frontend/`)
- **API** — Flask (`api/`)
- **Model** — served locally through [Ollama](https://ollama.com)
- **Questions** — 174 unique questions loaded from `Software_Questions.csv`,
  across 20 categories (System Design, DevOps, Front-end, Back-end, Security, …)

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
python app.py                   # http://localhost:5000
```

Check that the model was found:

```bash
curl http://localhost:5000/api/health
# {"status":"ok","questions_loaded":174,"model_available":true, ...}
```

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
| `MODEL_PROVIDER` | `ollama` | Which backend grades answers |
| `OLLAMA_URL` | `http://localhost:11434` | Where Ollama is listening |
| `OLLAMA_MODEL` | `mistral:7b-instruct` | Model name — **set this to your own model** |
| `MODEL_TIMEOUT` | `120` | Seconds to wait for the model |
| `ALLOWED_ORIGINS` | `*` | Comma-separated CORS origins |
| `PORT` | `5000` | API port |

To use your own trained model, register it with Ollama and point `OLLAMA_MODEL`
at it:

```bash
OLLAMA_MODEL=my-interview-grader python app.py
```

### Frontend (`.env`)

| Variable | Default | What it does |
|---|---|---|
| `VITE_API_BASE` | `http://localhost:5000` | API address |
| `VITE_TIMER_SECONDS` | `180` | Time per question before auto-submit |

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
