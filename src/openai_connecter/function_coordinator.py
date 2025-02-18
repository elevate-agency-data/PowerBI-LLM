import json
from typing import Optional, Tuple, Dict, Any
from src.json_operator.json_extraction import *
from src.openai_connecter.general_openai_connecter import *
from src.openai_connecter.summarize_dashboard import *
from src.openai_connecter.modify_dashboard import *
from src.json_operator.json_update import *
import config.config as config

class FunctionCoordinator:
    """Coordinates different functions and handles the business logic of the application."""
    
    def __init__(self, function_descriptions: list):
        self.function_descriptions = function_descriptions

    def process_request(self, text: str, report_json_content: dict, model_bim_content: dict) -> Tuple[Optional[str], Optional[bytes], str]:
        """
        Process the user's request and coordinate the appropriate services.
        
        Returns:
        - modified_json: JSON string if the report was modified
        - file_content: Bytes if documentation was generated
        - message: Status or error message
        """
        try:
            output = generate_completion(text, self.function_descriptions)
            function_name = output.get("function_call", {}).get("name")

            if function_name == "add_read_me":
                return self._handle_readme_generation(output, report_json_content)
            elif function_name == "summary_in_target_platform":
                return self._handle_documentation_generation(output, report_json_content, model_bim_content)
            elif function_name == "slicer_uniformisation_in_report":
                return self._handle_slicer_uniformisation(text, report_json_content)
            else:
                return None, None, config.UNSUPPORTED_REQUEST_ERROR

        except Exception as e:
            return None, None, f"An error occurred: {str(e)}"

    def _handle_readme_generation(self, output: Dict[str, Any], report_json_content: dict) -> Tuple[str, None, str]:
        """Handle the generation of a README page."""
        extracted_report = extract_dashboard_by_page(report_json_content)
        summary_dashboard, overview_all_pages = summarize_dashboard_by_page(extracted_report)
        arguments = json.loads(output.get("function_call", {}).get("arguments", "{}"))
        updated_report = add_read_me(arguments['dashboard_summary'], arguments['pages'])
        report_json_content['sections'].insert(0, updated_report["sections"][0])
        return json.dumps(report_json_content, indent=4), None, config.MODIFICATION_SUCCESS

    def _handle_documentation_generation(self, output: Dict[str, Any], report_json_content: dict, model_bim_content: dict) -> Tuple[None, bytes, str]:
        """Handle the generation of documentation."""
        args = json.loads(output.function_call.arguments)
        language = args.get("language", config.DEFAULT_LANGUAGE)
        target_platform = args.get("platform", config.DEFAULT_PLATFORM)

        extracted_report = extract_dashboard_by_page(report_json_content)
        extracted_dataset = extract_relevant_parts_dataset(model_bim_content)
        extracted_measures = extract_measures_name_and_expression(extracted_dataset['measures'])

        summary_dashboard, overview_all_pages = summarize_dashboard_by_page(
            extracted_report, target_platform=target_platform, language=language
        )
        
        overall_summary = global_summary_dashboard(
            overview_all_pages, target_platform=target_platform, language=language
        )

        summary_table = summarize_table_source(
            extracted_dataset['tables'], target_platform=target_platform, language=language
        )

        summary_measure_overview = create_measures_overview_table(extracted_measures, target_platform)
        summary_measure_detailed = create_measures_by_column_table(extracted_measures, target_platform)

        text_list = [
            config.DOC_DASHBOARD_OVERVIEW,
            f"{overall_summary}\n\n",
            config.DOC_DETAILED_INFO,
            f"{summary_dashboard}\n\n",
            config.DOC_DATASET_INFO,
            config.DOC_TABLE_SOURCE,
            f"{summary_table}\n\n",
            config.DOC_MEASURES_SUMMARY,
            f"{summary_measure_overview}\n\n",
            config.DOC_DETAILED_MEASURES,
            f"{summary_measure_detailed}\n\n"
        ]

        file_content = "\n\n".join(text_list).encode('utf-8')
        return None, file_content, config.MODIFICATION_SUCCESS

    def _handle_slicer_uniformisation(self, text: str, report_json_content: dict) -> Tuple[str, None, str]:
        """Handle the uniformisation of slicers."""
        df = build_df(report_json_content)
        result = process_dashboard_request(text, df)
        dict_slicers = json.dumps(result, indent=2, ensure_ascii=False)
        dict_slicers = json.loads(dict_slicers)
        updated_json = modify_json(report_json_content, dict_slicers, df)
        return json.dumps(updated_json, ensure_ascii=False, indent=4), None, config.MODIFICATION_SUCCESS 