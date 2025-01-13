from flask import Flask, request, jsonify
from db_setup import init_db
from utils import add_user
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup logging
logging.basicConfig(
    filename="logs/app.log",
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

        add_user(name, language)
        logger.info(f"User data saved: Name={name}, Language={language}")
        return jsonify({"message": f"Hello {name}, Your native language is {language}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
