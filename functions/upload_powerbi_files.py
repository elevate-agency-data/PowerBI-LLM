import zipfile
import os
import shutil
import json

# Function to handle the PBIP folder and extract report.json and model.bim
def extract_report_and_model(zip_file):
    # Extract the zip file
    extract_path = '/mnt/data/pbip_extracted/'

    # Each time, we first remove the entire directory and its contents
    if os.path.exists(extract_path):
        shutil.rmtree(extract_path)

    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    inner_folder_name = os.listdir(extract_path)[0]
    inner_folder_path = os.path.join(extract_path, inner_folder_name)
    # Print the contents of the inner folder
    inner_folder_contents = os.listdir(inner_folder_path)
    report_folder_path = None
    model_bim_path = None

    # Look for the folder that ends with '.Report' or '.SemanticModel'
    for folder in inner_folder_contents:
        full_folder_path = os.path.join(inner_folder_path, folder)
        if folder.endswith('.Report') and os.path.isdir(full_folder_path):
            report_folder_path = full_folder_path
        elif folder.endswith('.SemanticModel') and os.path.isdir(full_folder_path):
            model_folder_path = full_folder_path

    # Extract report.json
    if report_folder_path:
        report_json_path = os.path.join(report_folder_path, 'report.json')
        with open(report_json_path, 'r', encoding='utf-8') as file:
            report_json_content = json.load(file)
    else:
        report_json_content = None

    # Extract model.bim
    if model_folder_path:
        model_bim_path = os.path.join(model_folder_path, 'model.bim')
        if os.path.exists(model_bim_path):
            with open(model_bim_path, 'r', encoding='utf-8') as file:
                model_bim_content = json.load(file)
        else:
            model_bim_content = None

    return report_json_content, model_bim_content, inner_folder_path, report_json_path, model_bim_path