"""Base agent class for all agents.

This module provides the BaseAgent class that serves as a foundation for all
specialized agents in the novel_writer application, offering common 
functionality including LLM interactions and logging.

Example:
    ```python
    from novel_writer.agents.base_agent import BaseAgent
    from novel_writer.config.llm import LLMConfig

    class MyAgent(BaseAgent):
        async def process(self, input_data: dict) -> dict:
            # Get LLM response
            response = await self._get_llm_response("Generate a story idea")
            return {"result": response}
    ```
"""

import logging
import traceback
from typing import Optional, Dict, Any

from novel_writer.config.llm import LLMConfig

# Initialize logger
logger = logging.getLogger(__name__)

class BaseAgent:
    """Base agent class for all specialized agents.
    
    This class provides common functionality for all agents including
    LLM configuration management and standardized response handling.
    All agent classes should inherit from this base class.
    
    Example:
        ```python
        class StoryAgent(BaseAgent):
            async def generate_story(self, prompt: str) -> str:
                response = await self._get_llm_response(prompt)
                return response
        ```
    """

    def __init__(self, llm_config: LLMConfig):
        """Initialize the base agent.
        
        Args:
            llm_config: Configuration for the LLM client
            
        Example:
            ```python
            config = LLMConfig(api_key="your-api-key")
            agent = MyAgent(config)
            ```
        """
        logger.debug(f"{self.__class__.__name__} initializing")
        self.llm_config = llm_config
        logger.superdebug(f"{self.__class__.__name__} initialized with LLM config: {self.llm_config}")

    async def _get_llm_response(self, prompt: str) -> str:
        """Get a response from the LLM.
        
        Send a prompt to the LLM and process the response. This method handles
        response cleaning, error handling, and logging.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response as a string
            
        Raises:
            Exception: If there is an error getting the response from the LLM
            
        Example:
            ```python
            response = await self._get_llm_response("Generate a story idea")
            ```
        """
        logger.debug(f"{self.__class__.__name__} sending prompt to LLM")
        # Log the full prompt at SUPERDEBUG level for complete traceability
        logger.superdebug(f"{self.__class__.__name__} full prompt:\n{prompt}")
        
        try:
            start_time = logger.superdebug(f"{self.__class__.__name__} LLM request started")
            # Get the response from the LLM
            response = await self.llm_config.get_completion(prompt)
            logger.superdebug(f"{self.__class__.__name__} LLM request completed")
            
            # Log the raw response at SUPERDEBUG level
            logger.superdebug(f"{self.__class__.__name__} raw LLM response:\n{response}")
            
            # Clean up the response
            cleaned = response.strip()
            
            # Remove code block markers if present
            if cleaned.startswith("```") and cleaned.endswith("```"):
                cleaned = cleaned[3:-3].strip()
                logger.superdebug(f"{self.__class__.__name__} removed code block markers")
                
            # Remove markdown prefix if present
            if cleaned.startswith("markdown"):
                cleaned = cleaned[8:].strip()
                logger.superdebug(f"{self.__class__.__name__} removed markdown prefix")
                
            logger.debug(f"{self.__class__.__name__} successfully received and processed LLM response")
            logger.superdebug(f"{self.__class__.__name__} cleaned LLM response:\n{cleaned}")
            
            return cleaned
            
        except Exception as e:
            logger.error(f"{self.__class__.__name__} error getting LLM response: {str(e)}")
            logger.superdebug(f"{self.__class__.__name__} error details:\n{traceback.format_exc()}")
            raise Exception(f"Error getting LLM response: {str(e)}")
            
    def _log_response_parsing(self, method_name: str, raw_data: str, parsed_data: Dict[str, Any]) -> None:
        """Log details about response parsing for debugging.
        
        This method provides standardized logging for response parsing operations,
        helping with debugging and monitoring.
        
        Args:
            method_name: Name of the method doing the parsing
            raw_data: Raw response data being parsed
            parsed_data: The parsed data structure
            
        Example:
            ```python
            self._log_response_parsing("parse_story", raw_response, parsed_story)
            ```
        """
        logger.debug(f"{self.__class__.__name__}.{method_name} successfully parsed response")
        logger.superdebug(f"{self.__class__.__name__}.{method_name} parsing details:")
        logger.superdebug(f"Raw data length: {len(raw_data)} characters")
        logger.superdebug(f"Parsed data structure: {parsed_data}")
        
    def _log_method_start(self, method_name: str, **params) -> None:
        """Log the start of a method call with parameters.
        
        This method provides standardized logging for method entry points,
        including parameter logging with sensitive data filtering.
        
        Args:
            method_name: Name of the method being called
            **params: Parameters passed to the method
            
        Example:
            ```python
            self._log_method_start("generate_story", title="My Story", genre="Fantasy")
            ```
        """
        logger.debug(f"{self.__class__.__name__}.{method_name} started")
        # Filter out sensitive data if needed (e.g. API keys)
        safe_params = {k: v for k, v in params.items() if k != "api_key"}
        logger.superdebug(f"{self.__class__.__name__}.{method_name} parameters: {safe_params}")
        
    def _log_method_end(self, method_name: str, result: Any = None) -> None:
        """Log the end of a method call with result.
        
        Args:
            method_name: Name of the method that completed
            result: Optional result to log
        """
        logger.debug(f"{self.__class__.__name__}.{method_name} completed")
        if result is not None:
            logger.superdebug(f"{self.__class__.__name__}.{method_name} result: {result}")

    def _log_method_error(self, method_name: str, error: Exception) -> None:
        """Log an error that occurred in a method.
        
        Args:
            method_name: Name of the method where the error occurred
            error: The exception that was raised
        """
        logger.error(f"{self.__class__.__name__}.{method_name} error: {str(error)}")
        logger.superdebug(f"{self.__class__.__name__}.{method_name} error details:\n{traceback.format_exc()}") 