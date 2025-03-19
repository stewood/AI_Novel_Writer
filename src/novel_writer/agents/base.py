from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..config.logging import get_logger

class BaseAgent(ABC):
    """Base class for all agents in the novel_writer system."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent with a name and optional configuration."""
        self.name = name
        self.config = config or {}
        self.logger = get_logger(f"agent.{name}")
        
    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """Execute the agent's main functionality."""
        pass
    
    def log_start(self, message: str, **kwargs):
        """Log the start of an operation."""
        self.logger.info(f"Starting {message}", extra=kwargs)
        
    def log_end(self, message: str, **kwargs):
        """Log the completion of an operation."""
        self.logger.info(f"Completed {message}", extra=kwargs)
        
    def log_error(self, message: str, error: Exception, **kwargs):
        """Log an error that occurred during execution."""
        self.logger.error(f"Error in {message}: {str(error)}", extra=kwargs)
        
    def log_debug(self, message: str, **kwargs):
        """Log debug information."""
        self.logger.debug(message, extra=kwargs)
        
    def log_superdebug(self, message: str, **kwargs):
        """Log super detailed debug information."""
        self.logger.superdebug(message, extra=kwargs)
        
    def validate_input(self, data: Dict[str, Any], required_fields: list) -> bool:
        """Validate that all required fields are present in the input data."""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            self.log_error("Input validation failed", ValueError(f"Missing required fields: {missing_fields}"))
            return False
        return True 