from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from mtp6coopnw.observability.events import EventRecord
from mtp6coopnw.observability.redaction import redact_mapping


@dataclass(slots=True)
class StructuredLogger:
    logger: logging.Logger

    def emit(self, event: EventRecord, *, level: int = logging.INFO) -> None:
        payload = redact_mapping(event.to_dict())
        self.logger.log(level, json.dumps(payload, ensure_ascii=False, sort_keys=True))


def create_logger(name: str, handler: logging.Handler | None = None) -> StructuredLogger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if handler is not None:
        logger.handlers.clear()
        logger.addHandler(handler)
    elif not logger.handlers:
        logger.addHandler(logging.StreamHandler())

    return StructuredLogger(logger)
