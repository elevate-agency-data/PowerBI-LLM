"""Handler for the `summary_in_target_platform` function (full documentation)."""

import json
from typing import Optional, Tuple, Dict, Any

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


class DocumentationFunctionHandler:
    """Encapsulates the business logic for generating detailed documentation."""

    def process(
        self,
        text: str,
        report_json_content: dict,
        model_bim_content: dict,
        report_images: list,
        language: str,
        model_name: str,
        openai_client: Any,
        output: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Optional[str], Optional[bytes], str]:
        """
        Generate documentation text and return it as bytes.

        Returns:
            - modified_json: always None for this handler
            - file_content: documentation content as bytes
            - message: status message
        """
        language_override = language
        target_platform = config.DEFAULT_PLATFORM

        if output and getattr(output, "function_call", None):
            try:
                args = json.loads(output.function_call.arguments)
            except (TypeError, json.JSONDecodeError):
                args = {}
            language_override = args.get("language") or language
            target_platform = args.get("platform", config.DEFAULT_PLATFORM)

        extracted_report = extract_dashboard_by_page(report_json_content)
        extracted_dataset = extract_relevant_parts_dataset(model_bim_content)
        extracted_measures = extract_measures_name_and_expression(
            extracted_dataset["measures"]
        )

        summary_dashboard, overview_all_pages = summarize_dashboard_by_page(
            extracted_report,
            target_platform=target_platform,
            language=language_override,
            model_name=model_name,
            openai_client=openai_client,
        )

        overall_summary = global_summary_dashboard(
            overview_all_pages,
            target_platform=target_platform,
            language=language_override,
            model_name=model_name,
            openai_client=openai_client,
        )

        summary_table = summarize_table_source(
            extracted_dataset["tables"],
            target_platform=target_platform,
            language=language_override,
            model_name=model_name,
            openai_client=openai_client,
        )

        summary_measure_overview = create_measures_overview_table(
            extracted_measures,
            target_platform,
            language=language_override,
            model_name=model_name,
            openai_client=openai_client,
        )
        summary_measure_detailed = create_measures_by_column_table(
            extracted_measures,
            target_platform,
            language=language_override,
            model_name=model_name,
            openai_client=openai_client,
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
        return None, file_content, config.MODIFICATION_SUCCESS


