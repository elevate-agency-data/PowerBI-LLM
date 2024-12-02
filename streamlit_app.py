
from functions.openai_connector import *
from functions.integrate_json_back import *
from functions.main_function import *
from functions.extract_original_json import *
from functions.add_read_me import *
from functions.upload_powerbi_files import *
import streamlit as st
import openai
import json
# from dotenv import find_dotenv, load_dotenv
import zipfile
import io
import os

# load_dotenv(find_dotenv())

st.title('🦜🔗 PBIP Folder Modifier')
# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key', type="password")
openai.api_key = openai_api_key

# Initialize a variable to store the modified JSON content
modified_json = None
# Form for user input and file upload
with st.form('pbip_form'):
    text = st.text_area('Enter your request:', 'I want to add a filter to each page of the PowerBI report.')
    zip_file = st.file_uploader('Upload the PBIP folder (as a .zip file)', type=['zip'])
    submitted = st.form_submit_button('Submit')
# Process the form submission
if submitted:
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    elif zip_file is None:
        st.warning('Please upload the PBIP folder as a .zip file!', icon='⚠')
    else:
        # Extract report.json and model.bim from the uploaded PBIP folder
        report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path = extract_report_and_model(zip_file)
        output = generate_completion(text)
        print(output.get("function_call", {}).get("name"))
        if output.get("function_call", {}).get("name") == "add_read_me":
            # If "add_read_me" is called, extract the relevant KPI part
            kpis = extract_relevant_elements_dashboard_summary(report_json_content)
            
            # Run the function call with the extracted KPI data
            add_read_me_output = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": f"{kpis}"
                    }
                ],
                functions=function_descriptions,
                function_call={"name": "add_read_me", "arguments": json.dumps({"kpis": kpis})}
            )
            # Extract the arguments string and parse it into a dictionary
            arguments = prepare_arguments(kpis, function_descriptions)
            arguments_dict = json.loads(arguments)
            updated_report = add_read_me(**arguments_dict)
            report_json_content['sections'].insert(0, updated_report["sections"][0])
            modified_json = json.dumps(report_json_content, indent=4)
        elif output.get("function_call", {}).get("name") == "summary_in_confluence":
            extracted_report = extract_dashboard_by_page(report_json_content)
            extracted_dataset = extract_relevant_parts_dataset(model_bim_content)
            target_platform = "confluence"
            summary_dashboard = summarize_dashboard_by_page(extracted_report, target_platform)
            summary_dataset = summarize_dataset(extracted_dataset, target_platform)
            # dashboard_summary = summarize_dashboard(summary_dashboard, target_platform)
            # st.write(dashboard_summary)
            st.write(summary_dashboard)
            st.write(summary_dataset)
            
        else:
            # Call the function to modify the JSON file based on user input
            report_json_content = json.dumps(report_json_content, indent=4) # Convert the Python dictionary back to a JSON string
            modified_json = modify_report_json(text, report_json_content)
        if modified_json:
            # Write back the modified report.json and create the zip file
            modified_zip = write_modified_zip(modified_json, report_json_path, folder_path)
            st.success('PBIP folder modified successfully!')
            
            # Provide a download button for the modified zip file
            st.download_button(
                label='Download Modified PBIP Folder',
                data=modified_zip,
                file_name='modified_pbip.zip',
                mime='application/zip'
            )
