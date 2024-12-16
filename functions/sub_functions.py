import json
import openai

def prepare_arguments_add_read_me(kpis, function_descriptions):
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

def prepare_arguments_summary_in_target_platform(user_prompt, function_descriptions):
    # Run the function call with the extracted KPI data
    add_read_me_output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"{user_prompt}"
            }
        ],
        functions=function_descriptions,
        function_call={"name": "summary_in_target_platform", "arguments": json.dumps({"kpis": kpis})}
    )
    return add_read_me_output.choices[0].message["function_call"]["arguments"]

def add_read_me(dashboard_summary, pages):
    # Define the template directly in the code
    template = {
        "config": "{\"version\":\"5.37\",\"themeCollection\":{\"baseTheme\":{\"name\":\"CY22SU03\",\"version\":\"5.31\",\"type\":2}},\"activeSectionIndex\":0,\"defaultDrillFilterOtherVisuals\":true,\"filterSortOrder\":3,\"linguisticSchemaSyncVersion\":2,\"settings\":{\"useNewFilterPaneExperience\":true,\"allowChangeFilterTypes\":true,\"useStylableVisualContainerHeader\":true,\"exportDataMode\":1,\"allowDataPointLassoSelect\":false,\"filterPaneHiddenInEditMode\":false,\"pauseQueries\":false,\"useEnhancedTooltips\":true},\"objects\":{\"section\":[{\"properties\":{\"verticalAlignment\":{\"expr\":{\"Literal\":{\"Value\":\"'Top'\"}}}}}],\"outspacePane\":[{\"properties\":{\"expanded\":{\"expr\":{\"Literal\":{\"Value\":\"false\"}}},\"visible\":{\"expr\":{\"Literal\":{\"Value\":\"false\"}}}}}]}}",
        "filters": "[]",
        "layoutOptimization": 0,
        "publicCustomVisuals": [],
        "resourcePackages": [
            {
                "resourcePackage": {
                    "disabled": False,
                    "items": [
                        {
                            "name": "CY22SU03",
                            "path": "BaseThemes/CY22SU03.json",
                            "type": 202
                        }
                    ],
                    "name": "SharedResources",
                    "type": 2
                }
            }
        ],
        "sections": [
            {
                "config": "{}",
                "displayName": "Glossary",
                "displayOption": 1,
                "filters": "[]",
                "height": 720.00,
                "name": "88cbaa1e34d414c234a5",
                "visualContainers": [
                    {
                        "config": "{\"name\":\"677ff640e2128e7c8715\",\"layouts\":[{\"id\":0,\"position\":{\"x\":325.4878295609724,\"y\":0,\"z\":0,\"width\":654.4881177143293,\"height\":63.22425466292269}}],\"singleVisual\":{\"visualType\":\"textbox\",\"drillFilterOtherVisuals\":true,\"objects\":{\"general\":[{\"properties\":{\"paragraphs\":[{\"textRuns\":[{\"value\":\" DASHBOARD NAME\",\"textStyle\":{\"fontWeight\":\"bold\",\"fontSize\":\"20pt\"}}],\"horizontalTextAlignment\":\"center\"},{\"textRuns\":[{\"value\":\"\"}]}]}}]}}}",
                        "filters": "[]",
                        "height": 63.22,
                        "width": 654.49,
                        "x": 325.49,
                        "y": 0.00,
                        "z": 0.00
                    }
                ],
                "width": 1280.00
            }
        ]
    }

    # Initialize the y-position for the first textbox and spacing between textboxes
    y_position = 50
    horizontal_distince_between_textbox = 40

    # Dashboard Summary Textbox Configuration
    dashboard_summary_height = 80
    dashboard_summary_width = 1200
    dashboard_summary_config = {
        "config": json.dumps({
            "name": "dashboardSummaryBox",
            "layouts": [{"id": 0, "position": {"x": 10, "y": y_position, "z": 0, "width": dashboard_summary_width, "height": dashboard_summary_height}}],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": [{
                                "textRuns": [{
                                    "value": dashboard_summary,
                                    "textStyle": {"fontSize": "14pt"}
                                }]
                            }]
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": dashboard_summary_height,
        "width": dashboard_summary_width,
        "x": 10,
        "y": y_position,
        "z": 0
    }
    template["sections"][0]["visualContainers"].append(dashboard_summary_config)

    # Update y_position for the next textbox
    y_position += dashboard_summary_height + horizontal_distince_between_textbox

    # Create text for page overviews with reduced spacing
    page_summary_height = 50
    paragraphs = [{"textRuns": [{"value": "Page Overview", "textStyle": {"fontWeight": "bold", "fontSize": "14pt"}}]}]

    for page in pages:
        paragraphs.append({
            "textRuns": [
                {
                    "value": f"{page['page_name']}: ",  # Page name part
                    "textStyle": {
                        "fontSize": "12pt",
                        "fontWeight": "bold"  # Make it bold
                    }
                },
                {
                    "value": page['page_summary'],  # Page summary part
                    "textStyle": {
                        "fontSize": "12pt"  # Keep regular font for the summary
                    }
                }
            ]
        })
        page_summary_height += 20

    # Textbox for all page summaries
    page_summaries_config = {
        "config": json.dumps({
            "name": "pageSummariesBox",
            "layouts": [{"id": 0, "position": {"x": 10, "y": y_position, "z": 0, "width": 1200, "height": page_summary_height}}],
            "singleVisual": {
                "visualType": "textbox",
                "drillFilterOtherVisuals": True,
                "objects": {
                    "general": [{
                        "properties": {
                            "paragraphs": paragraphs
                        }
                    }]
                }
            }
        }),
        "filters": "[]",
        "height": page_summary_height,
        "width": 1200,
        "x": 10,
        "y": y_position,
        "z": 0
    }
    template["sections"][0]["visualContainers"].append(page_summaries_config)

    # Update y_position for the next textbox
    y_position += page_summary_height + horizontal_distince_between_textbox

    # KPIs related text boxes
    x_position = 10
    max_width = 0

    for i, page in enumerate(pages):
        if i != 0 and i % 2 == 0:
            x_position = 10
            y_position += max_width + 30
            max_width = 0

        paragraphs = [{"textRuns": [{"value": page['page_name'], "textStyle": {"fontWeight": "bold", "fontSize": "14pt"}}]}]
        for visual in page['visuals']:
            paragraphs.append({
                "textRuns": [
                    {
                        "value": f"{visual['kpi_name']}: ",  # KPI name part
                        "textStyle": {
                            "fontSize": "12pt",
                            "fontWeight": "bold"  # Make the KPI name bold
                        }
                    },
                    {
                        "value": visual['kpi_definition'],  # KPI definition part
                        "textStyle": {
                            "fontSize": "12pt"  # Regular font for the KPI definition
                        }
                    }
                ]
            })

        textbox_height = 50 + len(page['visuals']) * 30
        max_width = max(max_width, textbox_height)

        kpi_textbox_config = {
            "config": json.dumps({
                "name": f"{page['page_name'].replace(' ', '')}KPIs",
                "layouts": [{"id": 0, "position": {"x": x_position, "y": y_position, "z": 0, "width": 600, "height": textbox_height}}],
                "singleVisual": {
                    "visualType": "textbox",
                    "drillFilterOtherVisuals": True,
                    "objects": {
                        "general": [{
                            "properties": {
                                "paragraphs": paragraphs
                            }
                        }]
                    }
                }
            }),
            "filters": "[]",
            "height": textbox_height,
            "width": 600,
            "x": x_position,
            "y": y_position,
            "z": 0
        }
        template["sections"][0]["visualContainers"].append(kpi_textbox_config)
        x_position += 650

    page_height = y_position + textbox_height + 50 
    # Update the page height to reflect the total height
    template["sections"][0]["height"] = page_height

    return template