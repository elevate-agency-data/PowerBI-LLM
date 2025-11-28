"""Handler for the `add_read_me` function (README generation in the PBIP)."""

import json
from typing import Optional, Tuple, Dict, Any, List

import config.config as config
from src.json_operator.json_extraction import extract_dashboard_by_page
from src.openai_connecter.summarize_dashboard import summarize_dashboard_by_page_png_json
from src.openai_connecter.general_openai_connecter import prepare_arguments_add_read_me
from src.json_operator.json_update import add_read_me


class ReadmeFunctionHandler:
    """Encapsulates the business logic for generating a README page."""

    def __init__(self, function_descriptions: list):
        self._function_descriptions = function_descriptions

    def process(
        self,
        text: str,
        report_json_content: dict,
        model_bim_content: dict,
        report_images: List[str],
        language: str,
        model_name: str,
        openai_client: Any,
        output: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[str], Optional[bytes], str]:
        """
        Generate a README page and return the modified report.json.

        Returns:
            - modified_json: JSON string if the report was modified
            - file_content: always None for this handler
            - message: status message
        """
        # Extract dashboard structure
        extracted_report = extract_dashboard_by_page(report_json_content)

        # Summarize pages using JSON + screenshots
        _, overview_all_pages = summarize_dashboard_by_page_png_json(
            extracted_report,
            report_images,
            target_platform=config.DEFAULT_PLATFORM,
            language=language,
            model_name=model_name,
            openai_client=openai_client,
        )

        # Ask the model to build arguments for the add_read_me function
        arguments_str = prepare_arguments_add_read_me(
            overview_all_pages,
            self._function_descriptions,
            language=language,
            model_name=model_name,
            openai_client=openai_client,
        )
        arguments = json.loads(arguments_str)

        # Build the README section and insert it into the report JSON
        updated_report = add_read_me(
            arguments["dashboard_summary"],
            arguments["pages"],
            language=language,
        )
        report_json_content["sections"].insert(0, updated_report["sections"][0])

        return json.dumps(report_json_content, indent=4), None, config.MODIFICATION_SUCCESS


