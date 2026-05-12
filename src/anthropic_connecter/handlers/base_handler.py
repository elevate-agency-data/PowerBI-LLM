"""
Base abstraction for tab handlers (Documentation / README tabs).

Defines the contract every tab handler implements, allowing UI code to depend
on an abstraction rather than concrete implementations (DIP). New tab features
must implement this interface — do not add if/elif branches in the dispatcher.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Any, List


@dataclass
class HandlerRequest:
    """Standardized request object passed to every TabHandler."""
    text: str
    report_json_content: dict
    model_bim_content: dict
    report_images: List[str]
    language: str
    anthropic_client: Any


@dataclass
class HandlerResponse:
    """Standardized response returned by every TabHandler."""
    modified_json: Optional[str] = None
    file_content: Optional[bytes] = None
    message: str = ""


class TabHandler(ABC):
    """
    Abstract base class defining the contract for all tab handlers.

    - High-level modules (Streamlit tabs) depend on this abstraction.
    - Low-level modules (concrete tab handlers) implement this abstraction.
    - New tab capabilities are added by subclassing — never by modifying callers.
    """

    @abstractmethod
    def process(self, request: HandlerRequest) -> HandlerResponse:
        """Process the request and return a standardized response."""
