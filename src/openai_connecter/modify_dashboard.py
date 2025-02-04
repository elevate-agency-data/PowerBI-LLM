"""
This module provides a set of functions to interact with OpenAI's API for modifying a Power BI dashboard.
"""

import openai
import json

def unif_slicers(extracted_report, instructions):
    """Uniformize slicers in the report based on user instructions"""
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
    json_reponse_clean = json.dumps(json.loads(json_reponse), ensure_ascii=False)

    return json_reponse_clean 