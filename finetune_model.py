import openai
import json
import ast
from tqdm import tqdm
import time
import pandas as pd

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
api_key = "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"
openai.api_key = api_key

# Create file
with open("C:/Users/Elevate/Documents/PowerBI_LLM/PowerBI-LLM/bdd/bdd_jsons_train_unif_filtres.jsonl", "rb") as file:
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
job_id = "ftjob-8tNx7QfT3CMJ011hEgi0E6zS"
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
Si tu ne sais pas comment modifier le fichier JSON, reponds 'Impossible de modifier le fichier JSON'""".replace('\n', '')

fine_tuned_model = status['fine_tuned_model']

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


instructions = "Uniformise le format de tous les filtres en te basant sur le format du filtre Country"
json_reponse_clean = get_answer(json_input_path, fine_tuned_model, prompt, instructions)

###### Application sur une base test #######

bdd_test = pd.read_excel("bdd/bdd_test.xlsx")

bdd_test['json_resultat'] = bdd_test.apply(lambda row: get_answer(row['json_path_before_change'], fine_tuned_model, prompt, row['instructions']), axis=1)

bdd_test.to_excel("bdd_test_output.xlsx", index=False)