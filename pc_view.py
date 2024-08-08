import os
import json
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, 
    QPushButton, QApplication, QMessageBox, QInputDialog, QTreeWidget, QDialog, QTreeWidgetItem, QLineEdit, QRadioButton, QButtonGroup
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QSize, QPoint
from PyQt6.QtGui import QIcon, QGuiApplication
from urllib.parse import quote
from PyQt6.QtWebEngineCore import QWebEnginePage



class PCView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create a container widget for the web view
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_widget.setLayout(self.container_layout)
        
        self.web_view = QWebEngineView()
        self.container_layout.addWidget(self.web_view)
        
        # Add the container widget to the main layout
        self.layout.addWidget(self.container_widget)

        self.set_border_color(None)
        self.web_view.page().profile().downloadRequested.connect(self.handle_download)

        # Add port input and radio buttons
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("80")
        
        self.local_radio = QRadioButton("Local")
        self.server_radio = QRadioButton("Server")
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.local_radio)
        self.button_group.addButton(self.server_radio)
        self.local_radio.setChecked(True)

        # self.local_radio.toggled.connect(self.reload_preview)
        # self.server_radio.toggled.connect(self.reload_preview)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_input)
        port_layout.addWidget(self.local_radio)
        port_layout.addWidget(self.server_radio)
        self.layout.addLayout(port_layout)

        # Add tree widget for JSON view
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.hide()
        self.layout.addWidget(self.tree_widget)

        # Add toggle PC view button
        self.toggle_pc_view_button = QPushButton("Toggle Mobile View")
        self.toggle_pc_view_button.clicked.connect(self.toggle_pc_view)
        self.layout.addWidget(self.toggle_pc_view_button)

    def set_border_color(self, color):
        if color:
            self.setStyleSheet(f"border: 2px solid {color};")
        else:
            self.setStyleSheet("border: none;")

    

    def load_file_preview(self, file_path):
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.json':
                self.show_json_in_tree_view(file_path)
            elif file_extension == '.php' and file_path.endswith('UI.php'):
                file_name = os.path.splitext(os.path.basename(file_path))[0]
                project_path = os.path.dirname(file_path)
                htdocs_index = project_path.lower().find('htdocs')

                if htdocs_index == -1:
                    raise ValueError("Project is not located under htdocs directory")

                relative_path = project_path[htdocs_index + len('htdocs') + 1:]
                relative_path_parts = relative_path.split(os.sep)
                project_folder = relative_path_parts[0]
                project_path_up_to_folder = os.path.join(project_folder)

                port = self.port_input.text() or "80"
                is_local = self.local_radio.isChecked()

                if is_local:
                    preview_url = f"http://localhost:{port}/{quote(project_path_up_to_folder.replace(os.sep, '/'))}/RDFView.php?ui={file_name}"
                else:
                    preview_url = f"https://takeitideas.in/software/RDFMicroProjects/reminderApp/RDFView.php?ui=reminderAppUI={file_name}"

                url = QUrl.fromUserInput(preview_url)
                print(url)
                self.web_view.load(url)
                self.tree_widget.clear()
                self.tree_widget.hide()
                self.web_view.show()
        except Exception as e:
            print(f"Failed to load preview: {e}")
            self.web_view.setHtml("<html><body><h1>Failed to load preview</h1></body></html>")
    
    def show_json_in_tree_view(self, file_path):
        try:
            with open(file_path, 'r') as json_file:
                json_data = json.load(json_file)
                self.populate_tree_widget(json_data)
                self.web_view.setHtml("<html><body></body></html>")
                self.web_view.hide()
                self.tree_widget.show()
        except Exception as e:
            print(f"Error loading JSON file: {e}")
            logging.error(f"Error loading JSON file: {e}")

    def populate_tree_widget(self, data, parent_item=None):
        if parent_item is None:
            self.tree_widget.clear()
            parent_item = self.tree_widget.invisibleRootItem()

        if isinstance(data, dict):
            for key, value in data.items():
                item = QTreeWidgetItem(parent_item, [key])
                self.populate_tree_widget(value, item)
        elif isinstance(data, list):
            for i, value in enumerate(data):
                item = QTreeWidgetItem(parent_item, [f"Item {i}"])
                self.populate_tree_widget(value, item)
        else:
            item = QTreeWidgetItem(parent_item, [str(data)])

    def clear_view(self):
        self.web_view.setHtml("<html><body></body></html>")
        self.tree_widget.clear()

    def handle_download(self, download):
        try:
            default_path = os.path.join(os.path.expanduser('~'), download.path().split('/')[-1])
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)
            if file_path:
                download.setPath(file_path)
                download.accept()
        except Exception as e:
            print(f"Error handling download: {e}")

    def toggle_pc_view(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, 'toggle_pc_view'):
                parent.toggle_pc_view()
                break
            parent = parent.parent()