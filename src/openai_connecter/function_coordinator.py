import json
from typing import Optional, Tuple, Dict, Any, Callable
from src.json_operator.json_extraction import *
from src.openai_connecter.general_openai_connecter import *
from src.openai_connecter.summarize_dashboard import *
import config.config as config
from config.translation import t
from src.openai_connecter.handlers.readme_function_handler import ReadmeFunctionHandler
from src.openai_connecter.handlers.documentation_function_handler import (
    DocumentationFunctionHandler,
)


class FunctionCoordinator:
    """
    Coordinates higher-level operations by routing to function-specific handlers.

    Open/Closed Principle:
    - New capabilities should be added by registering a new handler,
      without modifying the core coordination logic.
    """

    def __init__(self, function_descriptions: list):
        self.function_descriptions = function_descriptions
        self._readme_handler = ReadmeFunctionHandler(function_descriptions)
        self._documentation_handler = DocumentationFunctionHandler()
        # Registry of function name -> handler callable
        # Handlers share a common signature via small adapter lambdas.
        self._handlers: Dict[
            str,
            Callable[
                [
                    Optional[Dict[str, Any]],
                    str,
                    dict,
                    dict,
                    list,
                    str,
                    str,
                    Any,
                ],
                Tuple[Optional[str], Optional[bytes], str],
            ],
        ] = {
            "add_read_me": lambda output, text, report_json, model_bim, images, lang, model, client: self._readme_handler.process(  # noqa: E501
                text,
                report_json,
                model_bim,
                images,
                lang,
                model,
                client,
                output,
            ),
            "summary_in_target_platform": lambda output, text, report_json, model_bim, images, lang, model, client: self._documentation_handler.process(  # noqa: E501
                text,
                report_json,
                model_bim,
                images,
                lang,
                model,
                client,
                output,
            ),
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

            return handler(
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

