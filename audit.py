import logging
import logging.handlers
import datetime
import inspect
import json
import os
import socket

from typing import Optional, Dict, Any


class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            # Rotating file handler
            handler = logging.handlers.RotatingFileHandler(
                'audit.log',
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )

            formatter = logging.Formatter(
                '%(asctime)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_event(self, event_code: str, user_id: int = 0, key_id: int = 0,
                  extra_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Audit logging with structured data.
        """
        service_name = "image_processor"
        hostname = socket.gethostname()

        if extra_data is None:
            extra_data = {}

        try:
            frame = inspect.currentframe().f_back
            caller_info = {
                "caller_function": frame.f_code.co_name,
                "caller_filename": os.path.basename(frame.f_code.co_filename),
                "caller_line_number": frame.f_lineno
            }
            extra_data["caller_info"] = caller_info
        except (AttributeError, ValueError):
            pass

        log_data = {
            "event_code": event_code,
            "service": service_name,
            "hostname": hostname,
            "user_id": user_id,
            "key_id": key_id,
            "extra_data": extra_data
        }

        # Логируем как JSON для удобства парсинга
        self.logger.info(json.dumps(log_data, ensure_ascii=False))


_audit_logger = AuditLogger()


def audit_log(event_code: str, user_id: int = 0, key_id: int = 0,
              extra_data: Optional[Dict[str, Any]] = None) -> None:
    """
    Audit logging function.
    """
    _audit_logger.log_event(event_code, user_id, key_id, extra_data)