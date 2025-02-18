"""Main Streamlit application for the PowerBI Assistant."""

import streamlit as st
import openai
from src.file_operator.file_operations import *
from src.openai_connecter.function_coordinator import FunctionCoordinator
import config.config as config
import config.function_descriptions as function_descriptions

def main():
    """Main function to run the Streamlit application."""
    st.title(config.TITLE)

    # Sidebar for API key input
    openai_api_key = st.sidebar.text_input(config.API_KEY_LABEL, type="password")
    openai.api_key = openai_api_key

    # Form for user input and file upload
    with st.form('pbip_form'):
        text = st.text_area(config.REQUEST_LABEL, config.DEFAULT_REQUEST_TEXT)
        zip_file = st.file_uploader(config.FILE_UPLOAD_LABEL, type=['zip'])
        submitted = st.form_submit_button(config.SUBMIT_BUTTON_LABEL)

    # Process the form submission
    if submitted:
        if not openai_api_key.startswith('sk-'):
            st.warning(config.API_KEY_ERROR, icon='⚠')
        elif zip_file is None:
            st.warning(config.FILE_UPLOAD_ERROR, icon='⚠')
        else:
            # Extract report.json and model.bim from the uploaded PBIP folder
            report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path = extract_report_and_model(zip_file)
            
            # Initialize the service coordinator
            coordinator = FunctionCoordinator(function_descriptions.FUNCTION_DESCRIPTIONS)
            
            # Process the request
            modified_json, file_content, message = coordinator.process_request(text, report_json_content, model_bim_content)
            
            # Display the message
            if "error" in message.lower():
                st.error(message)
            else:
                st.success(message)
            
            # Handle the results
            if modified_json:
                # Write back the modified report.json and create the zip file
                modified_zip = write_modified_zip(modified_json, report_json_path, inner_folder_path)
                
                # Provide a download button for the modified zip file
                st.download_button(
                    label=f'Download {config.MODIFIED_PBIP_FILENAME}',
                    data=modified_zip,
                    file_name=config.MODIFIED_PBIP_FILENAME,
                    mime='application/zip'
                )
            
            elif file_content:
                # Create a downloadable link for the documentation file
                st.download_button(
                    label=f'Download {config.DOCUMENTATION_FILENAME}',
                    data=file_content,
                    file_name=config.DOCUMENTATION_FILENAME,
                    mime='text/plain'
                )

if __name__ == "__main__":
    main()
