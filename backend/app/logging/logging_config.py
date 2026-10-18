import logging
import logging.config
import logging.handlers
import json
import os
import socket
from datetime import datetime, timezone
import queue

class JSONFormatter(logging.Formatter):
    def __init__(self):
        super().__init__()
        self.hostname = socket.gethostname()
        self.service_name = os.getenv("SERVICE_NAME", "raven")

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": self.service_name,
            "hostname": self.hostname,
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        if record.exc_info:
            exc_type, exc_value, _ = record.exc_info
            log_data["exception"] = f"{exc_type.__name__}: {exc_value}"

        return json.dumps(log_data, ensure_ascii=False)


LOG_QUEUE = queue.Queue(maxsize=10000)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "json": {
            "()": JSONFormatter,
        }
    },

    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/app.log",
            "maxBytes": 50_000_000,
            "backupCount": 10,
            "encoding": "utf-8",
            "formatter": "json",
            "level": "INFO",
        },

        "queue": {
            "class": "logging.handlers.QueueHandler",
            "queue": LOG_QUEUE,
        },
    },

    "root": {
        "level": "INFO",
        "handlers": ["queue"],
    },

    "loggers": {
        "uvicorn.access": {
            "level": "WARNING",
            "handlers": ["queue"],
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "CRITICAL",
            "handlers": ["queue"],
            "propagate": False,
        },
    },
}


def setup_logging() -> logging.handlers.QueueListener:
    os.makedirs("logs", exist_ok=True)

    logging.config.dictConfig(LOGGING_CONFIG)

    file_handler = logging.getHandlerByName("file")

    queue_listener = logging.handlers.QueueListener(
        LOG_QUEUE,
        file_handler,
        respect_handler_level=True,
    )
    queue_listener.start()

    logging.getLogger("app").info("Logging initialized")

    return queue_listener
