"""Optional OpenTelemetry setup (no-op if packages missing)."""

import os


def setup_tracing(service_name: str) -> None:
    if os.getenv("ENABLE_OTEL", "false").lower() not in {"1", "true", "yes"}:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter())
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception:
        # Otel not installed or exporter not configured; skip gracefully
        return
