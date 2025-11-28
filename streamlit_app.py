"""Streamlit entry point that orchestrates UI flow and dispatches requests."""

import streamlit as st
import openai
from openai import OpenAI
from src.openai_connecter.function_coordinator import FunctionCoordinator
import config.function_descriptions as function_descriptions
from config.translation import t
from src.ui.sidebar import render_sidebar
from src.ui.inputs import render_inputs
from src.validators.input_validator import validate_inputs
from src.handlers.readme_handler import handle_readme_generation
from src.handlers.documentation_handler import handle_documentation_generation


def main():
    """Main function to run the Streamlit application."""

    openai_api_key, selected_language, selected_model = render_sidebar()
    
    st.title(t(selected_language, "app_title"))
    st.text(t(selected_language, "app_description"))
    (
        zip_file,
        pdf_file,
        generate_readme,
        generate_description,
    ) = render_inputs(selected_language, t)

    is_valid, error_message = validate_inputs(openai_api_key, zip_file, pdf_file)

    if not is_valid:
        st.warning(error_message, icon="⚠")
        return

    openai.api_key = openai_api_key
    openai_client = OpenAI(api_key=openai_api_key)
    coordinator = FunctionCoordinator(function_descriptions.FUNCTION_DESCRIPTIONS)

    if generate_readme:
        handle_readme_generation(
            coordinator,
            zip_file,
            pdf_file,
            selected_language,
            selected_model,
            openai_client,
        )
    elif generate_description:
        handle_documentation_generation(
            coordinator,
            zip_file,
            selected_language,
            selected_model,
            openai_client,
        )
            
if __name__ == "__main__":
    main()
