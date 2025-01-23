import os
from flask import Flask, request, jsonify
from db_setup import init_db
from utils import add_user
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Ensure logs directory exists
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file_path = os.path.join(log_dir, 'app.log')

# Setup logging
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Setup tracing
resource = Resource(attributes={"service.name": "user-info-app"})
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Flask app setup
app = Flask(__name__)

# Initialize the database
init_db()

@app.route('/api/greet', methods=['POST'])
def greet_user():
    with tracer.start_as_current_span("process_request"):
        data = request.json
        name = data.get("name")
        language = data.get("language")

        if not name or not language:
            logger.warning("Invalid input: Missing name or language")
            return jsonify({"error": "Name and language are required."}), 400

        try:
            add_user(name, language)
            logger.info(f"User data saved: Name={name}, Language={language}")
            return jsonify({"message": f"Hello {name}, Your native language is {language}"}), 200
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            return jsonify({"error": "Internal server error."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
