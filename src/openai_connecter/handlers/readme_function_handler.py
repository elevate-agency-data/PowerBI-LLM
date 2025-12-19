"""Handler for the `add_read_me` function (README generation in the PBIP)."""

import json

import config.config as config
from src.json_operator.json_extraction import extract_dashboard_by_page
from src.openai_connecter.summarize_dashboard import summarize_dashboard_by_page_png_json
from src.openai_connecter.general_openai_connecter import prepare_arguments_add_read_me
from src.json_operator.json_update import add_read_me
from src.openai_connecter.handlers.base_handler import FunctionHandler, HandlerRequest, HandlerResponse


class ReadmeFunctionHandler(FunctionHandler):
    """
    Encapsulates the business logic for generating a README page.
    
    Implements the FunctionHandler interface, following the Dependency Inversion Principle.
    """

    def __init__(self, function_descriptions: list):
        self._function_descriptions = function_descriptions

    def process(self, request: HandlerRequest) -> HandlerResponse:
        """
        Generate a README page and return the modified report.json.

        Args:
            request: HandlerRequest containing all necessary data for processing

        Returns:
            HandlerResponse with modified_json containing the updated report
        """
        # Extract dashboard structure
        extracted_report = extract_dashboard_by_page(request.report_json_content)

        # Summarize pages using JSON + screenshots
        _, overview_all_pages = summarize_dashboard_by_page_png_json(
            extracted_report,
            request.report_images,
            target_platform=config.DEFAULT_PLATFORM,
            language=request.language,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )

        # Ask the model to build arguments for the add_read_me function
        arguments_str = prepare_arguments_add_read_me(
            overview_all_pages,
            self._function_descriptions,
            language=request.language,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )
        arguments = json.loads(arguments_str)

        # Build the README section and insert it into the report JSON
        updated_report = add_read_me(
            arguments["dashboard_summary"],
            arguments["pages"],
            language=request.language,
        )
        request.report_json_content["sections"].insert(0, updated_report["sections"][0])

        return HandlerResponse(
            modified_json=json.dumps(request.report_json_content, indent=4),
            message=config.MODIFICATION_SUCCESS,
        )


