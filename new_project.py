import os
import json
from PyQt6.QtWidgets import QInputDialog, QMessageBox

class NewProject:
    @staticmethod
    def create_project_structure(project_path):
        folders = ['RDF_UI', 'RDF_ACTION', 'RDF_BW', 'RDF_BVO', 'RDF_DATA']
        for folder in folders:
            os.makedirs(os.path.join(project_path, folder), exist_ok=True)
        
        # Create a default ProjectInfo.json file
        project_info = {
            "init": f"{os.path.basename(project_path)}UI.php"
        }
        with open(os.path.join(project_path, "ProjectInfo.json"), 'w') as file:
            json.dump(project_info, file, indent=4)

        # Create UI file with project name
        ui_file_name = f"{os.path.basename(project_path)}UI.php"
        open(os.path.join(project_path, "RDF_UI", ui_file_name), 'w').close()

    @staticmethod
    def create_new_project(parent):
        try:
            project_name, ok = QInputDialog.getText(parent, "New Project", "Enter project name:")
            if ok and project_name:
                project_path = os.path.join(r'C:\xampp\htdocs', project_name)
                if os.path.exists(project_path):
                    QMessageBox.warning(parent, "Project Exists", "A project with this name already exists.")
                    return None
                
                NewProject.create_project_structure(project_path)
                QMessageBox.information(parent, "Success", "New project created successfully.")
                return project_path
        except Exception as e:
            print(f"Error creating new project: {e}")
            return None