import json

def extract_relevant_elements(json_data):
    extracted_data = {
        "config": json_data.get("config", {}),
        "sections": []
    }

    for section in json_data.get("sections", []):
        # Store displayName to know the section/page name
        section_summary = {
            "displayName": section.get("displayName", ""),
            "visualContainers": []
        }

        # Process each visual container in the section
        for visual in section.get("visualContainers", []):
            # Parse config if it's a string
            config_data = visual.get("config", {})
            if isinstance(config_data, str):
                config_data = json.loads(config_data)

            # Extract relevant visual properties
            visual_summary = {
                "visualType": config_data.get("singleVisual", {}).get("visualType", ""),
                "projections": config_data.get("singleVisual", {}).get("projections", []),
                "prototypeQuery": config_data.get("singleVisual", {}).get("prototypeQuery", {}),
                "columnProperties": config_data.get("singleVisual", {}).get("columnProperties", {}),
                "title": config_data.get("vcObjects", {}).get("title", []),
                "filters": visual.get("filters", [])
            }
            
            # Add visual summary if it has useful data
            if any(visual_summary.values()):
                section_summary["visualContainers"].append(visual_summary)

        # Add section summary if it has relevant visual containers
        if section_summary["visualContainers"]:
            extracted_data["sections"].append(section_summary)

    return extracted_data