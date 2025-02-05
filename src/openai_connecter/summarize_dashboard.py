"""
This module provides a set of functions to interact with OpenAI's API for summarizing a Power BI dashboard.
"""
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI()

def global_summary_dashboard(extracted_json_by_page, target_platform="Confluence", language="English"):
    """Generate a global summary of the dashboard"""
    try:
        prompt = (
            f"Create a concise and professional summary of a Power BI report in approximately 150 words in {language} based on the provided Dashboard Information:\n\n"
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

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that specializes in summarizing Power BI dashboards. Your task is to create a concise yet comprehensive summary of the dashboard based on the information provided for its different pages. Ensure the summary is accurate, well-structured, and tailored for the specified target platform."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"

def summarize_dashboard_by_page(extracted_json_by_page, target_platform="Confluence", language="English"):
    """Generate a summary for each page in the dashboard"""
    result_summary = ""
    page_overview_dict = {}  # Dictionary to store Page Overview content by page_name

    for page_data in extracted_json_by_page:
        page_name = page_data['displayName']
        extracted_json_of_the_page = page_data['extracted_data']

        try:
            prompt = (
                "I will provide you with a JSON file, and you need to retrieve the following information from the file:\n\n"
                "### Instructions\n"
                "1. **Page Overview**\n"
                "   - Write a overall purpose of the page.\n\n"
                "2. **Visualizations**\n"
                "   - List all the visuals on the page, what they represent, and how users can interpret them.\n\n"
                "3. **Filtering**\n"
                "   - Explain slicers, filters, or date pickers used on the page.\n\n"
                "4. **Scenarios for Interpretation**\n"
                "   - Provide examples to guide users on how to interpret the dashboard effectively.\n\n"
                f"### Provided JSON\n{extracted_json_of_the_page}\n\n"
                "### Important Notes\n"
                "- If certain information is not available in the JSON file, omit it without inventing data.\n"
                f"- Ensure the retrieved information is structured in {language} and formatted appropriately for {target_platform}.\n\n"
                "### Expected Output Format\n"
                "- Use headings and bullet points to organize the output.\n"
                "- Ensure clear and concise explanations for each section."
            )

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that extracts key information from Power BI pbip reports' JSON files."},
                    {"role": "user", "content": prompt}
                ]
            )

            summary = response.choices[0].message.content
            result_summary += f"### {page_name}\n{summary}\n\n"

            structured_prompt = (
                "Extract only the **Page Overview** and **Visualizations** from the following content and return it in plain text format:\n\n"
                "- For the content under the Visualizations section, ignore slicers and focus only on visuals such as charts and tables that provide meaningful insights into the dashboard.\n\n"
                f"{summary}\n\n"
            )

            overview_response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a content extractor specializing in summarizing key sections."},
                    {"role": "user", "content": structured_prompt}
                ]
            )
            page_overview = overview_response.choices[0].message.content.strip()
            page_overview_dict[page_name] = page_overview

        except Exception as e:
            return {"error": f"An error occurred: {str(e)}"}

    return result_summary, page_overview_dict

def create_measures_overview_table(measures_content, target_platform="Confluence"):
    """Create a table overview of measures"""
    try:
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

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that specializes in summarizing the measures in Power BI dashboards."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def create_measures_by_column_table(measures_content, target_platform="Confluence"):
    """Create a table showing measures grouped by column"""
    try:
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
            "- Each row in the table should correspond to one column from the 'Used Columns' of a measure. If a measure uses multiple columns, create separate rows for each column, repeating the measure's name and source table.\n"
            "- For the output, **only return the table** without any additional text.\n"
            f"- Ensure the table is formatted appropriately for {target_platform}.\n\n"
            "### MEASURES\n"
            f"{measures_content}\n\n"
            "### Output\n"
            "Generate the table in the format shown above."
        )

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that specializes in summarizing the measures in Power BI dashboards."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"An error occurred: {str(e)}"

