import openai
import json
import ast
import time
import pandas as pd
from build_database import extraire_configs, extract_relevant_elements

###### Finetune du modèle ######

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
with open("C:/Users/Elevate/OneDrive - Francetelevisions/Documents/PowerBI_LLM/PowerBI-LLM/bdd/bdd_jsons_train_unif_filtres.jsonl", "rb") as file:
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

prompt = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
Ton role est de modifier le fichier JSON du rapport fourni selon les instructions fournies par l'utilisateur.
Tu ne dois pas faire d'autres modifications que celles precisees par l'utilisateur.
Tu dois absolument respecter le schema du JSON fourni dans le fichier JSON que tu reponds.
Si tu ne sais pas comment modifier le fichier JSON, reponds 'Modification impossible'""".replace('\n', '')


fine_tuned_model = status['fine_tuned_model']

# Modèle finetuné 10 exemples interactions
# fine_tuned_model = "ft:gpt-3.5-turbo-0125:personal::AL5LdBcA"

# Modèle finetuné 10 exemples uniformisation filtres
fine_tuned_model = "ft:gpt-3.5-turbo-0125:personal::AItubhkO"

json_input_path = "jsons_test/IT__web_multi_slicers.json"


def get_answer(json_input_path, fine_tuned_model, prompt, instructions) :
    with open(json_input_path, 'r') as json_data :
        json_input = json.load(json_data)

    response = openai.ChatCompletion.create(
    model=fine_tuned_model,
    messages=[
        {"role": "system", "content": f"{prompt}"},
        {"role": "user", "content": f"{instructions} en te basant sur le fichier JSON du rapport power BI fourni. Fichier JSON ={json_input}"}
    ]
    )
    json_reponse = response['choices'][0]['message']['content']
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse))

    return json_reponse_clean


instructions = "Uniformise le format de tous les filtres en te basans sur le filtre 'mobile_model_name'"
json_reponse_clean = get_answer(json_input_path, fine_tuned_model, prompt, instructions)


###### Utilisation du modèle version fichiers config ########

prompt_config = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
Je vais te fournir une liste de morceaux de fichiers jsons qui decrivent la configuration de chaque visuel dans un dashboard power bi. 
Ton role est de modifier les arguments dans les morceaux de fichiers jsons du rapport fourni selon les instructions fournies par l'utilisateur.
Tu ne dois pas faire d'autres modifications que celles precisees par l'utilisateur.
Tu dois absolument respecter le schema du JSON fourni.
Si tu ne sais pas comment modifier le fichier JSON, reponds 'Modification impossible'""".replace('\n', '')

def get_answer(json_input_path, fine_tuned_model, prompt, instructions) :

    json_input = extraire_configs(json_input_path, ["slicer",  "advancedSlicerVisual"])

    response = openai.ChatCompletion.create(
    model=fine_tuned_model,
    messages=[
        {"role": "system", "content": f"{prompt}"},
        {"role": "user", "content": f"{instructions} en te basant sur le fichier JSON du rapport power BI fourni. Fichier JSON ={json_input}"}
    ]
    )
    json_reponse = response['choices'][0]['message']['content']
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse))

    return json_reponse_clean


def reinserer_extraits_json(json_input_path, json_reponse_clean, json_output_path):
    # Charger le fichier JSON d'origine
    with open(json_input_path, 'r', encoding='utf-8') as fichier:
        data_origine = json.load(fichier)

    # Charger la réponse du modèle
    extraits_modifies = json.loads(json_reponse_clean)

    # Parcourir chaque extrait modifié
    for extrait in extraits_modifies:
        visual_name = extrait["name"]
        # Chercher le visuel correspondant dans le fichier d'origine
        for visual in data_origine["sections"][0]["visualContainers"]:
            config_data = json.loads(visual['config'])
            if config_data["name"] == visual_name:
                # Remplacer l'ancien visuel par le nouveau
                config_data.update(extrait)
                visual['config'] = json.dumps(config_data)
                break
    
    # Sauvegarder les modifications dans un nouveau fichier JSON
    with open(json_output_path, 'w', encoding='utf-8') as fichier_sortie:
        json.dump(data_origine, fichier_sortie, ensure_ascii=False, indent=4)
    
    print(f"Modifications réinsérées dans le fichier {fichier_sortie}")


###### Application sur une base test #######

bdd_test = pd.read_excel("bdd/bdd_test.xlsx")

bdd_test['json_resultat'] = bdd_test.apply(lambda row: get_answer(row['json_path_before_change'], fine_tuned_model, prompt, row['instructions']), axis=1)

bdd_test.to_excel("bdd_test_output.xlsx", index=False)

##############################################################
######## Utilisation du modèle avec relevant parts ###########

prompt = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
Je vais te fournir une liste de morceaux de fichiers jsons qui decrivent la configuration des filtres dans un dashboard power bi. 
Ton role est de modifier les arguments dans les morceaux de fichiers jsons du rapport fourni selon les instructions fournies par l'utilisateur.
L'objectif final est d'uniformiser les filtres du rapport en se basant sur le format du filtre precise par l'utilisateur.
Tu ne dois absolument pas faire d'autres modifications que celles precisees par l'utilisateur.
Si tu ne sais pas comment faire les bonnes modifications, reponds 'Modification impossible'""".replace('\n', '')

status = check_fine_tune_status(job_id)
print(status)

fine_tuned_model = status['fine_tuned_model']
fine_tuned_model = "ft:gpt-3.5-turbo-0125:personal::AcVIeavl"
json_input_path = "jsons_test/perf_sliders_ftv.json"
instructions = "Uniformise le format des filtres Page et Slider en te basant sur le format du filtre Type sur la page 'Performance du jour'"
json_input_path = "jsons_test/loreal_lbds_reduit.json"
instructions = "Uniformise le format de tous les filtres de la page Products Performance en te basant sur le format du filtre Range"

def get_answer(json_input_path, fine_tuned_model, prompt, instructions) :

    json_input = extract_relevant_elements(json_input_path)

    response = openai.ChatCompletion.create(
        model=fine_tuned_model,
        messages=[
            {"role": "system", "content": f"{prompt}"},
            {"role": "user", "content": f"{instructions} en modifiant les extraits du fichier JSON du rapport power BI fourni. Extraits du fichier JSON ={json_input}"}
        ]
    )
    json_reponse = response['choices'][0]['message']['content']
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse), ensure_ascii=False)

    return json_reponse_clean


reponse = get_answer(json_input_path, fine_tuned_model, prompt, instructions)

original_json_path = "jsons_test/perf_sliders_ftv_reduit.json"
json_output_path = "test.json"
modified_parts = json.loads(reponse)
keys_to_update = ['visualType', 'prototypeQuery', 'objects', 'vcObjects']

section = modified_parts.get('sections', [])[0]
original_section = updated_json.get('sections', [])[0]
modified_container = modified_visual_containers[0]
original_container = original_visual_containers[0]

def update_json_bis(original_json_path, modified_parts, json_output_path, keys_to_update):
    with open(original_json_path, 'r', encoding="utf-8") as file:
        updated_json = json.load(file)

    # Parcourir les sections modifiées
    for section in modified_parts.get('sections', []):
        modified_visual_containers = section.get('visualContainers', [])

        # Rechercher la section correspondante dans l'original
        for original_section in updated_json.get('sections', []):
            if section.get('displayName') == original_section.get('displayName'):
                original_visual_containers = original_section.get('visualContainers', [])

                # Parcourir les visualContainers modifiés
                for modified_container in modified_visual_containers:
                    #modified_name = modified_container.get('name')
                    modified_name = modified_container["prototypeQuery"]["Select"][0]["Name"]

                    # Mettre à jour le conteneur correspondant dans l'original
                    for original_container in original_visual_containers:
                        original_config = json.loads(original_container.get('config', '{}'))
                        #original_name = original_config.get('name')
                        try :
                            original_name = original_config["singleVisual"]["prototypeQuery"]["Select"][0]["Name"]
                        except :
                            pass
                        if original_name == modified_name:
                            # Mettre à jour uniquement les parties spécifiées
                            for key in keys_to_update :
                                original_config['singleVisual'][key] = modified_container[key]
                            # Réécrire la configuration mise à jour
                            original_container['config'] = json.dumps(original_config, ensure_ascii=False)

    # Sauvegarder les modifications dans un nouveau fichier JSON
    with open(json_output_path, 'w', encoding='utf-8') as fichier_sortie:
        json.dump(updated_json, fichier_sortie, ensure_ascii=False, indent=4)

    print(f"Modifications réinsérées dans le fichier {json_output_path}")



def update_json(original_json_path, modified_parts, json_output_path, keys_to_update):
    with open(original_json_path, 'r', encoding="utf-8") as file:
        updated_json = json.load(file)

    # Parcourir les sections modifiées
    for section in modified_parts.get('sections', []):
        modified_visual_containers = section.get('visualContainers', [])

        # Rechercher la section correspondante dans l'original
        for original_section in updated_json.get('sections', []):
            if section.get('displayName') == original_section.get('displayName'):
                original_visual_containers = original_section.get('visualContainers', [])

                # Parcourir les visualContainers modifiés
                for modified_container in modified_visual_containers:
                    #modified_name = modified_container.get('name')
                    modified_name = modified_container["prototypeQuery"]["Select"][0]["NativeReferenceName"]

                    # Mettre à jour le conteneur correspondant dans l'original
                    for original_container in original_visual_containers:
                        original_config = json.loads(original_container.get('config', '{}'))
                        #original_name = original_config.get('name')
                        original_name = original_config["singleVisual"]["prototypeQuery"]["Select"][0]["NativeReferenceName"]
                        if original_name == modified_name:
                            # Mettre à jour uniquement les parties spécifiées
                            for key in keys_to_update :
                                original_config['singleVisual'][key] = modified_container[key]
                            # Réécrire la configuration mise à jour
                            original_container['config'] = json.dumps(original_config, ensure_ascii=False)

    # Sauvegarder les modifications dans un nouveau fichier JSON
    with open(json_output_path, 'w', encoding='utf-8') as fichier_sortie:
        json.dump(updated_json, fichier_sortie, ensure_ascii=False, indent=4)

    print(f"Modifications réinsérées dans le fichier {json_output_path}")

update_json_bis(original_json_path, modified_parts, json_output_path, keys_to_update)

# section = modified_parts.get('sections', [])[0]
# original_section = updated_json.get('sections', [])[0]

# modified_container = modified_visual_containers[1]
# original_container = original_visual_containers[2]

# key='objects'

# original_config['singleVisual']['visualType']
# original_config['prototypeQuery']
# modified_container['objects']

# modified_container["prototypeQuery"]["Select"][0]["NativeReferenceName"]

# original_config["singleVisual"]["prototypeQuery"]["Select"][0]["NativeReferenceName"]