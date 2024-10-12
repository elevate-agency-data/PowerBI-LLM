import streamlit as st
import openai
import json
import zipfile
import io
import os

st.title('🦜🔗 PBIP Folder Modifier')

# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key', type="password")

# Initialize a variable to store the modified JSON content
modified_json = None

# Function to handle the PBIP folder and extract report.json
def extract_report_json(zip_file):
    # Get the base name of the uploaded zip file, excluding the extension
    inner_folder_name = os.path.splitext(zip_file.name)[0]  # Get the base name without .zip
    # Extract the zip file
    extract_path = '/mnt/data/pbip_extracted/'
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    inner_folder_path = os.path.join(extract_path, inner_folder_name)

    # Print the contents of the inner folder
    inner_folder_contents = os.listdir(inner_folder_path)

    # Look for the folder that ends with '.Report'
    report_folder_path = None
    for folder in inner_folder_contents:
        if folder.endswith('.Report') and os.path.isdir(os.path.join(inner_folder_path, folder)):
            report_folder_path = os.path.join(inner_folder_path, folder)
            break

    report_json_path = os.path.join(report_folder_path, 'report.json')

    # Read and return the content of the report.json file
    with open(report_json_path, 'r', encoding='utf-8') as file:
        report_json_content = file.read()
    
    return report_json_content, inner_folder_path, report_json_path

# Function to modify the report.json file based on user input
def modify_report_json(input_text, report_json_content):
    # Set up OpenAI API key
    openai.api_key = openai_api_key
    
    # Create a prompt for the model
    messages = [
        {"role": "system", "content": "You are an assistant that helps modify PowerBI JSON files."},
        {"role": "user", "content": f"Here is a JSON file related to a PowerBI report:\n{report_json_content}\n\nI am going to provide you with a user request that includes some changes they would like to make to the PowerBI report. You need to make the corresponding modifications to the JSON file and send me the modified JSON file. You should only make modifications based on the user request and not invent any other requests.\n\nHere is the user request: {input_text}"}
    ]
    
    # Call the chat-based fine-tuned model
    response = openai.ChatCompletion.create(
        model="ft:gpt-3.5-turbo-0125:personal::AG3HbjhD",  # Fine-tuned model
        messages=messages,
        max_tokens=1500  # Adjust token limit if needed
    )
    
    modified_json_content = response['choices'][0]['message']['content']
    
    try:
        # Try to parse the response as JSON
        modified_json_data = json.loads(modified_json_content)
    except json.JSONDecodeError:
        st.error("The modified content is not valid JSON. Please refine the request or check the output.")
        return None
    
    # Return the modified JSON content
    return json.dumps(modified_json_data, indent=2)

# Function to write the modified JSON back to the original folder structure and re-zip the file
def write_modified_zip(modified_json, report_json_path, folder_path):
    # Write the modified JSON content back to report.json
    with open(report_json_path, 'w', encoding='utf-8') as file:
        file.write(modified_json)

    # Create a new zip file with the modified content
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        # Walk the folder and add everything back to the zip
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                new_zip.write(file_path, arcname=arcname)

    zip_buffer.seek(0)  # Move to the beginning of the file for download
    return zip_buffer

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
        # Extract report.json from the uploaded PBIP folder
        report_json_content, folder_path, report_json_path = extract_report_json(zip_file)
        
        if report_json_content:
            # Call the function to modify the JSON file based on user input
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