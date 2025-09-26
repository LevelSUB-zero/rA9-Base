"""
Logging configuration for RA9.

This module provides structured logging with proper formatting and handlers.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import structlog
from .config import get_config


def setup_logging(
    log_level: Optional[str] = None,
    log_file: Optional[Path] = None,
    log_format: Optional[str] = None,
    enable_json: bool = False
) -> None:
    """Setup structured logging for RA9."""
    
    config = get_config()
    
    # Use provided values or fall back to config
    level = log_level or config.log_level
    file_path = log_file or config.log_file
    format_str = log_format or config.log_format
    
    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if enable_json:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_str,
        handlers=_get_handlers(file_path)
    )


def _get_handlers(log_file: Optional[Path] = None) -> list:
    """Get logging handlers."""
    handlers = [logging.StreamHandler(sys.stdout)]
    
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    return handlers


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class RA9Logger:
    """RA9-specific logger with common patterns."""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message."""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message."""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message."""
        self.logger.error(message, **kwargs)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message."""
        self.logger.debug(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """Log critical message."""
        self.logger.critical(message, **kwargs)
    
    def agent_start(self, agent_name: str, query: str) -> None:
        """Log agent start."""
        self.logger.info(
            "Agent started",
            agent=agent_name,
            query=query[:100] + "..." if len(query) > 100 else query
        )
    
    def agent_complete(self, agent_name: str, result: Dict[str, Any]) -> None:
        """Log agent completion."""
        self.logger.info(
            "Agent completed",
            agent=agent_name,
            quality_score=result.get("quality_score", 0),
            iterations=result.get("iterations", 0)
        )
    
    def memory_operation(self, operation: str, key: str, success: bool) -> None:
        """Log memory operation."""
        self.logger.info(
            "Memory operation",
            operation=operation,
            key=key,
            success=success
        )
    
    def api_call(self, provider: str, endpoint: str, success: bool, tokens: int = 0) -> None:
        """Log API call."""
        self.logger.info(
            "API call",
            provider=provider,
            endpoint=endpoint,
            success=success,
            tokens=tokens
        )
    
    def workflow_stage(self, stage: str, status: str, details: Optional[str] = None) -> None:
        """Log workflow stage."""
        self.logger.info(
            "Workflow stage",
            stage=stage,
            status=status,
            details=details
        )
