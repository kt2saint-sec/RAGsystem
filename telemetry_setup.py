"""
telemetry_setup.py
This module configures the OpenTelemetry SDK for the RAG system.
It sets up console exporters for both traces and metrics, so all telemetry
data is printed directly to the terminal.
"""
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource

def initialize_telemetry(service_name: str = "RAG_System"):
    """
    Initializes OpenTelemetry trace and metric providers with console exporters.
    """
    # Create a resource to identify our service
    resource = Resource(attributes={
        "service.name": service_name,
    })

    # --- Trace Configuration ---
    # Set up a TracerProvider with our resource
    trace_provider = TracerProvider(resource=resource)
    
    # Set up a console exporter for traces
    console_span_exporter = ConsoleSpanExporter()
    
    # Use a BatchSpanProcessor to send spans to the exporter
    trace_provider.add_span_processor(BatchSpanProcessor(console_span_exporter))
    
    # Set the global TracerProvider
    trace.set_tracer_provider(trace_provider)

    # --- Metric Configuration ---
    # Set up a console exporter for metrics
    console_metric_exporter = ConsoleMetricExporter()
    
    # Use a PeriodicExportingMetricReader to collect and send metrics
    metric_reader = PeriodicExportingMetricReader(console_metric_exporter)
    
    # Set up a MeterProvider with our resource and reader
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    
    # Set the global MeterProvider
    metrics.set_meter_provider(meter_provider)

    print(f"OpenTelemetry initialized for service '{service_name}' with Console exporters.")
