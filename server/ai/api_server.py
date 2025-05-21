from flask import Flask, request, jsonify
from code_analyzer import analyze_code
import logging

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Code Analyzer API is running."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get('code')
    if not code:
        return jsonify({'error': 'Code is required for analysis'}), 400
    try:
        result = analyze_code(code)
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error analyzing code: {e}")
        return jsonify({'error': 'Failed to analyze code'}), 500

if __name__ == '__main__':
    app.run(port=5000)
