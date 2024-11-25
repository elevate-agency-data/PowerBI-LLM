import json
import openai

template_path = "templates/read_me_template.json"

def prepare_arguments(kpis, function_descriptions):
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
    return add_read_me_output.choices[0].message["function_call"]["arguments"]

def add_read_me(dashboard_summary, pages, template_path=template_path):
    """
    Adds a read-me page to a Power BI report JSON template.

    Parameters:
    - dashboard_summary (str): Summary description of the entire dashboard.
    - pages (list): List of dictionaries containing page details, each with:
        - "page_name" (str): Name of the page
        - "page_summary" (str): Summary of the page
        - "visuals" (list): List of dictionaries for each KPI with:
            - "kpi_name" (str): KPI name
            - "kpi_definition" (str): KPI definition
    - template_path (str): Path to the Power BI report template JSON.

    Returns:
    - dict: Updated JSON structure with the read-me content filled in.
    """
    # Load the template
    with open(template_path, "r") as f:
        report_json = json.load(f)

    # Update the dashboard summary
    for section in report_json["sections"]:
        for visual in section["visualContainers"]:
            config = json.loads(visual["config"])
            text_runs = config.get("singleVisual", {}).get("objects", {}).get("general", [{}])[0].get("properties", {}).get("paragraphs", [])

            # Replace placeholders for dashboard summary
            for paragraph in text_runs:
                for text_run in paragraph.get("textRuns", []):
                    if text_run.get("value") == "DASHBOARD SUMMARY":
                        text_run["value"] = dashboard_summary

                    # Loop through pages to replace page-specific placeholders
                    for page in pages:
                        page_name = page["page_name"]
                        page_summary = page["page_summary"]
                        visuals = page["visuals"]

                        # Replace "PAGE NAME" placeholder exactly with the page name
                        if "PAGE NAME" in text_run.get("value", ""):
                            text_run["value"] = text_run["value"].replace("PAGE NAME", page_name)
                        elif "PAGE SUMMARY" in text_run.get("value", ""):
                            text_run["value"] = f": {page_summary}"

                        # Create new textRuns entries for each KPI
                        kpi_text_runs = []
                        for visual_info in visuals:
                            kpi_text_runs.append({
                                "value": f"{visual_info['kpi_name']}: ",
                                "textStyle": {"fontSize": "12pt", "fontWeight": "bold"}
                            })
                            kpi_text_runs.append({
                                "value": f"{visual_info['kpi_definition']}\n",
                                "textStyle": {"fontSize": "12pt"}
                            })

                        # Insert KPI definitions into the paragraph if the KPI placeholder is found
                        if any("KPI NAME" in tr.get("value", "") for tr in paragraph["textRuns"]):
                            paragraph["textRuns"] = kpi_text_runs

                # Remove any remaining KPI placeholder if present at the bottom
                paragraph["textRuns"] = [tr for tr in paragraph["textRuns"] if tr.get("value") != "KPI DEFINATION"]

            # Update the visual config with modified text_runs
            visual["config"] = json.dumps(config)

    return report_json
