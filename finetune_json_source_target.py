import json
import pandas as pd
import openai
import ast

##########################
# Construction de la bdd #
##########################

# Path to the JSON file
file_path = "jsons_test/ftv_profils_videonautes.json"

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
                visual_id = config_data.get("name", {})
                
                if visual_type in visual_type_to_be_included:
                    slicer_name = None
                    slicer_name_key = None
                    header_present = False
                    title_present = False

                    # Determine slicer name and key
                    try :
                        if ("title" in config_data['singleVisual']["vcObjects"] and 
                            'text' in config_data['singleVisual']["vcObjects"]["title"][0]["properties"] and 
                            config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"] != "''"):
                            
                            slicer_name = config_data['singleVisual']["vcObjects"]["title"][0]["properties"]["text"]["expr"]["Literal"]["Value"]
                            slicer_name_key = "title"
                            title_present = True
                    except :
                        pass

                    if slicer_name is None :
                        try :
                            if ('header' in config_data['singleVisual']['objects'] and 
                                'text' in config_data['singleVisual']['objects']['header'][0]['properties']) :
                                # and config_data['singleVisual']['objects']['header'][0]['properties']['show']['expr']['Literal']['Value'] != "false"):
                                slicer_name = config_data['singleVisual']['objects']['header'][0]['properties']['text']['expr']['Literal']['Value']
                                slicer_name_key = "header"
                                header_present = True
                        except :
                            pass
                    
                    if slicer_name is None :
                        try :
                            if 'NativeReferenceName' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                                slicer_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['NativeReferenceName']
                                slicer_name_key = "NativeReferenceName"
                        except :
                            pass
                    if slicer_name is None :
                        try :
                            if 'Name' in config_data['singleVisual']['prototypeQuery']['Select'][0]:
                                slicer_name = config_data['singleVisual']['prototypeQuery']['Select'][0]['Name']
                                slicer_name_key = "Name"
                        except :
                            pass
                    
                    # slicer_name = slicer_name.replace("'", "").replace(":", "")
                    
                    

                    if slicer_name and slicer_name_key:
                        slicer_list_per_page.append({
                            "visual name": slicer_name,
                            "visual id": visual_id,
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
    "I want to update the slicer 'Type de plateforme' on the 'Vision globale du mois' page so that his format match the 'Type vidéonautes' slicer on the 'Profil vidéonautes saison' page."
)

prompt = (
    "You are an assistant designed to identify the source page, source visuals, target page, and target visuals based on user input. "
    "Your answer should be based on the given DataFrame, which contains information about all the pages and visuals in the dashboard. "
    "It is essential that you identify the correct source visual and target visuals from the user input and the DataFrame."
    "The name of the visuals and pages must be identical to the ones in the Dataframe."
    "If the user does not specify a particular page for uniformization, they might want to apply uniformization to all the pages.\n"
)

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
                            "description": "The id of the visual on the source page used as the formatting template. This should be extracted from the 'visual id' column of the dataframe. Only one source visual is permitted."
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
                                "description": "The id of each target visual on the target page to be formatted. These ids are sourced from the 'visual id' column of the dataframe. Multiple target visuals can be specified per page."
                            }
                        }
                    }
                }
            }
        }
    }
]

####### Récupérer les jsons source target
completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        functions=function_descriptions,
        function_call="auto",  # Let the model decide if it needs to call the function
    )

arguments = completion.choices[0].message["function_call"]["arguments"]

with open("jsons_source_target/videonautes_ftv_3.json", 'w', encoding='utf8') as file:
    json_obj = json.loads(arguments)
    json.dump(json_obj, file, indent=3, ensure_ascii=False)

df[['page name', 'visual id', 'visual name']]

####### Construire le template pour chaque exemple de la base ########

def template_json(user_prompt, original_json_path, json_source_target_path, prompt):
# Fonction pour mettre en forme le prompt avec le json PBI
    with open(original_json_path, 'r', encoding="utf-8") as file:
        original_json_data = json.load(file)
    df = build_df(original_json_data)
    with open(json_source_target_path, 'r', encoding="utf-8") as json_data :
        json_source_target = json.load(json_data)
    df_infos = df[['page name', 'visual id', 'visual name']].drop_duplicates().to_string()
    template = {"messages": [
        {"role": "system", "content": f"{prompt}"}, 
        {"role": "user", "content": f"{user_prompt}. Here is the informations on the dashboard you should base your analysis on: {df_infos}"}, 
        {"role": "assistant", "content": f"{json_source_target}"}]}

    final_json = json.dumps(template, indent=4, ensure_ascii=False)

    return final_json

# Test sur un rapport

user_prompt = "I want to update the slicer 'Type de plateforme' on the 'Vision globale du mois' page so that his format match the 'Type vidéonautes' slicer on the 'Profil vidéonautes saison' page."
original_json_path = "jsons_test/ftv_profils_videonautes.json"
json_source_target_path = "jsons_source_target/videonautes_ftv_3.json"

processed_json = template_json(user_prompt, original_json_path, json_source_target_path, prompt)
print(processed_json)

####### Construction de la base de données #######

bdd_excel = pd.read_excel("bdd/bdd_json_source_target.xlsx")
jsonl_path = 'bdd/bdd_json_source_target.jsonl'

def build_bdd(bdd_excel, prompt, jsonl_path):
    bdd_excel['json_resultat'] = bdd_excel.apply(lambda row: template_json(row['user_prompt'], row['json_source_path'], row['json_output_path'], prompt), axis=1)

    # On ajoute tous les jsons à un fichier jsonl
    with open(jsonl_path, 'w', encoding="utf-8") as file:
        for item in bdd_excel['json_resultat']:
            json_obj = json.loads(item)
            json.dump(json_obj, file, ensure_ascii=False)
            file.write('\n')
    
build_bdd(bdd_excel, prompt, jsonl_path)

##########################
# Finetuning du modèle   #
##########################

# Define a function to open a file and return its contents as a string
def open_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as infile:
        return infile.read()

# Define a function to save content to a file
def save_file(filepath, content):
    with open(filepath, 'a', encoding='utf-8') as outfile:
        outfile.write(content)

# Set the OpenAI API keys by reading them from files
openai.api_key = api_key

# Create file
with open("C:/Users/Elevate/OneDrive - Francetelevisions/Documents/PowerBI_LLM/PowerBI-LLM/bdd/bdd_json_source_target.jsonl", "rb") as file:
    response = openai.File.create(
        file=file,
        purpose='fine-tune'
    )

file_id = response['id']
print(f"File uploaded successfully with ID: {file_id}")


# Using the provided file_id
model_name = "gpt-3.5-turbo"  

response = openai.FineTuningJob.create(
    training_file=file_id,
    model=model_name
)

job_id = response['id']

print(f"Fine-tuning job created successfully with ID: {job_id}")

# Fonction pour vérifier l'état du travail de fine-tuning
def check_fine_tune_status(job_id):
    response = openai.FineTuningJob.retrieve(job_id)
    return response

status = check_fine_tune_status(job_id)
print(status)


##### Utilisation du modèle finetuné ######

user_prompt = (
    "I want to update the slicers 'Genre', 'Age', 'Region' and 'Periode' on the 'Vision utilisateurs' page and the slicers 'Livechat JOP' and 'Data JOP' on the 'Vision visiteurs' page, so that his format match the 'Video JOP' slicer on the 'Vision visiteurs' page."
)

prompt = (
    "You are an assistant designed to identify the source page, source visuals, target page, and target visuals based on user input. "
    "Your answer should be based on the given DataFrame, which contains information about all the pages and visuals in the dashboard. "
    "It is essential that you identify the correct source visual and target visuals from the user input and the DataFrame."
    "The name of the visuals and pages must be identical to the ones in the Dataframe."
    "If the user does not specify a particular page for uniformization, they might want to apply uniformization to all the pages.\n"
)

fine_tuned_model = status['fine_tuned_model']

# Modèle finetuné 10 exemples uniformisation filtres
fine_tuned_model = "ft:gpt-3.5-turbo-0125:personal::BAwNWDg1"

json_input_path = "jsons_test/ftv_jo.json"


def get_answer(json_input_path, fine_tuned_model, prompt, user_prompt) :
    with open(json_input_path, 'r') as json_data :
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
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse), indent=4, ensure_ascii=False)

    return json_reponse_clean


json_reponse_clean = get_answer(json_input_path, fine_tuned_model, prompt, user_prompt)
