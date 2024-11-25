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

def summarize_dashboard_by_page(extracted_json_by_page):
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
                "e. Scenarios for Interpretation\n"
                "	• Provide examples to guide users on how to interpret the dashboard.\n"
                f"Here is the JSON content:\n{extracted_json_of_the_page}\n\n"
                "If certain information cannot be found in the provided JSON file, you may ignore it and continue with the rest. Do not invent any information."
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

def summarize_dashboard(target_platform, json_content):
    try:
        # Combine the user prompt with the JSON content
        combined_prompt = (
            f"Make documentation based on the content of the JSON file for {target_platform}. "
            "In the documentation, you should include:\n"
            '"Overview" Related Info\n'
            "- Dashboard Name\n"
            "- Dashboard Purpose: Business objective/problem the dashboard addresses\n"
            "- Primary Users: List the roles/audience for the dashboard (e.g., Sales Team, Media Team, Top Management)\n"
            "- Update Frequency: Daily, Weekly, etc.\n"
            "- Key Features: Main features of the dashboard (e.g., online & offline data to monitor media investment)\n\n"
            "Front-end Documentation / Visualizations\n"
            "a. Page Overview\n"
            "- List all pages in the dashboard and their purpose (e.g., 'Sales Overview' – Provides a summary of total revenue, sales margin, and top-performing regions)\n\n"
            "b. KPIs and Metrics\n"
            "- KPI Definitions: Name of the KPI, DAX formula (ideally a phrase describing the calculation), data source, and threshold if needed "
            "(e.g., if <100K, colored red)\n\n"
            "c. Visualizations\n"
            "- Charts, Graphs, Cards: Name, what it represents, and how to interpret it (e.g., 'Sales by Region' – A bar chart showing total sales per region. "
            "Hovering over a bar reveals the exact revenue value.)\n\n"
            "d. Filtering\n"
            "- Explain slicers, filters, and date pickers (e.g., Use the date picker to select a custom period)\n\n"
            "e. Scenarios for Interpretation\n"
            "- Provide examples to guide users on how to interpret the dashboard.\n\n"
            "f. Admin & Last Update\n"
            "- Contact email and last update date\n\n"
            "Backend Documentation\n"
            "a. Data Sources: List all data sources by table or information category (e.g., Sales data comes from Snowflake 'SalesDB' database; special marketing events from Excel files uploaded to SharePoint + Scheduled refresh times\n"
            "b. Data Model: Table Descriptions: Name of the table, purpose of the table (e.g., Table 'Sales_Fact' stores transaction-level data with granularity at the order level)\n"
            "c. Data Volumes: Size of each table and record count\n"
            "d. Quality Measures: Sum checks, etc.\n\n"
            f"Here is the JSON content:\n{json_content}"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
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
