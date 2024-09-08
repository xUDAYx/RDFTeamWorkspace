import requests
import os
import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QDialog, QApplication, QVBoxLayout, QProgressBar, QLabel

import os
import sys
import requests
import zipfile
import shutil
from PyQt6.QtWidgets import QMessageBox

class Download:
    def update_boilerplate(self, parent=None):
        url = 'http://takeitideas.in/Downloads/Boilerplates.zip'
        
        # Determine the path of the base folder (where the script or executable is located)
        base_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        print(base_folder)
        
        # Paths for the downloaded zip file and the extraction folder
        local_zip_path = os.path.join(base_folder, 'Boilerplates.zip')
        extract_to_folder = os.path.join(base_folder, 'Boilerplates')

        is_update = os.path.exists(extract_to_folder)

        # Remove the existing Boilerplates folder if it exists
        if os.path.exists(extract_to_folder):
            shutil.rmtree(extract_to_folder)

        try:
            # Download the zip file
            response = requests.get(url, stream=True)

            # Check if the request was successful
            if response.status_code == 200:
                with open(local_zip_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                
                # Extract the contents of the zip file
                with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
                    # Get the list of members
                    members = zip_ref.namelist()
                    
                    # Find the common prefix (likely 'Boilerplates/' in this case)
                    root_folder = os.path.commonprefix(members).rstrip('/')
                    
                    # Extract each member while removing the root folder part
                    for member in members:
                        # Get the correct relative path by removing the root folder part
                        target_path = os.path.join(extract_to_folder, os.path.relpath(member, root_folder))
                        
                        # Create directories if needed
                        target_dir = os.path.dirname(target_path)
                        if not os.path.exists(target_dir):
                            os.makedirs(target_dir)
                        
                        # Extract the file or directory
                        if not member.endswith('/'):  # Avoid directories themselves
                            with zip_ref.open(member) as source, open(target_path, 'wb') as target:
                                shutil.copyfileobj(source, target)

                # Remove the downloaded zip file after extraction
                os.remove(local_zip_path)

                if is_update:
                    QMessageBox.information(parent,"success","Boilerplates updated successfully")
                else:
                    QMessageBox.information(parent, "Success", "Boilerplates downloaded successfully!")

            else:
                QMessageBox.critical(parent, "Error", f"Failed to download the file. Status code: {response.status_code}")
        except Exception as e:
            # Show error message
            QMessageBox.critical(parent, "Error", f"An error occurred: {e}")


class DownloadUIThread(QThread):
    update_message = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)
    error_message = pyqtSignal(str)

    def __init__(self, dialog, parent=None):
        super().__init__(parent)
        self.dialog = dialog

    def run(self):
        url = 'http://takeitideas.in/Downloads/RDF_UI.zip'
        
        base_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        local_folder_path = os.path.join(base_folder, 'RDF_UI')
        zip_file_path = os.path.join(base_folder, 'RDF_UI.zip')

        # Determine if this is a new download or an update
        is_update = os.path.exists(local_folder_path)

        try:
            # Download the zip file
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                with open(zip_file_path, 'wb') as file:
                    total_length = int(response.headers.get('content-length'))
                    downloaded = 0

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            progress = int(100 * downloaded / total_length)
                            self.progress_update.emit(progress, "Downloading RDF_UI.zip")
            else:
                self.error_message.emit(f"Failed to download the file. Status code: {response.status_code}")
                return

            # Extract the zip file
            if os.path.exists(zip_file_path):
                import zipfile
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(local_folder_path)
                os.remove(zip_file_path)

                if is_update:
                    self.update_message.emit("RDF_UI folder updated successfully!")
                else:
                    self.update_message.emit("RDF_UI folder downloaded successfully!")
            else:
                self.error_message.emit(f"Failed to find the downloaded zip file.")
        except Exception as e:
            self.error_message.emit(f"An error occurred: {e}")

class DownloadProjectsThread(QThread):
    update_message = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)
    error_message = pyqtSignal(str)

    def __init__(self, dialog, parent=None):
        super().__init__(parent)
        self.dialog = dialog

    def run(self):
        url = 'http://takeitideas.in/Downloads/RDF_Projects.zip'
        
        # Define the path for the ZIP file and extraction folder
        base_folder = 'C:/xampp/htdocs'  # Base directory where the extraction should happen
        local_folder_path = os.path.join(base_folder, 'RDFProjects_ROOT')  # Target extraction folder
        zip_file_path = os.path.join(base_folder, 'RDF_Projects.zip')

        try:
            # Download the ZIP file
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(zip_file_path, 'wb') as file:
                    total_length = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            progress = int(100 * downloaded / total_length)
                            self.progress_update.emit(progress, "Downloading RDF_Projects.zip")
            else:
                self.error_message.emit(f"Failed to download the file. Status code: {response.status_code}")
                return

            # Ensure the extraction folder exists
            if not os.path.exists(local_folder_path):
                os.makedirs(local_folder_path)

            # Extract the ZIP file
            if os.path.exists(zip_file_path):
                import zipfile
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(local_folder_path)
                os.remove(zip_file_path)

                self.update_message.emit("RDF_Projects folder extracted successfully!")
            else:
                self.error_message.emit(f"Failed to find the downloaded zip file.")
        except Exception as e:
            self.error_message.emit(f"An error occurred: {e}")


class DownloadFeaturesThread(QThread):
    update_message = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)
    error_message = pyqtSignal(str)

    def __init__(self, dialog, parent=None):
        super().__init__(parent)
        self.dialog = dialog

    def run(self):
        url = 'http://takeitideas.in/Downloads/RDF_Features.zip'
        
        base_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        local_folder_path = os.path.join(base_folder, 'RDF_Features')
        zip_file_path = os.path.join(base_folder, 'RDF_Features.zip')

        is_update = os.path.exists(local_folder_path)

        try:
            response = requests.get(url, stream=True)

            if response.status_code == 200:
                with open(zip_file_path, 'wb') as file:
                    total_length = int(response.headers.get('content-length'))
                    downloaded = 0

                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                            downloaded += len(chunk)
                            progress = int(100 * downloaded / total_length)
                            self.progress_update.emit(progress, "Downloading RDF_Features.zip")
            else:
                self.error_message.emit(f"Failed to download the file. Status code: {response.status_code}")
                return

            if os.path.exists(zip_file_path):
                import zipfile
                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                    zip_ref.extractall(local_folder_path)
                os.remove(zip_file_path)

                if is_update:
                    self.update_message.emit("RDF_Features folder updated successfully!")
                else:
                    self.update_message.emit("RDF_Features folder downloaded successfully!")
            else:
                self.error_message.emit(f"Failed to find the downloaded zip file.")
        except Exception as e:
            self.error_message.emit(f"An error occurred: {e}")

class DownloadDailog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Updating...')
        self.setFixedSize(300, 100)
        
        self.layout = QVBoxLayout()
        self.label = QLabel("Downloading...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()
