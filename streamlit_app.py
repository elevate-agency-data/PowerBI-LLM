"""Main Streamlit application for the PowerBI Assistant."""

import streamlit as st
import openai
from openai import OpenAI
from src.file_operator.file_operations import *
from src.openai_connecter.function_coordinator import FunctionCoordinator
import config.config as config
from config.translation import t
import config.function_descriptions as function_descriptions
import time

def main():
    """Main function to run the Streamlit application."""


    # Sidebar for API key input
    openai_api_key = st.sidebar.text_input(config.API_KEY_LABEL, type="password")
    

    # Sidebar for language selection
    language_options = ["English", "French", "Chinese"]
    default_lang_index = language_options.index(config.DEFAULT_LANGUAGE) if config.DEFAULT_LANGUAGE in language_options else 0
    selected_language = st.sidebar.selectbox("Output language", language_options, index=default_lang_index)
    
    # Sidebar for model selection
    model_options = config.SUPPORTED_MODELS
    default_model_index = model_options.index(config.DEFAULT_MODEL) if config.DEFAULT_MODEL in model_options else 0
    selected_model = st.sidebar.selectbox("OpenAI model", model_options, index=default_model_index)
    
    # Application title and description
    st.title(t(selected_language, "app_title"))
    
    st.text(t(selected_language, 'app_description'))

    # Form for user choice and file upload
    #with st.form('pbip_form'):
        #text = st.text_area(config.REQUEST_LABEL, config.DEFAULT_REQUEST_TEXT)
    zip_file = st.file_uploader(config.FILE_UPLOAD_LABEL, type=['zip'])
        #readme_requested = st.checkbox("Generate README")
        #documentation_requested = st.checkbox("Generate Description")
        #submitted = st.form_submit_button(config.SUBMIT_BUTTON_LABEL)
    pdf_file = st.file_uploader(config.FILE_UPLOAD_LABEL, type=['pdf'])
    
    col1, col2 = st.columns(2)
    generate_readme = col1.button(t(selected_language, 'readme'), disabled=zip_file is None, use_container_width=True)
    generate_description = col2.button(t(selected_language, 'documentation'), disabled=zip_file is None, use_container_width=True)

    # Process the form submission
    #if submitted:

    
    
    if not openai_api_key.startswith('sk-'):
        st.warning(config.API_KEY_ERROR, icon='⚠')
        
    elif zip_file is None:
        st.warning(config.FILE_UPLOAD_ERROR, icon='⚠')
    
    elif pdf_file is None:
        st.warning(config.FILE_UPLOAD_ERROR, icon='⚠')
        
    elif generate_readme:
        openai.api_key = openai_api_key
        openai_client = OpenAI(api_key=openai_api_key)
        start = time.time()
        text = "Please add a README page to the dashboard."
        
        # Extract report.json and model.bim from the uploaded PBIP folder
        report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path = extract_report_and_model(zip_file)
        report_images = convert_pdf_to_images(pdf_file)
        
        # Initialize the service coordinator
        coordinator = FunctionCoordinator(function_descriptions.FUNCTION_DESCRIPTIONS)
        
        # Process the request
        modified_json, file_content, message = coordinator.process_request(
            text,
            report_json_content,
            model_bim_content,
            report_images,
            selected_language,
            selected_model,
            openai_client,
            requested_function="add_read_me",
        )
        print(f"README generation took {time.time() - start:.2f}s")
        
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
    elif generate_description:

        openai.api_key = openai_api_key
        openai_client = OpenAI(api_key=openai_api_key)
        start = time.time()
        text = "Provide full documentation of the dashboard for confluence."
        
        report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path = extract_report_and_model(zip_file)
        
        # Initialize the service coordinator
        coordinator = FunctionCoordinator(function_descriptions.FUNCTION_DESCRIPTIONS)
        
        # Process the request
        print(openai_client)
        report_images = []
        modified_json, file_content, message = coordinator.process_request(
            text,
            report_json_content,
            model_bim_content,
            report_images,
            selected_language,
            selected_model,
            openai_client,
            requested_function="summary_in_target_platform",
        )
        print(f"Documentation generation took {time.time() - start:.2f}s")
        
        # Display the message
        if "error" in message.lower():
            st.error(message)
        else:
            st.success(message)
        
        # Handle the results
        if file_content:
            # Create a downloadable link for the documentation file
            st.download_button(
                label=f'Download {config.DOCUMENTATION_FILENAME}',
                data=file_content,
                file_name=config.DOCUMENTATION_FILENAME,
                mime='text/plain'
            )
            
    #else:
    #    st.warning("Sélectionnez au moins une action.", icon="⚠")
    #    st.stop()

            

if __name__ == "__main__":
    main()
