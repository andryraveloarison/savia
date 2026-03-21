import logging
import time
from contextvars import ContextVar
from pythonjsonlogger import jsonlogger

from app.shared.types.common import CorrelationId, DurationMs
from app.shared.types.json import JsonDict

correlation_id_ctx: ContextVar[CorrelationId] = ContextVar("correlation_id", default="n/a")

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record: JsonDict, record: logging.LogRecord, message_dict: JsonDict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record["correlation_id"] = correlation_id_ctx.get()
        if not log_record.get("timestamp"):
            log_record["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if log_record.get("levelname"):
            log_record["level"] = log_record["levelname"].upper()
        else:
            log_record["level"] = record.levelname

def setup_logging():
    logHandler = logging.StreamHandler()
    formatter = CustomJsonFormatter("%(timestamp)s %(level)s %(name)s %(message)s")
    logHandler.setFormatter(formatter)

    # Reset les handlers par défaut pour ne pas avoir de doublons
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    root_logger.addHandler(logHandler)
    root_logger.setLevel(logging.INFO)

def log_ticket_analysis(payload_ticket_id: str, engine_version: str, action: str, duration_ms: DurationMs):
    """
    Log structuré après l'analyse d'un ticket.
    """
    logger = logging.getLogger("savia")
    logger.info(
        f"Ticket analysis completed for {payload_ticket_id}",
        extra={
            "ticket_id": payload_ticket_id,
            "engine_version": engine_version,
            "action": action,
            "duration_ms": round(duration_ms, 2)
        }
    )
