from streamlit_app import *
import streamlit as st
import openai
import json

# Function to modify the report.json file based on user input
def modify_report_json(input_text, report_json_content):
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
    modified_json_content
    try:
        # Try to parse the response as JSON
        modified_json_data = json.loads(modified_json_content)
        modified_json_data
    except json.JSONDecodeError:
        st.error("The modified content is not valid JSON. Please refine the request or check the output.")
        return None
    
    # Return the modified JSON content
    return json.dumps(modified_json_data, indent=2)

def summarize_dashboard(target_platform, json_content):
    try:
        # Combine the user prompt with the JSON content
        combined_prompt = (
            f"Make documentation based on the content of the JSON file for {target_platform}. "
            "In the documentation, you should include:\n"
            "1) The general purpose of the dashboard\n"
            "2) Data sources for different tables\n"
            "3) Calculation formulas for DAX measures and calculated columns\n"
            "4) Data model structure, including relationships between tables\n\n"
            f"Here is the JSON content:\n{json_content}"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[
                {"role": "system", "content": "You are an assistant that summarizes JSON files of powerBI reports to different documentation platforms."},
                {"role": "user", "content": combined_prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
