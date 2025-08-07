import sys
import logging
from typing import Any, Dict
import structlog
from structlog.stdlib import LoggerFactory
from .settings import get_settings


def configure_logging() -> None:
   
    settings = get_settings()
    
    
    structlog.configure(
        processors=[
            # Add log level and timestamp
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            # JSON formatting for production, console for development
            structlog.processors.JSONRenderer()
            if settings.environment == "production"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.observability.log_level),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
   
    return structlog.get_logger(name)


class LoggerMixin:
    
    
    @property
    def logger(self) -> structlog.stdlib.BoundLogger:
       
        return get_logger(self.__class__.__name__)
    
    def log_event(self, event: str, **kwargs: Any) -> None:
       
        self.logger.info(event, **kwargs)
    
    def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        
        self.logger.error(
            "Error occurred",
            error=str(error),
            error_type=type(error).__name__,
            **(context or {})
        )
