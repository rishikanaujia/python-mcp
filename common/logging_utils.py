import json
import logging
from datetime import datetime
import os


class MCPLogger:
    """Logging utilities for MCP."""

    LOG_LEVELS = {
        'ERROR': logging.ERROR,
        'WARN': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG
    }

    def __init__(self, service_name=None, log_level=None):
        self.service_name = service_name or 'mcp-service'

        # Set log level from environment or default to INFO
        env_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
        self.log_level = log_level or self.LOG_LEVELS.get(env_level, logging.INFO)

        # Configure logger
        self.logger = logging.getLogger(self.service_name)
        self.logger.setLevel(self.log_level)

        # Add console handler if not already added
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def _format_log(self, level, message, data=None):
        """Format a log message."""
        log_obj = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level,
            'service': self.service_name,
            'message': message
        }

        if data:
            log_obj['data'] = data

        return json.dumps(log_obj)

    def error(self, message, data=None):
        """Log an error message."""
        self.logger.error(self._format_log('ERROR', message, data))

    def warn(self, message, data=None):
        """Log a warning message."""
        self.logger.warning(self._format_log('WARN', message, data))

    def info(self, message, data=None):
        """Log an info message."""
        self.logger.info(self._format_log('INFO', message, data))

    def debug(self, message, data=None):
        """Log a debug message."""
        self.logger.debug(self._format_log('DEBUG', message, data))