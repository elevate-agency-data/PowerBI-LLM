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

def global_summary_dashboard(extracted_json_by_page, target_platform):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "Create a concise and professional summary of a Power BI report in approximately 150 words based on the provided Dashboard Information:\n\n"
            "**Dashboard Information:**\n"
            f"{extracted_json_by_page}\n\n"
            "### Instructions:\n"
            "- Write a clear and comprehensive summary that captures the **dashboard's purpose**.\n"
            "- Ensure the summary accurately reflects the content provided and **do not invent anything**.\n"
            f"- The summary must be appropriately styled for **{target_platform}**.\n"
            "- You should only return a single paragraph of the summary without adding anything else.\n\n"
            "### Example Output:\n"
            "\"This dashboard provides a comprehensive overview of key performance indicators, highlighting recent trends, achievements, and areas requiring attention. "
            "It serves as a powerful tool to monitor progress, identify growth opportunities, and support strategic decision-making across critical business domains.\"\n"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are an assistant that specializes in summarizing Power BI dashboards. Your task is to create a concise yet comprehensive summary of the dashboard based on the information provided for its different pages. Ensure the summary is accurate, well-structured, and tailored for the specified target platform."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"

def summarize_dashboard_by_page(extracted_json_by_page, target_platform):
    result_summary = ""
    for i in range(len(extracted_json_by_page)):
        page_name = extracted_json_by_page[i]['displayName']
        extracted_json_of_the_page = extracted_json_by_page[i]['extracted_data']

        try:
            prompt = (
                "I will provide you with a JSON file, and you need to retrieve the following information from the file:\n\n"
                "### Instructions\n"
                "1. **Page Overview**\n"
                "   - Write a overall purpose of the page.\n"
                "   - Example:\n"
                '     - "This page provides a summary of total revenue, sales margin, and top-performing regions.\n\n'
                "2. **Visualizations**\n"
                "   - List all the visuals on the page, what they represent, and how users can interpret them.\n"
                "   - Example:\n"
                '     - "Sales by Region": A bar chart showing total sales per region. Hovering over a bar reveals the exact revenue value.\n\n'
                "3. **Filtering**\n"
                "   - Explain slicers, filters, or date pickers used on the page.\n"
                "   - Example:\n"
                '     - Date Picker: Use the date picker to select a custom period.\n\n'
                "4. **Scenarios for Interpretation**\n"
                "   - Provide examples to guide users on how to interpret the dashboard effectively.\n"
                '     - Example:\n'
                '       - "If you want to understand regional performance, use the slicer to select a region and observe the sales trends in the line chart."\n\n'
                "### Provided JSON\n"
                f"{extracted_json_of_the_page}\n\n"
                "### Important Notes\n"
                "- If certain information is not available in the JSON file, omit it without inventing data.\n"
                f"- Ensure the retrieved information is structured and formatted appropriately for {target_platform}.\n\n"
                "### Expected Output Format\n"
                "- Use headings and bullet points to organize the output.\n"
                "- Ensure clear and concise explanations for each section."
            )

            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts key information from Power BI pbip reports' JSON files."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract and append the summary to the result string
            summary = response['choices'][0]['message']['content']
            result_summary += f"### {page_name}\n{summary}\n\n"

        except Exception as e:
            return f"An error occurred: {str(e)}"

    return result_summary

def summarize_table_source(table_content, target_platform):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "Extract and list all table names and their corresponding sources from the provided TABLE Content.\n"
            "- The table names are located in the 'name' key of each object under the 'table_partitions' key.\n"
            "- For each table, extract its 'source' from the 'source' key of the same object.\n"
            "- If the 'source' key includes parameters (e.g., 'server_id', 'database_id', 'storage_id'), match each parameter name with the 'name' key in the 'expressions' section of the TABLE Content to identify the parameter's value.\n"
            "- For parameters with dynamic or concatenated values, describe clearly how these values are combined.\n"
            "- Ensure that all tables listed in the TABLE Content are included in the summary, with none omitted.\n"
            "- Do not add any irrelevant information such as introductions or summaries.\n"
            f"- Format the summary appropriately for {target_platform}, ensuring it is clear, concise, and well-organized.\n\n"
            "### TABLE Content\n"
            f"{table_content}\n\n"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that specializes in extracting powerBI related information from json file."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def create_measures_overview_table(measures_content, target_platform):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "**Create a table** with the following columns:\n"
            "- 'Name of the Measure'\n"
            "- 'Measure Formula'\n"
            "- 'Description'\n\n"
            "### Instructions\n"
            "1. The formulas for each measure can be found under the 'expression' key in the MEASURES content.\n"
            "2. For the 'Measure Formula' column, extract the exact formula from the 'expression' key without modifying or omitting anything.\n"
            "3. Ensure all measures presented in the MEASURES content are included in the 'Name of the Measure' column.\n"
            "4. Based on your understanding of the measure, write a short explanation of the measure's purpose in the 'Description' column\n"
            "5. For the output, **only return the table** without any additional text.\n"
            f"6. Ensure the table is formatted appropriately for {target_platform}\n\n"
            "### Example\n"
            "If a measure is calculated as follows:\n"
            "`Whitelisted Clients = CALCULATE(COUNTROWS('dim_client'), dim_client[is_whitelisted] = \"yes\")`\n\n"
            "The output of the table should look like this:\n\n"
            "| Name of the Measure   | Measure Formula                                                | Description                               |\n"
            "|-----------------------|-------------------------------------------------------------|-------------------------------------------|\n"
            "| Whitelisted Clients   | CALCULATE(COUNTROWS('dim_client'), dim_client[is_whitelisted] = \"yes\") | The measure calculates the total number of whitelisted clients |\n\n"
            "### MEASURES\n"
            f"{measures_content}\n\n"
            "### Output\n"
            "Generate the table in the format shown above."
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are an assistant that specializes in summarizing the measures in Power BI dashboards."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def create_measures_by_column_table(measures_content, target_platform):
    try:
        # Combine the user prompt with the JSON content
        prompt = (
            "**Create a table** with three columns: 'Name of the Measure', 'Source Table', and 'Used Columns', based on the measures provided below.\n\n"
            "### Example\n"
            "If a measure is calculated as follows:\n"
            "`Whitelisted Clients = CALCULATE(COUNTROWS('dim_client'), dim_client[is_whitelisted] = \"yes\")`\n\n"
            "The output of the second table should look like this:\n\n"
            "| Name of the Measure   | Source Table | Used Columns       |\n"
            "|-----------------------|--------------|--------------------|\n"
            "| Whitelisted Clients   | dim_client   | pky_client         |\n"
            "| Whitelisted Clients   | dim_client   | is_whitelisted     |\n\n"
            "### Instructions\n"
            "- Each row in the table should correspond to one column from the 'Used Columns' of a measure.\n"
            "- If a measure uses multiple columns, create separate rows for each column, repeating the measure's name and source table.\n"
            "- For the output, **only return the table** without any additional text.\n"
            f"- Ensure the table is formatted appropriately for {target_platform}.\n\n"
            "### MEASURES\n"
            f"{measures_content}\n\n"
            "### Output\n"
            "Generate the table in the format shown above."
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = [
                {"role": "system", "content": "You are an assistant that specializes in summarizing the measures in Power BI dashboards."},
                {"role": "user", "content": prompt}
            ]
        )

        # Extract and return the summary
        summary = response['choices'][0]['message']['content']
        return summary

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
