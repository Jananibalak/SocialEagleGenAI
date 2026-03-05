import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AuditLogger:
    @staticmethod
    def log_event(user_id: int, event_type: str, details: Dict[str, Any] = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "details": details or {}
        }

        logger.info(f"AUDIT: {log_entry}")
