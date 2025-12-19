"""
Base abstraction for function handlers following the Dependency Inversion Principle (DIP).

This module defines the contract that all function handlers must follow,
allowing the FunctionCoordinator to depend on abstractions rather than concrete implementations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, Dict, List


@dataclass
class HandlerRequest:
    """
    Standardized request object that all handlers receive.
    
    This encapsulates all the data needed for processing a function request,
    eliminating the need for handlers to accept many positional parameters.
    """
    text: str
    report_json_content: dict
    model_bim_content: dict
    report_images: List[str]
    language: str
    model_name: str
    openai_client: Any
    output: Optional[Dict[str, Any]] = None


@dataclass
class HandlerResponse:
    """
    Standardized response that all handlers return.
    
    This provides a consistent return format across all handlers,
    making it easier for the coordinator to process results.
    """
    modified_json: Optional[str] = None
    file_content: Optional[bytes] = None
    message: str = ""


class FunctionHandler(ABC):
    """
    Abstract base class defining the contract for all function handlers.
    
    Following the Dependency Inversion Principle:
    - High-level modules (FunctionCoordinator) depend on this abstraction
    - Low-level modules (concrete handlers) implement this abstraction
    - This allows adding new handlers without modifying the coordinator
    """
    
    @abstractmethod
    def process(self, request: HandlerRequest) -> HandlerResponse:
        """
        Process the request and return a standardized response.
        
        Args:
            request: HandlerRequest containing all necessary data
            
        Returns:
            HandlerResponse with the results of processing
        """
        pass

