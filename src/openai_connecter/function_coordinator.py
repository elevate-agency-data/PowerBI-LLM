import json
from typing import Optional, Tuple, Dict, Any
from src.json_operator.json_extraction import *
from src.openai_connecter.general_openai_connecter import *
from src.openai_connecter.summarize_dashboard import *
from src.openai_connecter.modify_dashboard import *
from src.json_operator.json_update import *
import config.config as config
from config.translation import t

class FunctionCoordinator:
    """Coordinates different functions and handles the business logic of the application."""
    
    def __init__(self, function_descriptions: list):
        self.function_descriptions = function_descriptions

    def process_request(self, text: str, report_json_content: dict, model_bim_content: dict, report_images: list, language: str = config.DEFAULT_LANGUAGE, model_name: str = config.DEFAULT_MODEL, openai_client = None) -> Tuple[Optional[str], Optional[bytes], str]:
        """
        Process the user's request and coordinate the appropriate services.
        
        Returns:
        - modified_json: JSON string if the report was modified
        - file_content: Bytes if documentation was generated
        - message: Status or error message
        """
        try:
            text_with_language = f"{text}\n\nPreferred output language: {language}\nPreferred model: {model_name}"

            output = generate_completion(text_with_language, self.function_descriptions, model_name, openai_client)
            function_name = output.function_call.name


            if function_name == "add_read_me":
                print("coordinator")
                return self._handle_readme_generation(output, report_json_content, report_images, language, model_name,openai_client)
            elif function_name == "summary_in_target_platform":
                return self._handle_documentation_generation(output, report_json_content, model_bim_content, language, model_name, openai_client)
            elif function_name == "slicer_uniformisation_in_report":
                return self._handle_slicer_uniformisation(text, report_json_content, language, model_name)
            else:
                return None, None, config.UNSUPPORTED_REQUEST_ERROR

        except Exception as e:
            return None, None, f"An error occurred: {str(e)}"

    def _handle_readme_generation(self, output: Dict[str, Any], report_json_content: dict, report_images: list, language, model_name,openai_client) -> Tuple[str, None, str]:
        """Handle the generation of a README page."""
        print("step1")
        extracted_report = extract_dashboard_by_page(report_json_content)
        #summary_dashboard, overview_all_pages = summarize_dashboard_by_page(extracted_report, target_platform=config.DEFAULT_PLATFORM, language=language, model_name=model_name)
        print("Step2")
        summary_dashboard, overview_all_pages = summarize_dashboard_by_page_png_json(extracted_report,report_images, target_platform=config.DEFAULT_PLATFORM, language=language, model_name=model_name, openai_client = openai_client)
        arguments_str = prepare_arguments_add_read_me(overview_all_pages, self.function_descriptions, language=language, model_name=model_name, openai_client = openai_client)
        # Parse the JSON string into a dictionary
        arguments = json.loads(arguments_str)
        updated_report = add_read_me(arguments['dashboard_summary'], arguments['pages'], language=language)
        report_json_content['sections'].insert(0, updated_report["sections"][0])
        return json.dumps(report_json_content, indent=4), None, config.MODIFICATION_SUCCESS

    def _handle_documentation_generation(self, output: Dict[str, Any], report_json_content: dict, model_bim_content: dict, language_override, model_name, openai_client) -> Tuple[None, bytes, str]:
        """Handle the generation of documentation."""
        args = json.loads(output.function_call.arguments)
        language = args.get("language") or language_override
        target_platform = args.get("platform", config.DEFAULT_PLATFORM)

        extracted_report = extract_dashboard_by_page(report_json_content)
        extracted_dataset = extract_relevant_parts_dataset(model_bim_content)
        extracted_measures = extract_measures_name_and_expression(extracted_dataset['measures'])
        summary_dashboard, overview_all_pages = summarize_dashboard_by_page(
            extracted_report, target_platform=target_platform, language=language, model_name=model_name, openai_client=openai_client
        )
        overall_summary = global_summary_dashboard(
            overview_all_pages, target_platform=target_platform, language=language, model_name=model_name, openai_client=openai_client
        )

        summary_table = summarize_table_source(
            extracted_dataset['tables'], target_platform=target_platform, language=language, model_name=model_name, openai_client=openai_client
        )

        summary_measure_overview = create_measures_overview_table(extracted_measures, target_platform, language=language, model_name=model_name, openai_client=openai_client)
        summary_measure_detailed = create_measures_by_column_table(extracted_measures, target_platform, language=language, model_name=model_name, openai_client=openai_client)

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
