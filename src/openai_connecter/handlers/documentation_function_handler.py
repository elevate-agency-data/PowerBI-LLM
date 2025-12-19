"""Handler for the `summary_in_target_platform` function (full documentation)."""

import json

import config.config as config
from config.translation import t
from src.json_operator.json_extraction import (
    extract_dashboard_by_page,
    extract_relevant_parts_dataset,
    extract_measures_name_and_expression,
)
from src.openai_connecter.summarize_dashboard import (
    summarize_dashboard_by_page,
    global_summary_dashboard,
    summarize_table_source,
    create_measures_overview_table,
    create_measures_by_column_table,
)
from src.openai_connecter.handlers.base_handler import FunctionHandler, HandlerRequest, HandlerResponse


class DocumentationFunctionHandler(FunctionHandler):
    """
    Encapsulates the business logic for generating detailed documentation.
    
    Implements the FunctionHandler interface, following the Dependency Inversion Principle.
    """

    def process(self, request: HandlerRequest) -> HandlerResponse:
        """
        Generate documentation text and return it as bytes.

        Args:
            request: HandlerRequest containing all necessary data for processing

        Returns:
            HandlerResponse with file_content containing the documentation
        """
        language_override = request.language
        target_platform = config.DEFAULT_PLATFORM

        if request.output and getattr(request.output, "function_call", None):
            try:
                args = json.loads(request.output.function_call.arguments)
            except (TypeError, json.JSONDecodeError):
                args = {}
            language_override = args.get("language") or request.language
            target_platform = args.get("platform", config.DEFAULT_PLATFORM)

        extracted_report = extract_dashboard_by_page(request.report_json_content)
        extracted_dataset = extract_relevant_parts_dataset(request.model_bim_content)
        extracted_measures = extract_measures_name_and_expression(
            extracted_dataset["measures"]
        )

        summary_dashboard, overview_all_pages = summarize_dashboard_by_page(
            extracted_report,
            target_platform=target_platform,
            language=language_override,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )

        overall_summary = global_summary_dashboard(
            overview_all_pages,
            target_platform=target_platform,
            language=language_override,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )

        summary_table = summarize_table_source(
            extracted_dataset["tables"],
            target_platform=target_platform,
            language=language_override,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )

        summary_measure_overview = create_measures_overview_table(
            extracted_measures,
            target_platform,
            language=language_override,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )
        summary_measure_detailed = create_measures_by_column_table(
            extracted_measures,
            target_platform,
            language=language_override,
            model_name=request.model_name,
            openai_client=request.openai_client,
        )

        text_list = [
            f"{t(language_override, 'overview')}",
            f"{overall_summary}\n\n",
            f"{t(language_override, 'detail_info')}",
            f"{summary_dashboard}\n\n",
            f"{t(language_override, 'dataset_info')}",
            f"{t(language_override, 'table_source')}",
            f"{summary_table}\n\n",
            f"{t(language_override, 'measure_suma')}",
            f"{summary_measure_overview}\n\n",
            f"{t(language_override, 'detail_measure')}",
            f"{summary_measure_detailed}\n\n",
        ]

        file_content = "\n\n".join(text_list).encode("utf-8")
        return HandlerResponse(
            file_content=file_content,
            message=config.MODIFICATION_SUCCESS,
        )


