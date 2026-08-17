"""
@sdoc[REQ-ARCH-013]
"""

import json
import logging
from datetime import datetime, timezone

_LEVEL = {"start": logging.INFO, "end": logging.INFO, "error": logging.ERROR}


def emit(
    logger: logging.Logger,
    event_type: str,
    *,
    feature: str,
    req_uid: str,
    correlation_id: str,
    message: str,
) -> None:
    """Emit one structured log event per observability-platform.yaml § log_format.

    @sdoc[REQ-ARCH-013]
    """
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": logging.getLevelName(_LEVEL[event_type]),
        "event_type": event_type,
        "feature": feature,
        "req_uid": req_uid,
        "correlation_id": correlation_id,
        "message": message,
    }
    logger.log(_LEVEL[event_type], json.dumps(record))
