from flask import Flask, request, jsonify
from code_analyzer import analyze_code
import logging
from flask_cors import CORS
import os
import sys
from flask import got_request_exception

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "https://code-review-56fde.web.app"])

logging.basicConfig(level=logging.INFO)

# Check if OPENAI_API_KEY is set on startup
if not os.getenv("OPENAI_API_KEY"):
    logging.error("OPENAI_API_KEY environment variable is not set. The AI code review service will not work without it.")
    sys.exit(1)

@app.route('/health', methods=['GET'])
def health():
    app.logger.info("Health check requested")
    return jsonify({"status": "ok"})

@app.route('/test', methods=['GET'])
def test():
    app.logger.info("Test endpoint called")
    return jsonify({"message": "Test endpoint is working"})

@app.route('/analyze', methods=['POST'])
def analyze():
    app.logger.info("Analyze request received")
    data = request.json
    if not data or 'code' not in data:
        app.logger.error("Missing 'code' in request body")
        return jsonify({"error": "Missing 'code' in request body"}), 400

    code = data.get('code')

    try:
        result = analyze_code(code)
        # If analyze_code returns a tuple (verdict, feedback), convert to dict for compatibility
        if isinstance(result, tuple) and len(result) == 2:
            result = {
                "verdict": result[0],
                "summary": "",
                "bugs": result[1],
                "suggestions": "",
                "error": ""
            }
    except Exception as e:
        app.logger.error(f"Error during analysis: {str(e)}")
        return jsonify({"error": f"Error during analysis: {str(e)}"}), 500

    app.logger.info(f"Analysis completed successfully: {result}")
    return jsonify(result)

def log_exception(sender, exception, **extra):
    sender.logger.error(f"Unhandled Exception: {exception}")

got_request_exception.connect(log_exception, app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
