import sys
import os,json

import shutil
from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, QPushButton, QLabel, QLineEdit,
                             QFileDialog, QMessageBox,QWidget, QComboBox, QHBoxLayout)
from PyQt6.QtCore import pyqtSignal, Qt, QEvent,QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView
from project_view import ProjectView

class NewProjectWizard(QWizard):
    project_created = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle('New Project Wizard')
        self.setGeometry(100, 100, 800, 600)

        # Create the mobile view widget
        self.mobile_view = QWebEngineView()
        self.mobile_view.setFixedSize(300, 400)

        # Create pages
        self.create_intro_page()
        self.create_copy_sample_page()
        self.create_new_project_page()

        # Add pages to wizard
        self.addPage(self.intro_page)
        self.addPage(self.copy_sample_page)
        self.addPage(self.new_project_page)

        # Hide the default Next and Back buttons
        self.setButtonLayout([QWizard.WizardButton.BackButton, QWizard.WizardButton.CancelButton])

 

        self.setStyleSheet("""
            QWizard {
                background-color: #f2f2f2;
            }
            QWizardPage {
                background-color: #ffffff;
                border: 1px solid #dcdcdc;
                border-radius: 10px;
                padding: 20px;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit, QComboBox, QPushButton {
                font-size: 14px;
                padding: 5px;
            }
        """)

        self.project_view = ProjectView()

    def create_intro_page(self):
        self.intro_page = QWizardPage()
        self.intro_page.setTitle("Setup New Project")
        self.intro_page.setSubTitle("Choose whether to copy a sample project or create a new one from scratch.")

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.copy_sample_button = QPushButton("Copy a Sample Project")
        self.copy_sample_button.setStyleSheet("""
            QPushButton {
                background-color: #6200EE;
                color: white;
                border: none;
                padding: 15px 30px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px;
                border-radius: 12px;
                transition: background-color 0.3s, transform 0.3s;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            QPushButton:hover {
                background-color: #3700B3;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #03DAC6;
                transform: scale(1.02);
            }""")
        self.create_new_button = QPushButton("Create New Project")
        self.create_new_button.setStyleSheet("""
            QPushButton {
                background-color: #6200EE;
                color: white;
                border: none;
                padding: 15px 30px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px;
                border-radius: 12px;
                transition: background-color 0.3s, transform 0.3s;
                box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19);
            }
            QPushButton:hover {
                background-color: #3700B3;
                transform: scale(1.05);
            }
            QPushButton:pressed {
                background-color: #03DAC6;
                transform: scale(1.02);
            }""")
        self.copy_sample_button.setToolTip("Copy a predefined sample project to a new location.")
        self.create_new_button.setToolTip("Create a new project with a blank structure.")

        button_layout.addWidget(self.copy_sample_button)
        button_layout.addWidget(self.create_new_button)

        # Add stretch to push buttons to the top 
        layout.addLayout(button_layout)
        self.intro_page.setLayout(layout)

        self.copy_sample_button.clicked.connect(self.goto_copy_sample_page)
        self.create_new_button.clicked.connect(self.goto_new_project_page)

    def create_copy_sample_page(self):
        self.copy_sample_page = QWizardPage()
        self.copy_sample_page.setTitle("Copy Sample Project")
        self.copy_sample_page.setSubTitle("Provide details for copying a sample project.")

        layout = QVBoxLayout()

        self.sample_project_label = QLabel("Select a sample project:")
        self.sample_project_combo = QComboBox()
        self.sample_project_combo.addItem("-- Select Sample Project --")
        self.sample_project_combo.addItems(self.get_sample_projects())
        self.sample_project_combo.setCurrentIndex(0) 

        self.copy_project_name_label = QLabel("Enter Project Name:")
        self.copy_project_name_input = QLineEdit()

        self.ui_file_label = QLabel("See UI files in project:")
        self.ui_file_combo = QComboBox()
        self.ui_file_combo.addItem("-- Select UI File --")

        self.copy_project_button = QPushButton("Copy Project")

        layout.addWidget(self.sample_project_label)
        layout.addWidget(self.sample_project_combo)
        layout.addWidget(self.ui_file_label)
        layout.addWidget(self.ui_file_combo)
        layout.addWidget(self.copy_project_name_label)
        layout.addWidget(self.copy_project_name_input)
        layout.addWidget(self.copy_project_button)

        self.copy_project_button.setEnabled(False)

        # Stylesheet for QPushButton
        self.copy_project_button.setStyleSheet("""
            QPushButton {
                background-color: #6200EE;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: white;
                color: black;
                border: 2px solid #6200EE;
            }
        """)

        # Stylesheet for QLineEdit and QComboBox
        self.copy_project_name_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #6200EE;
                border-radius: 4px;
            }
        """)
        self.sample_project_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #6200EE;
                border-radius: 4px;
                padding: 5px;
                background-color: #f0f0f0;
                min-width: 150px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #6200EE;
                border-left-style: solid;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
                background-color: #f0f0f0;
            }
            QComboBox QAbstractItemView {
                border: 2px solid #6200EE;
                selection-background-color: #d1d1d1;
            }
        """)

        # Create a QWidget for mobile view with a solid black border
        self.mobile_view_widget = QWidget()
        self.mobile_view_widget.setStyleSheet("""
            QWidget {
                border-radius:4px;
                border: 2px solid black;
            }
        """)

        mobile_layout = QVBoxLayout()
        mobile_layout.addWidget(self.mobile_view)
        self.mobile_view_widget.setLayout(mobile_layout)

        # Horizontal layout to include mobile view
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addLayout(layout)
        horizontal_layout.addWidget(self.mobile_view_widget)

        self.copy_sample_page.setLayout(horizontal_layout)

        self.sample_project_combo.currentIndexChanged.connect(self.update_ui_file_combo)
        self.ui_file_combo.currentIndexChanged.connect(self.update_mobile_view_with_ui_file)
        self.copy_project_name_input.textChanged.connect(self.check_copy_form_complete)
        self.copy_project_button.clicked.connect(self.copy_sample_project)

    def create_new_project_page(self):
        self.new_project_page = QWizardPage()
        self.new_project_page.setTitle("Create New Project")
        self.new_project_page.setSubTitle("Provide details for creating a new project.")

        layout = QVBoxLayout()

        self.project_name_label = QLabel("Enter Project Name:")
        self.project_name_input = QLineEdit()


        self.create_project_button = QPushButton("Create Project")

        layout.addWidget(self.project_name_label)
        layout.addWidget(self.project_name_input)
        layout.addWidget(self.create_project_button)

        self.create_project_button.setEnabled(False)

        # Stylesheet for QPushButton
        self.create_project_button.setStyleSheet("""
            QPushButton {
                background-color: #6200EE;
                color: white;
                border: none;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 4px 2px;
                transition-duration: 0.4s;
                cursor: pointer;
            }
            QPushButton:hover {
                background-color: white;
                color: black;
                border: 2px solid #6200EE;
            }
        """)

        # Stylesheet for QLineEdit and QComboBox
        self.project_name_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #6200EE;
                border-radius: 4px;
            }
        """)

        self.new_project_page.setLayout(layout)

        self.project_name_input.textChanged.connect(self.check_new_form_complete)
        self.create_project_button.clicked.connect(self.create_new_project)

    def goto_copy_sample_page(self):
        self.setCurrentId(1)
        self.update_sample_projects()

    def goto_new_project_page(self):
        self.setCurrentId(2)

    def handle_cancel(self):
        reply = QMessageBox.question(self, 'Cancel', 'Are you sure you want to cancel?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.accept()
        else:
            self.ignore()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Cancel', 'Are you sure you want to cancel?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()

    def get_sample_projects(self):
        sample_dir = r'D:\RDF_STUDIO\project_templates'
        if os.path.exists(sample_dir):
            return [name for name in os.listdir(sample_dir) if os.path.isdir(os.path.join(sample_dir, name))]
        return []

    def update_sample_projects(self):
        self.sample_project_combo.clear()  # Clear existing items
        self.sample_project_combo.addItem("-- Select Sample Project --")
        self.sample_project_combo.addItems(self.get_sample_projects())

    def update_ui_file_combo(self, index):
        if index > 0:
            project_name = self.sample_project_combo.itemText(index)
            project_path = os.path.join('project_templates', project_name,'RDF_UI')
            ui_files = [f for f in os.listdir(project_path) if f.endswith('UI.php')]

            self.ui_file_combo.clear()
            self.ui_file_combo.addItem("-- Select UI File --")
            self.ui_file_combo.addItems(ui_files)

            self.copy_project_button.setEnabled(True if ui_files else False)
        else:
            self.ui_file_combo.clear()
            self.ui_file_combo.addItem("-- Select UI File --")
            self.copy_project_button.setEnabled(False)

    def update_mobile_view_with_ui_file(self):
        try:
            selected_project = self.sample_project_combo.currentText().strip()
            selected_ui_file = self.ui_file_combo.currentText().strip()

            if selected_project == "-- Select Sample Project --" or selected_ui_file == "-- Select UI File --":
                self.mobile_view.setHtml("<html><body><p>No content available</p></body></html>")
                return

            # Construct the UI file path
            project_templates_dir = os.path.join(os.path.dirname(__file__), 'project_templates')
            ui_file_path = os.path.join(project_templates_dir, selected_project, "RDF_UI", selected_ui_file)

            # Check if the directory exists before attempting to access the file
            if os.path.exists(os.path.dirname(ui_file_path)):
                with open(ui_file_path, 'r', encoding='utf-8') as ui_file:
                    html_content = ui_file.read()
                self.mobile_view.setHtml(html_content)
            else:
                self.mobile_view.setHtml("<html><body><p>No content available</p></body></html>")

        except Exception as e:
            print(f"An error occurred while updating the mobile view: {e}")
            
    def reset_wizard(self):
        self.sample_project_combo.setCurrentId(0)
        self.copy_project_name_input.clear()
        self.project_name_input.clear()
        self.mobile_view.setHtml("<html><body><p>No content available</p></body></html>")


    def check_copy_form_complete(self):
        project_name = self.copy_project_name_input.text().strip()
        is_complete = bool(project_name and self.sample_project_combo.currentIndex() > 0 and self.ui_file_combo.currentIndex() > 0)
        self.copy_project_button.setEnabled(is_complete)

    def copy_sample_project(self):
        try:
            sample_project_name = self.sample_project_combo.currentText()
            new_project_name = self.copy_project_name_input.text().strip()

            if not sample_project_name or not new_project_name:
                QMessageBox.warning(self, "Input Error", "Please select a sample project and enter a project name.")
                return

            sample_project_dir = os.path.join('project_templates', sample_project_name)
            new_project_dir = os.path.join('C:\\xampp\\htdocs', new_project_name)

            if os.path.exists(new_project_dir):
                QMessageBox.critical(self, "Error", "A project with this name already exists!")
                return

            shutil.copytree(sample_project_dir, new_project_dir)
            self.project_created.emit(new_project_name)
            QMessageBox.information(self, "Success", "Project copied successfully!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while copying the project: {str(e)}")

    def get_ui_templates(self):
        template_dir = 'ui_templates'
        if os.path.exists(template_dir):
            return [name for name in os.listdir(template_dir) if os.path.isfile(os.path.join(template_dir, name))]
        return []

    def check_new_form_complete(self):
        project_name = self.project_name_input.text().strip()
        is_complete = bool(project_name)
        self.create_project_button.setEnabled(is_complete)

    def create_new_project(self):
        try:
            destination_dir = r'C:\xampp\htdocs'
            project_name = self.project_name_input.text()

            if not destination_dir or not project_name:
                QMessageBox.warning(self, "Incomplete Form", "Please complete all fields.")
                return

            dest_dir = os.path.join(destination_dir, project_name)

            if os.path.exists(dest_dir):
                QMessageBox.warning(self, "Project Exists", "A project with this name already exists in the selected directory.")
                return

            os.makedirs(dest_dir)

            # Create initial project structure
            os.makedirs(os.path.join(dest_dir, "RDF_UI"))
            os.makedirs(os.path.join(dest_dir, "RDF_ACTION"))
            os.makedirs(os.path.join(dest_dir, "RDF_BW"))
            os.makedirs(os.path.join(dest_dir, "RDF_BVO"))
            os.makedirs(os.path.join(dest_dir, "RDF_DATA"))

            # Create a default ProjectInfo.json file
            project_info = {
                "init": ""
            }

            with open(os.path.join(dest_dir, "ProjectInfo.json"), 'w') as file:
                json.dump(project_info, file, indent=4)

            self.project_created.emit(dest_dir)
            QMessageBox.information(self, "Success", "New project created successfully.")
            self.project_view.populate_tables(dest_dir)
            self.reset_wizard()
            self.close()
        except Exception as e:
            print(f"An error occurred while creating the new project: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred while creating the new project: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    wizard = NewProjectWizard()
    wizard.show()
    sys.exit(app.exec())
