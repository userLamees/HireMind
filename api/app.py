from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)

# Allow the Vue frontend (any origin, or a comma-separated ALLOWED_ORIGINS list)
# to call /api/* from the browser. Without this the browser blocks every request.
allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*')
if allowed_origins != '*':
    allowed_origins = [o.strip() for o in allowed_origins.split(',') if o.strip()]
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.json
        answer = data.get('answer', '').strip()
        
        if not answer:
            return jsonify({"success": False, "error": "No answer"}), 400
        
        # Better scoring logic
        word_count = len(answer.split())
        has_details = len(answer) > 50
        has_structure = any(word in answer.lower() for word in ['first', 'second', 'however', 'therefore', 'because'])
        
        base_score = min(100, 50 + (word_count * 2))
        if has_details:
            base_score += 10
        if has_structure:
            base_score += 15
        
        score = min(100, base_score)
        
        return jsonify({
            "success": True,
            "data": {
                "score": score,
                "feedback": "Good answer! Focus on structure and examples." if score < 75 else "Excellent response with clear reasoning.",
                "strengths": ["Clear communication", "Good pacing"],
                "improvements": ["Add more examples", "Provide metrics"] if score < 80 else ["Great job!"]
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "API is running"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
