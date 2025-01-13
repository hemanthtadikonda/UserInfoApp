# Backend: Python Flask Application
from flask import Flask, request, jsonify
import sqlite3
import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Setup tracing
resource = Resource(attributes={"service.name": "user-info-app"})
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# Database setup
def init_db():
    connection = sqlite3.connect('user_data.db')
    with connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS user_info (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                language TEXT NOT NULL)''')
    connection.close()

def add_user(name, language):
    connection = sqlite3.connect('user_data.db')
    with connection:
        connection.execute('INSERT INTO user_info (name, language) VALUES (?, ?)', (name, language))
    connection.close()

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
    init_db()
    app.run(host='0.0.0.0', port=5000)