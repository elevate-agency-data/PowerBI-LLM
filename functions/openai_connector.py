from streamlit_app import *
import streamlit as st
import openai
import json
import ast

# Function to modify the report.json file based on user input
# def modify_report_json(input_text, report_json_content):
#     # Create a prompt for the model
#     messages = [
#         {"role": "system", "content": "You are an assistant that helps modify PowerBI JSON files."},
#         {"role": "user", "content": f"Here is a JSON file related to a PowerBI report:\n{report_json_content}\n\nI am going to provide you with a user request that includes some changes they would like to make to the PowerBI report. You need to make the corresponding modifications to the JSON file and send me the modified JSON file. You should only make modifications based on the user request and not invent any other requests.\n\nHere is the user request: {input_text}"}
#     ]
    
#     # Call the chat-based fine-tuned model
#     response = openai.ChatCompletion.create(
#         model="ft:gpt-3.5-turbo-0125:personal::AG3HbjhD",  # Fine-tuned model
#         messages=messages,
#         max_tokens=1500  # Adjust token limit if needed
#     )
    
#     modified_json_content = response['choices'][0]['message']['content']
#     modified_json_content
#     try:
#         # Try to parse the response as JSON
#         modified_json_data = json.loads(modified_json_content)
#         modified_json_data
#     except json.JSONDecodeError:
#         st.error("The modified content is not valid JSON. Please refine the request or check the output.")
#         return None
    
#     # Return the modified JSON content
#     return json.dumps(modified_json_data, indent=2)


def summarize_dashboard(target_platform, json_content):
    try:
        # Combine the user prompt with the JSON content
        combined_prompt = (
            f"Make documentation based on the content of the JSON file for {target_platform}. "
            "In the documentation, you should include:\n"
            "1) The general purpose of the dashboard\n"
            "2) Data sources for different tables\n"
            "3) Calculation formulas for DAX measures and calculated columns\n"
            "4) Data model structure, including relationships between tables\n\n"
            f"Here is the JSON content:\n{json_content}"
        )

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
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



def get_answer(extracted_report, instructions) :

    prompt = """Tu es un data analyst expert en Power BI qui a l'habitude de travailler avec des rapports Power BI et leur fichier JSON. 
    Je vais te fournir une liste de morceaux de fichiers jsons qui decrivent la configuration des filtres dans un dashboard power bi. 
    Ton role est de modifier les arguments dans les morceaux de fichiers jsons du rapport fourni selon les instructions fournies par l'utilisateur.
    L'objectif final est d'uniformiser les filtres du rapport en se basant sur le format du filtre precise par l'utilisateur.
    Tu ne dois absolument pas faire d'autres modifications que celles precisees par l'utilisateur.
    Si tu ne sais pas comment faire les bonnes modifications, reponds 'Modification impossible'""".replace('\n', '')

    response = openai.ChatCompletion.create(
    model="ft:gpt-3.5-turbo-0125:personal::AWNyxMxO",
    messages=[
        {"role": "system", "content": f"{prompt}"},
        {"role": "user", "content": f"{instructions} en modifiant les extraits du fichier JSON du rapport power BI fourni. Extraits du fichier JSON ={extracted_report}"}
    ]
    )
    json_reponse = response['choices'][0]['message']['content']
    json_reponse_clean = json.dumps(ast.literal_eval(json_reponse))

    return json_reponse_clean


def update_json(json_to_update, modified_parts):

    keys_to_update = ['visualType', 'prototypeQuery', 'objects', 'vcObjects']

    # Parcourir les sections modifiées
    for section in modified_parts.get('sections', []):
        modified_visual_containers = section.get('visualContainers', [])

        # Rechercher la section correspondante dans l'original
        for original_section in json_to_update.get('sections', []):
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
                            original_container['config'] = json.dumps(original_config)

    return json_to_update
