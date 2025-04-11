import json
import pandas as pd
import openai
import copy
import ast

# Set the OpenAI API keys by reading them from files
openai.api_key = api_key

# Path to the JSON file
json_input_path = "jsons_test/contenus_ftv.json"

# Open and read the JSON file
with open(json_input_path, 'r', encoding="utf-8") as file:
    original_json_data = json.load(file)

def build_df(json_data):
    dict_page_visuals = {}

    for section in json_data.get("sections", []):
        # Only include pages that are not hidden in the dashboard
        page_config = json.loads(section['config'])
        if page_config.get('visibility') != 1:
            visuals_list_per_page = []

            # Process each visual container in the section
            for visual in section.get("visualContainers", []):
                # Parse config if it's a string
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                # visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_id = config_data.get("name", {})
                
                visual_name = None
                visual_name_key = None
                header_present = False
                title_present = False

                # Determine slicer name and key
                try :
                    if ("title" in config_data['singleVisual']["vcObjects"] and 
                        'text' in config_data['singleVisual']["vcObjects"]["title"][0]["properties"] and 
                        config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"] != "''"):
                        
                        visual_name = config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
                        visual_name_key = "title"
                        title_present = True
                except :
                    pass

                if visual_name is None :
                    try :
                        if ('header' in config_data['singleVisual']['objects'] and 
                            'text' in config_data['singleVisual']['objects']['header'][0]['properties']) :
                            # and config_data['singleVisual']['objects']['header'][0]['properties']['show']['expr']['Literal']['Value'] != "false"):
                            visual_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                            visual_name_key = "header"
                            header_present = True
                    except :
                        pass
                
                if visual_name is None :
                    try :
                        if 'NativeReferenceName' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                            visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                            visual_name_key = "NativeReferenceName"
                    except :
                        pass
                if visual_name is None :
                    try :
                        if 'Name' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                            visual_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']
                            visual_name_key = "Name"
                    except :
                        pass
                
                # slicer_name = slicer_name.replace("'", "").replace(":", "")

                if visual_name and visual_name_key:
                    visuals_list_per_page.append({
                        "visual name": visual_name,
                        "visual id": visual_id,
                        "visual name key": visual_name_key,
                        "visual type": visual_type,
                        "header present": header_present,
                        "title present": title_present
                    })

            # Add slicer visuals for the current page
            dict_page_visuals[section.get("displayName", "")] = visuals_list_per_page

    # List to store each row as a dictionary
    rows = []

    # Loop through each page and its visuals
    for page_name, visuals in dict_page_visuals.items():
        for visual in visuals:
            rows.append({
                "page name": page_name,
                "visual id": visual["visual id"],
                "visual name": visual["visual name"],
                "visual name key": visual["visual name key"],
                "visual type": visual["visual type"],
                "header present": visual["header present"],
                "title present": visual["title present"]
            })

    # Convert list of dictionaries into a DataFrame
    df = pd.DataFrame(rows)

    return df


pd.set_option('display.max_columns', None)
df = build_df(original_json_data)
print(df)



user_prompt = (
    "I want to update the visuals 'Campagne', 'Offre', 'Typologie de vidéos', 'Plateforme' and 'Catégorie' on all pages, in the dashboard so that their format match the 'Catégorie' slicer on the 'Vision hebdo' page."
)

prompt = (
    "You are an assistant designed to identify the source page, source visuals, target page, and target visuals based on user input. "
    "Your answer should be based on the given DataFrame, which contains information about all the pages and visuals in the dashboard. "
    "It is essential that you identify the correct source visual and target visuals from the user input and the DataFrame."
    "The name of the visuals and pages must be identical to the ones in the Dataframe."
    "If the user does not specify a particular page for uniformization, they might want to apply uniformization to all the pages.\n"
)

# Modèle finetuné 10 exemples uniformisation filtres
fine_tuned_model = "ft:gpt-3.5-turbo-0125:personal::BAwNWDg1"

def get_answer(json_input_path, fine_tuned_model, prompt, user_prompt) :
    with open(json_input_path, 'r', encoding="utf-8") as json_data: 
        json_input = json.load(json_data)
    df = build_df(json_input)
    df_infos = df[['page name', 'visual id', 'visual name']].drop_duplicates().to_string()
    response = openai.ChatCompletion.create(
    model=fine_tuned_model,
    messages=[
        {"role": "system", "content": f"{prompt}"}, 
        {"role": "user", "content": f"{user_prompt}. Here is the informations on the dashboard you should base your analysis on: {df_infos}"}, 
    ]
    )
    json_reponse = response['choices'][0]['message']['content']
    json_reponse= json_reponse.encode('latin1').decode('utf-8')
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse), indent=4, ensure_ascii=False)

    return json_reponse_clean


json_source_target = get_answer(json_input_path, fine_tuned_model, prompt, user_prompt)


json_source_target = json.loads(json_source_target)
print(json_source_target)


def extract_json_elements_source_visual(json_data, json_source_target):
    source_page_name = json_source_target["source"]["source_page"]
    source_visual_id = json_source_target["source"]["source_visual"]
    for section in json_data.get("sections", []):
        page_name = section.get("displayName", "")
        if page_name == source_page_name :
            for visual in section.get("visualContainers", []) :
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)
                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']
                if visual_type in visual_type_to_be_included :
                    visual_id = config_data.get("name", {})
                    if visual_id == source_visual_id :
                        visual_summary = {
                            "visualType": visual_type,
                            "objects": config_data.get("singleVisual", {}).get("objects", {}),
                            "vcObjects": config_data.get("singleVisual", {}).get("vcObjects", {})
                        }
                
    return visual_summary

source_visual_elements = extract_json_elements_source_visual(original_json_data, json_source_target)
print(source_visual_elements)

def update_target_visuals(original_json_data, source_visual_elements, source_page_name, source_visual_id, target_page_name, target_visual_id, df):
    for section in original_json_data.get("sections", []):
        page_name = section.get("displayName", "")
        if page_name == target_page_name:
            print(page_name)
            for visual in section.get("visualContainers", []):
                config_data = visual.get("config", {})
                if isinstance(config_data, str):
                    config_data = json.loads(config_data)

                visual_type = config_data.get("singleVisual", {}).get("visualType", "")
                visual_type_to_be_included = ['slicer', 'advancedSlicerVisual']

                if visual_type in visual_type_to_be_included:
                    visual_id = config_data.get("name", {})
                    if visual_id == target_visual_id:
                        # Crée une copie indépendante des éléments source
                        local_visual_elements = copy.deepcopy(source_visual_elements)
                        config_data["singleVisual"].update(local_visual_elements)

                        source_title_present = df[(df["visual id"] == source_visual_id) & (df["page name"] == source_page_name)]["title present"].values[0]
                        source_header_present = df[(df["visual id"] == source_visual_id) & (df["page name"] == source_page_name)]["header present"].values[0]

                        target_header_present = df[(df["visual id"] == target_visual_id) & (df["page name"] == target_page_name)]["header present"].values[0]

                        target_visual_name = df[df["visual id"] == target_visual_id]["visual name"].values[0]

                        # Modifie le titre si nécessaire
                        if source_title_present == True:
                            #config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"] = {"expr": {"Literal": {"Value": f"{visual_name}"}}}
                            updated_config_data = copy.deepcopy(config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"])
                            updated_config_data = {"expr": {"Literal": {"Value": f"{target_visual_name}"}}}
                            config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"] = updated_config_data
                            print(config_data["singleVisual"]["vcObjects"]["title"][0]["properties"]["text"])


                        # Modifie le header si présent dans la source
                        if source_header_present == True:
                            print("header modifié")
                            # Crée une copie indépendante du header
                            #config_data["singleVisual"]["objects"]["header"][0]["properties"]["text"] = {"expr": {"Literal": {"Value": f"{visual_name}"}}}
                            updated_config_data = copy.deepcopy(config_data["singleVisual"]["objects"]["header"][0]["properties"]["text"])
                            updated_config_data = {"expr": {"Literal": {"Value": f"{target_visual_name}"}}}
                            config_data["singleVisual"]["objects"]["header"][0]["properties"]["text"] = updated_config_data


                        # Si le header est dans le target mais pas dans la source
                        if target_header_present == True and 'text' not in source_visual_elements["objects"]["header"][0]["properties"]:
                            print("header rajouté")
                            # Crée une copie indépendante du header
                            target_header = copy.deepcopy(config_data["singleVisual"]["objects"]["header"][0]["properties"])
                            target_header.update({"text": {"expr": {"Literal": {"Value": f"{target_visual_name}"}}}})
                            config_data["singleVisual"]["objects"]["header"][0]["properties"] = target_header
                        
    
                        visual["config"] = json.dumps(config_data, ensure_ascii=False)
                        print("json updated")

    with open("test.json", "w", encoding='utf8') as file:
        json.dump(original_json_data, file, indent=4, ensure_ascii=False)
    print("end update")


def modify_json(original_json_data, json_source_target) :
    source_page_name = json_source_target["source"]["source_page"]
    source_visual_id = json_source_target["source"]["source_visual"]
    source_visual_elements = extract_json_elements_source_visual(original_json_data, json_source_target)
    for target_visual in json_source_target["target"] :
        target_page_name = target_visual["target_page"]
        target_visual_id = target_visual["target_visual"]
        update_target_visuals(original_json_data, source_visual_elements, source_page_name, source_visual_id, target_page_name, target_visual_id, df)
    print("json updated for all visuals")
        

modify_json(original_json_data, json_source_target)

