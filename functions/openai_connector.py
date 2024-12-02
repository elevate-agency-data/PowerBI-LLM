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

def summarize_dashboard_by_page(extracted_json_by_page, target_platform):
    dashboard_summary_by_page = {}
    for i in range(len(extracted_json_by_page)):
        page_name = extracted_json_by_page[i]['displayName']
        extracted_json_of_the_page = extracted_json_by_page[i]['extracted_data']

        try:
            prompt = (
                "I will provide you a JSON file and you need to retrieve the below information from the provided file:\n"
                "a. Page Overview\n"
                "   • List all pages in the dashboard and their purpose.\n"
                "     Example:\n"
                '     o "Sales Overview": Provides a summary of total revenue, sales margin, and top-performing regions.\n'
                "b. Visualizations\n"
                "   • Charts, Graphs, Cards:\n"
                "     List the visualizations, what they represent, and how to interpret them.\n"
                "     Example:\n"
                '     o "Sales by Region": A bar chart showing total sales per region. Hovering over a bar reveals the exact revenue value.\n'
                "c. Filtering\n"
                "   • Explain slicers, filters, date pickers.\n"
                "     Example:\n"
                '     o Date Picker: Use the date picker to select a custom period.\n'
                "d. Scenarios for Interpretation\n"
                "	• Provide examples to guide users on how to interpret the dashboard.\n"
                f"Here is the JSON content:\n{extracted_json_of_the_page}\n\n"
                "If certain information cannot be found in the provided JSON file, you may ignore it and continue with the rest. Do not invent any information.\n"
                f"Ensure the retrived information is formatted appropriately for {target_platform}."
            )


            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model = "gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that extract the key information from powerBI pbip reports' JSON files."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract and return the summary
            summary = response['choices'][0]['message']['content']
            dashboard_summary_by_page[page_name] = summary
            
        except Exception as e:
            return f"An error occurred: {str(e)}"

    return dashboard_summary_by_page

def summarize_dataset(extracted_dataset, target_platform):
    tables = extracted_dataset['tables']
    measures = extracted_dataset['measures']

    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "1. List all table names in the dataset along with their sources based on the TABLE Content.\n"
            "2. Identify all measures in the MEASURE Content and list their formulas in code format.\n"
            "It is critical that no information is omitted.\n"
            "Provide a clear explanation of the KPIs, ensuring that every measure and its formula present in the MEASURE Content is included.\n"
            f"Ensure the summary is formatted appropriately for {target_platform}.\n"
            "### TABLE Content\n"
            f"{tables}\n\n"
            "### MEASURE Content\n"
            f"{measures}\n"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that extract the key information from powerBI pbip reports' JSON files."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"

# def summarize_in_target_platform(summary_dashboard, summary_dataset, target_platform):
#     try:
#         # Combine the user prompt with the JSON content
#         combined_prompt = (
#             f"Transform the content below into the format of {target_platform}."
#             "Ensure that all information from both the Dashboard and Dataset sections is included comprehensively, without omitting any details.\n\n"
#             "### Dashboard Information\n"
#             f"{summary_dashboard}\n\n"
#             "### Dataset Information\n"
#             f"{summary_dataset}\n"
#         )

#         # Call OpenAI API
#         response = openai.ChatCompletion.create(
#             # Use the latest model for better comprehension
#             model="gpt-4",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": (
#                        "You are an assistant specializing in combiningng documents and put it to the target platform."
#                     ),
#                 },
#                 {"role": "user", "content": combined_prompt},
#             ]
#         )

#         # Extract and return the summary
#         summary = response['choices'][0]['message']['content']
#         return summary

#     except Exception as e:
#         return f"An error occurred: {str(e)}"
    
def summarize_dashboard(text, target_platform):
    try:
        # Combine the user prompt with the JSON content
        combined_prompt = (
            f"Write a summary of a Power BI dashboard based on the provided content organized by page. "
            f"Ensure the summary is formatted appropriately for {target_platform}.\n\n"
            f"### Content Summary by Page:\n"
            f"{summary_dashboard}"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                },
                {"role": "user", "content": combined_prompt},
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
