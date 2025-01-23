from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

def setup_tracing(service_name="default-service"):
    # Set up tracer provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Add a span processor and exporter (console exporter here for simplicity)
    span_processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(span_processor)

    # Return the tracer
    return trace.get_tracer(service_name)
