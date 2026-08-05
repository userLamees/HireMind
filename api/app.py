"""HireMind API — serves interview questions and grades answers."""
import os

from flask import Flask, jsonify, request
from flask_cors import CORS

import analyzer
import questions

app = Flask(__name__)

# The Vue frontend runs on a different origin (Vite dev server, or a built
# bundle). Without CORS the browser blocks every request.
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*')
if allowed_origins != '*':
    allowed_origins = [o.strip() for o in allowed_origins.split(',') if o.strip()]
CORS(app, resources={r'/api/*': {'origins': allowed_origins}})


@app.route('/', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'questions_loaded': len(questions.QUESTIONS),
        'model_provider': analyzer.MODEL_PROVIDER,
        'model': analyzer.OLLAMA_MODEL,
        'model_available': analyzer.model_available(),
    })


@app.route('/api/categories', methods=['GET'])
def list_categories():
    return jsonify({
        'success': True,
        'data': {
            'categories': questions.categories(),
            'difficulties': questions.difficulties(),
        },
    })


@app.route('/api/questions/random', methods=['GET'])
def random_question():
    exclude = [v for v in request.args.getlist('exclude') if v]
    question = questions.pick_random(
        category=request.args.get('category'),
        difficulty=request.args.get('difficulty'),
        exclude=exclude,
    )
    # public() drops ideal_answer — the answer key never reaches the browser.
    return jsonify({'success': True, 'data': questions.public(question)})


@app.route('/api/analyze', methods=['POST'])
def analyze_answer():
    payload = request.get_json(silent=True) or {}
    answer = str(payload.get('answer', '')).strip()

    if not answer:
        return jsonify({'success': False, 'error': 'Answer is empty'}), 400

    # Prefer the stored question so we can grade against its reference answer.
    question = questions.get(payload.get('question_id'))
    if question:
        question_text = question['question']
        ideal_answer = question['ideal_answer']
        difficulty = question['difficulty']
    else:
        # Falls back to the bare {answer} contract.
        question_text = str(payload.get('question', '')).strip() or 'Not provided'
        ideal_answer = ''
        difficulty = ''

    result = analyzer.analyze(question_text, ideal_answer, answer, difficulty)
    return jsonify({'success': True, 'data': result})


if __name__ == '__main__':
    # 5001, not 5000: macOS AirPlay Receiver occupies 5000 by default.
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
