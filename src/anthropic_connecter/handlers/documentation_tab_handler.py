"""TabHandler for the Documentation tab (full Markdown documentation)."""

import config.config as config
from config.translation import t
from src.json_operator.json_extraction import (
    extract_dashboard_by_page,
    extract_relevant_parts_dataset,
    extract_measures_name_and_expression,
)
from src.anthropic_connecter.summarize_dashboard import (
    summarize_dashboard_by_page,
    global_summary_dashboard,
    summarize_table_source,
    create_measures_overview_table,
    create_measures_by_column_table,
)
from src.anthropic_connecter.handlers.base_handler import (
    TabHandler,
    HandlerRequest,
    HandlerResponse,
)


class DocumentationTabHandler(TabHandler):
    """Generate Markdown documentation and return it as bytes."""

    def process(self, request: HandlerRequest) -> HandlerResponse:
        language = request.language
        target_platform = config.DEFAULT_PLATFORM

        extracted_report = extract_dashboard_by_page(request.report_json_content)
        extracted_dataset = extract_relevant_parts_dataset(request.model_bim_content)
        extracted_measures = extract_measures_name_and_expression(
            extracted_dataset["measures"]
        )

        summary_dashboard, overview_all_pages = summarize_dashboard_by_page(
            extracted_report,
            target_platform=target_platform,
            language=language,
            anthropic_client=request.anthropic_client,
        )
        overall_summary = global_summary_dashboard(
            overview_all_pages,
            target_platform=target_platform,
            language=language,
            anthropic_client=request.anthropic_client,
        )
        summary_table = summarize_table_source(
            extracted_dataset["tables"],
            target_platform=target_platform,
            language=language,
            anthropic_client=request.anthropic_client,
        )
        summary_measure_overview = create_measures_overview_table(
            extracted_measures,
            target_platform,
            language=language,
            anthropic_client=request.anthropic_client,
        )
        summary_measure_detailed = create_measures_by_column_table(
            extracted_measures,
            target_platform,
            language=language,
            anthropic_client=request.anthropic_client,
        )

        text_list = [
            f"{t(language, 'overview')}",
            f"{overall_summary}\n\n",
            f"{t(language, 'detail_info')}",
            f"{summary_dashboard}\n\n",
            f"{t(language, 'dataset_info')}",
            f"{t(language, 'table_source')}",
            f"{summary_table}\n\n",
            f"{t(language, 'measure_suma')}",
            f"{summary_measure_overview}\n\n",
            f"{t(language, 'detail_measure')}",
            f"{summary_measure_detailed}\n\n",
        ]
        file_content = "\n\n".join(text_list).encode("utf-8")
        return HandlerResponse(
            file_content=file_content,
            message=config.MODIFICATION_SUCCESS,
        )
