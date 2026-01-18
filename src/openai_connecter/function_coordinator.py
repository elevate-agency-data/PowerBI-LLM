import json
from typing import Optional, Tuple, Dict, Any
from src.json_operator.json_extraction import *
from src.openai_connecter.general_openai_connecter import *
from src.openai_connecter.summarize_dashboard import *
import config.config as config
from src.openai_connecter.handlers.readme_function_handler import ReadmeFunctionHandler
from src.openai_connecter.handlers.documentation_function_handler import (
    DocumentationFunctionHandler,
)
from src.openai_connecter.handlers.base_handler import FunctionHandler, HandlerRequest, HandlerResponse


class FunctionCoordinator:
    """
    Coordinates higher-level operations by routing to function-specific handlers.

    Dependency Inversion Principle (DIP):
    - Depends on the FunctionHandler abstraction, not concrete handler implementations
    - New capabilities can be added by implementing FunctionHandler and registering it,
      without modifying the core coordination logic (Open/Closed Principle)
    """

    def __init__(self, function_descriptions: list):
        self.function_descriptions = function_descriptions
        # Registry of function name -> FunctionHandler instance
        # All handlers implement the FunctionHandler interface
        self._handlers: Dict[str, FunctionHandler] = {
            "add_read_me": ReadmeFunctionHandler(function_descriptions),
            "summary_in_target_platform": DocumentationFunctionHandler(),
        }

    def process_request(
        self,
        text: str,
        report_json_content: dict,
        model_bim_content: dict,
        report_images: list,
        language: str = config.DEFAULT_LANGUAGE,
        model_name: str = config.DEFAULT_MODEL,
        openai_client = None,
        requested_function: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[bytes], str]:
        """
        Process the user's request and coordinate the appropriate services.
        
        Returns:
        - modified_json: JSON string if the report was modified
        - file_content: Bytes if documentation was generated
        - message: Status or error message
        """
        try:
            output = None
            function_name = requested_function

            if not function_name:
                text_with_language = f"{text}\n\nPreferred output language: {language}\nPreferred model: {model_name}"
                output = generate_completion(text_with_language, self.function_descriptions, model_name, openai_client)
                function_call = getattr(output, "function_call", None)
                if not function_call:
                    return None, None, config.UNSUPPORTED_REQUEST_ERROR
                function_name = function_call.name
            else:
                output = None

            handler = self._handlers.get(function_name)
            if not handler:
                return None, None, config.UNSUPPORTED_REQUEST_ERROR

            # Convert parameters to HandlerRequest and call handler
            # Then convert HandlerResponse back to tuple for backward compatibility
            return self._handle_with_new_interface(
                handler,
                output,
                text,
                report_json_content,
                model_bim_content,
                report_images,
                language,
                model_name,
                openai_client,
            )

        except Exception as e:
            return None, None, f"An error occurred: {str(e)}"
    
    def _handle_with_new_interface(
        self,
        handler: FunctionHandler,
        output: Optional[Dict[str, Any]],
        text: str,
        report_json_content: dict,
        model_bim_content: dict,
        report_images: list,
        language: str,
        model_name: str,
        openai_client: Any,
    ) -> Tuple[Optional[str], Optional[bytes], str]:
        """
        Adapter method to convert old-style parameters to HandlerRequest
        and convert HandlerResponse back to tuple format.
        
        This allows handlers using the new interface to work with the coordinator
        while maintaining backward compatibility.
        """
        request = HandlerRequest(
            text=text,
            report_json_content=report_json_content,
            model_bim_content=model_bim_content,
            report_images=report_images,
            language=language,
            model_name=model_name,
            openai_client=openai_client,
            output=output,
        )
        response = handler.process(request)
        return response.modified_json, response.file_content, response.message

