import streamlit as st
from langchain.llms import OpenAI
import json
import io

st.title('🦜🔗 JSON File Modifier')

# Sidebar for API key input
openai_api_key = st.sidebar.text_input('OpenAI API Key')

# Initialize a variable to store the modified JSON content
modified_json = None

# Function to generate a response and modify the .json file
def modify_json(input_text, json_file):

    # Initialize the OpenAI model
    llm = OpenAI(
        temperature=0.1, 
        openai_api_key=openai_api_key
)
    # Read the content of the uploaded .json file
    json_content = json_file.read().decode('utf-8')
    # Create a prompt for the model that includes the user input and the JSON content
    prompt = f"Here is a JSON file related to a PowerBI report:\n{json_content}\n\nI am going to provide you with a user request that includes some changes they would like to make to the Power BI report. You need to make the corresponding modifications to the JSON file and send me the modified JSON file. You should only make modifications based on the user request and not invent any other requests.\n\nHere is the user request: {input_text}"

    # Get the modified JSON content from the model
    modified_json_content = llm(prompt)

    # Convert the modified content back to a bytes object
    modified_json_bytes = io.BytesIO(modified_json_content.encode('utf-8'))
    
    # return modified_json_bytes
    return modified_json_bytes

# Form for user input and file upload
with st.form('json_form'):
    text = st.text_area('Enter your request:', 'I want to add a filter to each page of the PowerBI report.')
    json_file = st.file_uploader('Upload a .json file', type=['json'])
    submitted = st.form_submit_button('Submit')

# Process the form submission
if submitted:
    if not openai_api_key.startswith('sk-'):
        st.warning('Please enter your OpenAI API key!', icon='⚠')
    elif json_file is None:
        st.warning('Please upload a .json file!', icon='⚠')
    else:
        # Call the function to modify the JSON file based on user input
        modified_json = modify_json(text, json_file)
        st.success('File modified successfully!')
        
        # Display the original JSON content
        st.subheader("Modified JSON File Content")
        st.write(modified_json)

# Display the download button outside the form
if modified_json:
    st.download_button(
        label='Download Modified JSON File',
        data=modified_json,
        file_name='modified_file.json',
        mime='application/json'
    )
