"""Interview question bank, loaded from the Software_Questions.csv dataset."""
import csv
import os
import random

DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Software_Questions.csv')

# The dataset ships two inconsistent category labels. generate_synthetic_data.py
# collapses them the same way, so keeping this identical means the question bank
# lines up with the synthetic dataset.
CATEGORY_FIXES = {
    'General Program': 'General Programming',
    'Database and SQL': 'Database Systems',
}


def _load(path=DATA_PATH):
    """Read the CSV once into memory, dropping duplicate questions."""
    questions = []
    seen = set()

    # The file is latin1-encoded, not utf-8 — reading it as utf-8 raises.
    with open(path, encoding='latin1', newline='') as f:
        for row in csv.DictReader(f):
            text = (row.get('Question') or '').strip()
            if not text or text in seen:
                continue
            seen.add(text)

            category = (row.get('Category') or '').strip()
            questions.append({
                'id': int(row['Question Number']),
                'question': text,
                'ideal_answer': (row.get('Answer') or '').strip(),
                'category': CATEGORY_FIXES.get(category, category),
                'difficulty': (row.get('Difficulty') or '').strip(),
            })

    return questions


QUESTIONS = _load()
_BY_ID = {q['id']: q for q in QUESTIONS}


def public(question):
    """Strip the answer key before sending a question to the browser."""
    return {
        'id': question['id'],
        'question': question['question'],
        'category': question['category'],
        'difficulty': question['difficulty'],
    }


def get(question_id):
    try:
        return _BY_ID.get(int(question_id))
    except (TypeError, ValueError):
        return None


def pick_random(category=None, difficulty=None, exclude=()):
    """Pick one question, optionally filtered. Filters that match nothing are
    ignored rather than returning empty — the user always gets a question."""
    pool = QUESTIONS

    if category:
        filtered = [q for q in pool if q['category'].lower() == category.lower()]
        pool = filtered or pool

    if difficulty:
        filtered = [q for q in pool if q['difficulty'].lower() == difficulty.lower()]
        pool = filtered or pool

    if exclude:
        excluded = {int(e) for e in exclude if str(e).isdigit()}
        remaining = [q for q in pool if q['id'] not in excluded]
        # Once every question has been seen, start over instead of failing.
        pool = remaining or pool

    return random.choice(pool)


def categories():
    return sorted({q['category'] for q in QUESTIONS if q['category']})


def difficulties():
    return sorted({q['difficulty'] for q in QUESTIONS if q['difficulty']})
