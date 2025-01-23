from flask import Flask, request, jsonify
import logging
from db_utils import init_db, add_user
from tracing import setup_tracing
from opentelemetry import trace

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)

# Setup tracing
tracer = setup_tracing(service_name="user-info-app")

# Flask application
app = Flask(__name__)

@app.route('/api/greet', methods=['POST'])
def greet_user():
    with tracer.start_as_current_span("process_request"):
        data = request.json
        name = data.get("name")
        language = data.get("language")

        if not name or not language:
            logger.warning("Invalid input: Missing name or language")
            return jsonify({"error": "Name and language are required."}), 400

        add_user(name, language)
        logger.info(f"User data saved: Name={name}, Language={language}")
        return jsonify({"message": f"Hello {name}, Your native language is {language}"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
