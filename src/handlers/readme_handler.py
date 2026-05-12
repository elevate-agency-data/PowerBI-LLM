"""Business logic for the README-generation tab."""

import time

import streamlit as st

import config.config as config
from src.file_operator.file_operations import (
    extract_report_and_model,
    convert_pdf_to_images,
    write_modified_zip,
)
from src.anthropic_connecter.handlers.base_handler import HandlerRequest
from src.anthropic_connecter.handlers.readme_tab_handler import ReadmeTabHandler


def handle_readme_generation(zip_file, pdf_file, selected_language, anthropic_client):
    """Generate a README page and offer the modified PBIP zip for download."""
    start = time.time()
    report_json_content, model_bim_content, inner_folder_path, report_json_path, _ = (
        extract_report_and_model(zip_file)
    )
    report_images = convert_pdf_to_images(pdf_file)

    handler = ReadmeTabHandler()
    try:
        response = handler.process(
            HandlerRequest(
                text="Please add a README page to the dashboard.",
                report_json_content=report_json_content,
                model_bim_content=model_bim_content,
                report_images=report_images,
                language=selected_language,
                anthropic_client=anthropic_client,
            )
        )
    except Exception as exc:
        st.error(f"README generation failed: {exc}")
        return

    print(f"README generation took {time.time() - start:.2f}s")
    if "error" in response.message.lower():
        st.error(response.message)
        return
    st.success(response.message)

    if response.modified_json:
        modified_zip = write_modified_zip(
            response.modified_json, report_json_path, inner_folder_path
        )
        st.download_button(
            label=f"Download {config.MODIFIED_PBIP_FILENAME}",
            data=modified_zip,
            file_name=config.MODIFIED_PBIP_FILENAME,
            mime="application/zip",
        )
