import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from db_setup import init_db
from utils import add_user
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Ensure logs directory exists
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Setup application logging
app_log_file = os.path.join(log_dir, 'app.log')
logging.basicConfig(
    filename=app_log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("app_logger")

# Setup tracing logging
trace_log_file = os.path.join(log_dir, 'trace.log')
trace_logger = logging.getLogger("trace_logger")
trace_logger.setLevel(logging.INFO)
trace_handler = logging.FileHandler(trace_log_file)
trace_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
trace_logger.addHandler(trace_handler)

# Setup tracing
tracer_provider = TracerProvider()
span_processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://<otel-collector-host>:4317"))
tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# Flask application
app = Flask(__name__)
CORS(app)  # Enable CORS for the app

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
            trace_logger.info(f"Trace: Processed user {name} with language {language}")
            return jsonify({"message": f"Hello {name}, Your native language is {language}"}), 200
        except Exception as e:
            logger.error(f"Error saving user data: {e}")
            trace_logger.error(f"Trace Error: {e}")
            return jsonify({"error": "Internal server error."}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return jsonify({"status": "healthy"}), 200

if __name__ == "__main__":
    try:
        init_db()  # Initialize the database
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
        trace_logger.error(f"Trace Error: Application failed to start: {e}")
