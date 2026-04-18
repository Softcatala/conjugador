import logging
import os
from pathlib import Path

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTEL_RESOURCE = Resource.create({"service.name": "conjugador"})


def _init_otel_logging(level: int) -> None:
    """
    Sets up the OpenTelemetry log pipeline: LoggerProvider -> BatchProcessor -> OTLP exporter.

    The OTLP endpoint is read from the standard OTEL_EXPORTER_OTLP_ENDPOINT env var
    by the OTLPLogExporter automatically.
    """
    logger_provider = LoggerProvider(resource=OTEL_RESOURCE)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter())
    )
    set_logger_provider(logger_provider)

    otel_handler = LoggingHandler(
        level=level, logger_provider=logger_provider
    )
    logging.getLogger().addHandler(otel_handler)


def _init_otel_tracing() -> None:
    """
    Sets up the OpenTelemetry trace pipeline: TracerProvider -> BatchProcessor -> OTLP exporter.

    The OTLP endpoint is read from the standard OTEL_EXPORTER_OTLP_ENDPOINT env var
    by the OTLPSpanExporter automatically.
    """
    tracer_provider = TracerProvider(resource=OTEL_RESOURCE)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter())
    )
    trace.set_tracer_provider(tracer_provider)


def init_logging() -> None:
    """
    Initializes all the logging environment such as the Log Level, and Log File.
    """
    LOGDIR = os.environ.get("LOGDIR", "")
    LOGLEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
    logger = logging.getLogger()
    logfile = Path(LOGDIR) / "web-service.log"
    hdlr = logging.handlers.RotatingFileHandler(
        logfile, maxBytes=1024 * 1024, backupCount=1
    )
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(LOGLEVEL)

    console = logging.StreamHandler()
    console.setLevel(LOGLEVEL)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)

    _init_otel_tracing()
    _init_otel_logging(logger.level)
