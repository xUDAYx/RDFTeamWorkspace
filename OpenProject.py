import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, QPushButton,
    QMessageBox, QHBoxLayout, QListWidget, QLineEdit
)
from PyQt6.QtCore import pyqtSignal

class OpenProjectWizard(QWizard):
    project_opened = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Open Project Wizard")
        self.setFixedSize(300, 400)

        self.rdf_project_root = "C:/xampp/htdocs/RDFProjects_ROOT"
        if not os.path.exists(self.rdf_project_root):
            QMessageBox.critical(None, "Error", "RDFProjects_ROOT folder does not exist.")
            sys.exit(1)

        self.intro_page = QWizardPage()
        self.intro_layout = QVBoxLayout(self.intro_page)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search projects...")
        self.search_field.textChanged.connect(self.filter_projects)
        self.intro_layout.addWidget(self.search_field)

        self.project_list = QListWidget()
        self.intro_layout.addWidget(self.project_list)

        # Populate the list with folder names
        self.load_projects()

        # Connect item click and double-click events
        self.project_list.itemClicked.connect(self.open_project)
        self.project_list.itemDoubleClicked.connect(self.select_folder)

        self.select_button = QPushButton("Open Project")
        self.select_button.setStyleSheet("background-color:#6495ED; color: white;")
        self.select_button.clicked.connect(self.select_folder)
        self.intro_layout.addWidget(self.select_button)

        self.addPage(self.intro_page)
        self.selected_folder = None
        self.selected_folder_path = None

        self.setButtonLayout([
            QWizard.WizardButton.Stretch,
            QWizard.WizardButton.BackButton,
            QWizard.WizardButton.NextButton,
            QWizard.WizardButton.CancelButton,
        ])

    def load_projects(self):
        try:
            projects = [f for f in os.listdir(self.rdf_project_root) if os.path.isdir(os.path.join(self.rdf_project_root, f))]
            if projects:
                self.project_list.addItems(projects)
            else:
                self.project_list.addItem("No projects found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading projects: {str(e)}")

    def filter_projects(self):
        search_term = self.search_field.text().lower()
        for index in range(self.project_list.count()):
            item = self.project_list.item(index)
            item.setHidden(search_term not in item.text().lower())

    def open_project(self, item):
        project_name = item.text()
        self.selected_folder_path = os.path.join(self.rdf_project_root, project_name)
        self.selected_folder = self.selected_folder_path

    def select_folder(self):
        if self.selected_folder:
            if not os.path.isdir(self.selected_folder):
                QMessageBox.warning(self, "Invalid Selection", "The selected folder is not valid.")
                return
            self.project_opened.emit(self.selected_folder)
            self.accept()  # Accept and close the wizard
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder from the list.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = OpenProjectWizard()
    wizard.show()
    sys.exit(app.exec())

