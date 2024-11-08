import zipfile
import io
import os

# Function to write the modified JSON back to the original folder structure and re-zip the file
def write_modified_zip(modified_json, report_json_path, folder_path):
    # Write the modified JSON content back to report.json
    with open(report_json_path, 'w', encoding='utf-8') as file:
        file.write(modified_json)

    # Create a new zip file with the modified content
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as new_zip:
        # Walk the folder and add everything back to the zip
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                new_zip.write(file_path, arcname=arcname)

    zip_buffer.seek(0)  # Move to the beginning of the file for download
    return zip_buffer