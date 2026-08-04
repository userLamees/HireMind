from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    try:
        data = request.json
        answer = data.get('answer', '')

        if not answer:
            return jsonify({"success": False, "error": "No answer"}), 400

        score = min(100, max(50, len(answer) // 5))

        return jsonify({
            "success": True,
            "data": {
                "score": score,
                "feedback": "Excellent answer! Keep practicing.",
                "strengths": ["Clear communication", "Well structured"],
                "improvements": ["Add more examples", "Provide metrics"]
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
