import zipfile
import os
import json

# Function to handle the PBIP folder and extract report.json
def extract_report_json(zip_file):
    # Get the base name of the uploaded zip file, excluding the extension
    inner_folder_name = os.path.splitext(zip_file.name)[0] 
    # Extract the zip file
    extract_path = '/mnt/data/pbip_extracted/'
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    inner_folder_path = os.path.join(extract_path, inner_folder_name)
    # Print the contents of the inner folder
    inner_folder_contents = os.listdir(inner_folder_path)
    # Look for the folder that ends with '.Report'
    report_folder_path = None
    for folder in inner_folder_contents:
        if folder.endswith('.Report') and os.path.isdir(os.path.join(inner_folder_path, folder)):
            report_folder_path = os.path.join(inner_folder_path, folder)
            break
    report_json_path = os.path.join(report_folder_path, 'report.json')
    # Read and return the content of the report.json file
    with open(report_json_path, 'r', encoding='utf-8') as file:
        # report_json_content = file.read() # this method works for the report modifier use case
        report_json_content = json.load(file)
    
    return report_json_content, inner_folder_path, report_json_path