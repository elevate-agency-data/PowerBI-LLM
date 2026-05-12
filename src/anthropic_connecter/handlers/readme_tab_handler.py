"""TabHandler for the README tab (inject README page into report.json)."""

import json

import config.config as config
from src.json_operator.json_extraction import extract_dashboard_by_page
from src.json_operator.json_update import add_read_me
from src.anthropic_connecter.summarize_dashboard import (
    summarize_dashboard_by_page_png_json,
    prepare_readme_arguments,
)
from src.anthropic_connecter.handlers.base_handler import (
    TabHandler,
    HandlerRequest,
    HandlerResponse,
)


class ReadmeTabHandler(TabHandler):
    """Generate a README page and return the modified report.json content."""

    def process(self, request: HandlerRequest) -> HandlerResponse:
        extracted_report = extract_dashboard_by_page(request.report_json_content)

        _, overview_all_pages = summarize_dashboard_by_page_png_json(
            extracted_report,
            request.report_images,
            target_platform=config.DEFAULT_PLATFORM,
            language=request.language,
            anthropic_client=request.anthropic_client,
        )

        arguments = prepare_readme_arguments(
            overview_all_pages,
            language=request.language,
            anthropic_client=request.anthropic_client,
        )

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
