import json
import pandas as pd
import openai

# Path to the JSON file
file_path = "jsons_test/contenus_ftv.json"

# Open and read the JSON file
with open(file_path, 'r', encoding="utf-8") as file:
    original_json_data = json.load(file)

def build_df(json_data):
    dict_page_slicers = {}

    for section in json_data.get("sections", []):
        # Only include pages that are not hidden in the dashboard
        page_config = json.loads(section['config'])
        if page_config.get('visibility') != 1:
            slicer_list_per_page = []

            # Process each visual container in the section
            for visual in section.get("visualContainers", []):
                # Parse config if it's a string
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                
                if visual_type in visual_type_to_be_included:
                    slicer_name = None
                    slicer_name_key = None
                    header_present = False
                    title_present = False

                    # Determine slicer name and key
                    if 'header' in config_data['singleVisual']['objects'] and 'text' in config_data['singleVisual']['objects']['header'][0]['properties']:
                        slicer_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                        slicer_name_key = "header"
                        header_present = True
                    elif 'NativeReferenceName' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                        slicer_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                        slicer_name_key = "NativeReferenceName"
                    elif 'Name' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                        slicer_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']
                        slicer_name_key = "Name"
                    
                    # Determine if there is a title
                    if ("title" in config_data['singleVisual']["vcObjects"] and 
                        'text' in config_data['singleVisual']["vcObjects"]["title"][0]["properties"] and 
                        config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"] != "''"):
                        title_present = True
                              
                    if slicer_name and slicer_name_key:
                        slicer_list_per_page.append({
                            "visual name": slicer_name,
                            "visual name key": slicer_name_key,
                            "visual type": visual_type,
                            "header present": header_present,
                            "title present": title_present
                        })

            # Add slicer visuals for the current page
            dict_page_slicers[section.get("displayName", "")] = slicer_list_per_page

    # List to store each row as a dictionary
    rows = []

    # Loop through each page and its visuals
    for page_name, visuals in dict_page_slicers.items():
        for visual in visuals:
            rows.append({
                "page name": page_name,
                "visual name": visual["visual name"],
                "visual name key": visual["visual name key"],
                "visual type": visual["visual type"],
                "header present": visual["header present"],
                "title present": visual["title present"]
            })

    # Convert list of dictionaries into a DataFrame
    df = pd.DataFrame(rows)

    return df


df = build_df(original_json_data)


function_descriptions = [
    {
        "name": "uniformize_visuals",
        "description": "This function automates the standardization of visual styles across different pages of a Power BI dashboard. It updates the formatting of specified target visuals to match the style of a designated source visual. The function ensures consistent visual presentation, aiding in seamless user experiences across various dashboard pages.",
        "parameters": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "object",
                    "properties": {
                        "source_page": {
                            "type": "string",
                            "description": "Specifies the page name where the source visual is located. This value must correspond to the 'page name' column of the dataframe. Only one source page is allowed."
                        },
                        "source_visual": {
                            "type": "string",
                            "description": "The name of the visual on the source page used as the formatting template. This should be extracted from the 'visual name' column of the dataframe. Only one source visual is permitted."
                        }
                    }
                },
                "target": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target_page": {
                                "type": "string",
                                "description": "The name of the page containing the target visuals that will be updated. This is taken from the 'page name' column of the dataframe. Multiple target pages can be specified. The source page can also be a target page."
                            },
                            "target_visual": {
                                "type": "string",
                                "description": "The identifier of each target visual on the target page to be formatted. These identifiers are sourced from the 'visual name' column of the dataframe. Multiple target visuals can be specified per page."
                            }
                        }
                    }
                }
            }
        }
    }
]

def generate_completion(user_input):
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_input}],
        functions=function_descriptions,
        function_call="auto",  # Let the model decide if it needs to call the function
    )
    arguments = completion.choices[0].message["function_call"]["arguments"]
    return arguments



user_prompt = (
    "I want to update all the slicers in the dashboard so that their format match the 'Gender' slicer on the 'Page 1' page."
)
user_prompt = (
    "I want to update the slicers 'Campagne', 'Offre', 'Typologie de vidéos', 'Plateforme' and 'Catégorie' on all pages, in the dashboard so that their format match the 'Catégorie' slicer on the 'Vision hebdo' page."
)

total_prompt = (
    "You are an assistant designed to identify the source page, source visuals, target page, and target visuals based on user input. "
    "Your answer should be based on the given DataFrame, which contains information about all the pages and visuals in the dashboard. "
    #"It is essential to understand the user's intention and ensure that nothing in the DataFrame is omitted."
    "It is essential that you identify the correct source visual and target visuals from the user input and the DataFrame."
    "If the user does not specify a particular page for uniformization, they might want to apply uniformization to all the pages.\n"
    f"Here is the user input: {user_prompt}\n"
    f"Here is the DataFrame you should base your analysis on:\n{df}"
)

dict_slicers = generate_completion(total_prompt)
dict_slicers = json.loads(dict_slicers)
print(dict_slicers)

def extract_json_elements_source_visual(json_data, source_page_name, source_visual_name, df):
    for section in json_data.get("sections", []):
        page_name = section.get("displayName", "")
        if page_name == source_page_name :
            for visual in section.get("visualContainers", []) :
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                #tous les visuels sont parcourus et certains n'ont pas de prototypequery ou text d'où le try/except
                # if 'header' in config_data['singleVisual']['objects'] and 'text' in config_data['singleVisual']['objects']['header'][0]['properties'] :
                #     visual_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                # elif 'NativeReferenceName' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                #     visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                # else : 
                #     visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']
                if visual_type in visual_type_to_be_included :
                    name_key = df[(df["visual name"] == source_visual_name) & (df["page name"] == source_page_name)]["visual name key"].values[0]
                    if name_key == "header" :
                        visual_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                    elif name_key == "NativeReferenceName" :
                        visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                    elif name_key == "Name" :
                        visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']

                    if visual_name == source_visual_name :
                        visual_summary = {
                            "visualType": visual_type,
                            "objects": config_data.get("singleVisual", {}).get("objects", {}),
                            "vcObjects": config_data.get("singleVisual", {}).get("vcObjects", {})
                        }
                
    return visual_summary


source_page_name = dict_slicers["source"]["source_page"]
source_visual_name = dict_slicers["source"]["source_visual"]
source_visual_elements = extract_json_elements_source_visual(original_json_data, source_page_name, source_visual_name, df)

source_page_name = "Vision mensuelle"
source_visual_name = "'Plateforme:'"

target_page_name = "Vision hebdo"
target_visual_name = "'Offre:'"

def update_target_visuals(original_json_data, source_visual_elements, target_page_name, target_visual_name, df):
    for section in original_json_data.get("sections", []):
        page_name = section.get("displayName", "")
        if page_name == target_page_name :
            print(page_name)
            for visual in section.get("visualContainers", []) :
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                if visual_type in visual_type_to_be_included :
                    name_key = df[(df["visual name"] == target_visual_name) & (df["page name"] == target_page_name)]["visual name key"].values[0]
                    # On regarde d'où provient le nom du visuel target et on va chercher au même endroit le nom du visuel en train d'être parcouru dans la boucle for. Si ce n'est pas le bon -> pass
                    if name_key == "header" :
                        # try/except parce que le visuel en train d'être parcouru n'a peut être pas de header
                        try :
                            visual_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                        except :
                            visual_name = None
                    elif name_key == "NativeReferenceName" :
                        try :
                            visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                        except :
                            visual_name = None
                    elif name_key == "Name" :
                        try :
                            visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']
                        except :
                            visual_name = None
                    # print(visual_name, target_visual_name)
                    if visual_name == target_visual_name :
                        print(visual_name)
                        # print(True)
                        config_data["singleVisual"].update(source_visual_elements)

                        source_title_present = df[(df["visual name"] == source_visual_name) & (df["page name"] == source_page_name)]["title present"].values[0]
                        source_header_present = df[(df["visual name"] == source_visual_name) & (df["page name"] == source_page_name)]["header present"].values[0]

                        target_header_present = df[(df["visual name"] == target_visual_name) & (df["page name"] == target_page_name)]["header present"].values[0]
                        
                        # S'il y a un titre on re modifie pour que les slicers n'aient pas tous le même titre
                        if source_title_present == True :
                            print("title modifié")
                            config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"] = {"expr": {"Literal": {"Value": f"{visual_name}"}}}

                        if source_header_present == True :
                            print("header modifié")
                            config_data["singleVisual"]["objects"]["header"][0]["properties"]['text'] = {"expr": {"Literal": {"Value": f"{visual_name}"}}}
                        
                        #Si header dans target visuel mais pas dans source
                        if target_header_present == True and 'text' not in source_visual_elements["objects"]["header"][0]["properties"]:
                            print("header rajouté")
                            config_data["singleVisual"]["objects"]["header"][0]["properties"].update({"text" : {"expr": {"Literal": {"Value": f"{visual_name}"}}}})

                        visual["config"] = json.dumps(config_data, ensure_ascii=False)
                        print("json updated")

    with open("test.json", "w", encoding='utf8') as file:
        json.dump(original_json_data, file, indent=4, ensure_ascii=False)
    print("end update")

def modify_json(original_json_data, dict_slicers) :
    source_page_name = dict_slicers["source"]["source_page"]
    source_visual_name = dict_slicers["source"]["source_visual"]
    source_visual_elements = extract_json_elements_source_visual(original_json_data, source_page_name, source_visual_name, df)
    for target_visual in dict_slicers["target"] :
        target_page_name = target_visual["target_page"]
        target_visual_name = target_visual["target_visual"]
        update_target_visuals(original_json_data, source_visual_elements, target_page_name, target_visual_name, df)
    print("json updated for all visuals")
        

modify_json(original_json_data, dict_slicers)


source_page_name = "Vision hebdo"
source_visual_name = "'Offre:'"
offre_visual_elements = extract_json_elements_source_visual(original_json_data, source_page_name, source_visual_name)
