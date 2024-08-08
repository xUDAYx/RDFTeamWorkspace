import sys
from PyQt6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QLabel, QPushButton,
    QTreeView, QMessageBox, QWidget, QHBoxLayout
)
from PyQt6.QtGui import QFileSystemModel
from PyQt6.QtCore import QDir, QModelIndex,pyqtSignal
import os
from project_view import ProjectView


class OpenProjectWizard(QWizard):
    project_opened = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Open Project Wizard")

        self.rdf_project_root = "C:/xampp/htdocs/RDFProjects_ROOT"
        self.project_view = ProjectView()
        if not os.path.exists(self.rdf_project_root):
            QMessageBox.critical(None, "Error", "RDFProject_Root folder does not exist.")
            sys.exit(1)

        self.intro_page = QWizardPage()
        self.intro_page.setTitle("Open Project")
        self.intro_layout = QVBoxLayout(self.intro_page)

        # Heading label for the main root folder
        self.heading_label = QLabel(f"Folder for RDFProject_Root")
        self.heading_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.intro_layout.addWidget(self.heading_label)

        # Create a horizontal layout for title and folder info
        self.info_layout = QHBoxLayout()
        self.intro_layout.addLayout(self.info_layout)

        # Title label
        self.intro_label = QLabel("Select a folder from the list below.")
        self.info_layout.addWidget(self.intro_label)
        
        # Folder info label
        self.folder_info = QLabel("No folder selected")
        self.info_layout.addStretch()  # Push the folder info label to the right
        self.info_layout.addWidget(self.folder_info)

        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(self.rdf_project_root))
        self.tree_view.clicked.connect(self.on_folder_clicked)

        # Hide the "Size" and "Type" columns
        self.tree_view.header().hideSection(2)  # Hide the Size column
        self.tree_view.header().hideSection(1)  # Hide the Type column

        self.intro_layout.addWidget(self.tree_view)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.intro_layout.addWidget(self.select_button)

        self.addPage(self.intro_page)
        self.selected_folder = None
        self.selected_folder_path = None

    def on_folder_clicked(self, index: QModelIndex):
        self.selected_folder_path = self.model.filePath(index)
        self.selected_folder = self.selected_folder_path
        # Update the folder info label
        folder_name = os.path.basename(self.selected_folder_path)
        self.folder_info.setText(f"{folder_name} ({self.selected_folder_path})")

    def select_folder(self):
        if self.selected_folder:
            self.project_opened.emit(self.selected_folder)
            self.accept()  # Accept and close the wizard
        else:
            QMessageBox.warning(self, "No Folder Selected", "Please select a folder from the list.")
   
if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = OpenProjectWizard()
    wizard.show()
    sys.exit(app.exec())

    
