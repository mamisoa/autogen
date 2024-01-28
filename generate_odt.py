replacements = {
    'current_date': '01/01/2024',
    'day_15_before' : '15/12/2023',
    '_genre': 'Monsieur',
    'first_name': 'John',
    'last_name': 'Doe',
    'surgery_date_xx': '01/02/2024',
    'surgery_time_xx': '15:00',
    'surgery_price': '4200',
    '_dob': '01/01/1990',
    'surgery_date_x1': '02/02/2024',
    'surgery_date_10': '10/02/2024',
    'surgery_date_x3': '03/02/2024',
    'surgery_time_x3': '09:00',
    'surgery_date_x7': '08/02/2024',
    'surgery_time_x7': '10:00',
    'surgery_date_30': '08/02/2024',
    'surgery_time_30': '11:00',
}

import zipfile
import os
import re
import json

def edit_odt(file_path, replacements, new_file_path):
    """
    Edit an ODT file by replacing specified placeholders with new values.

    Args:
    file_path (str): Path to the original ODT file.
    replacements (dict): Dictionary of placeholders and their replacements.
    new_file_path (str): Path to save the modified ODT file.

    Returns:
    json: A JSON object containing the status of the replacements and any errors.
    """
    status_report = {"status": "success", "details": {"successful_replacements": [], "failed_replacements": []}}

    try:
        temp_dir = 'temp_odt'

        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        content_file = os.path.join(temp_dir, 'content.xml')

        with open(content_file, 'r', encoding='utf-8') as file:
            content = file.read()

        for old, new in replacements.items():
            # Check if the placeholder exists in the content
            if old in content:
                new_content = re.sub(old, new, content)
                if new_content != content:
                    content = new_content
                    status_report["details"]["successful_replacements"].append({old: new})
                else:
                    status_report["details"]["failed_replacements"].append({old: "replacement not made"})
            else:
                status_report["details"]["failed_replacements"].append({old: "not found in content"})

        with open(content_file, 'w', encoding='utf-8') as file:
            file.write(content)

        with zipfile.ZipFile(new_file_path, 'w') as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, temp_dir))

        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        if status_report["details"]["failed_replacements"]:
            status_report["status"] = "failure"

    except Exception as e:
        status_report["status"] = "failure"
        status_report["details"]["error"] = f"Error encountered: {str(e)}"

    return json.dumps(status_report, indent=4)

result = edit_odt('./240128_preop_femto.odt', replacements, './updated_preop.odt')
print(result)
