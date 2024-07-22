import os
import json
import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QPushButton, 
    QApplication, QMessageBox, QInputDialog, QTreeWidget, QDialog, QTreeWidgetItem
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt, QSize, QPoint
from PyQt6.QtGui import QIcon
from urllib.parse import quote
from PyQt6.QtWebEngineCore import QWebEnginePage

class CustomDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Message")
        self.setModal(True)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
        # Message label
        self.label = QLabel(message)
        self.layout.addWidget(self.label)
        
        # OK button
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        
        self.setFixedSize(250, 100)
        
        # Position the dialog slightly to the right from the left edge and slightly to the left from the right edge of the screen
        screen_rect = QApplication.primaryScreen().availableGeometry()
        dialog_rect = self.geometry()
        x = int(screen_rect.left() + 20)  # Shift 20 pixels to the right from the left edge
        x = int(screen_rect.right() - dialog_rect.width() - 50)  # Shift 20 pixels to the left from the right edge
        y = int(screen_rect.top() + (screen_rect.height() - dialog_rect.height()) / 2)
        self.move(QPoint(x, y))

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def javaScriptAlert(self, frame, msg):
        dialog = CustomDialog(msg)
        dialog.exec()

    def javaScriptConfirm(self, frame, msg):
        reply = QMessageBox.question(None, "JavaScript Confirm", msg, 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes

    def javaScriptPrompt(self, frame, msg, default_value):
        text, ok = QInputDialog.getText(None, "JavaScript Prompt", msg, text=default_value)
        return text if ok else None

class MobileView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Create a container widget for the web view
        self.container_widget = QWidget()
        self.container_widget.setFixedWidth(300)

        # Get available screen height
        available_height = QApplication.primaryScreen().availableGeometry().height()

        # Set height based on available screen height
        self.container_widget.setFixedHeight(min(max(400, available_height - 100), 600))

        self.container_widget.setStyleSheet("""
            QWidget {
                border: 10px solid black;
                border-radius: 20px;
                background-color: white;
            }
        """)
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(0)
        self.container_widget.setLayout(self.container_layout)

        # Add navigation buttons
        self.navigation_layout = QHBoxLayout()
        self.navigation_layout.setSpacing(0)

        icon_size = 25  # Define the icon size

        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("images/back_button.png"))
        self.back_button.setToolTip("Back")
        self.back_button.setIconSize(QSize(icon_size, icon_size))
        self.back_button.setFixedSize(icon_size + 10, icon_size + 10)
        self.back_button.setStyleSheet("border: none;")
        self.back_button.clicked.connect(self.web_view_back)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon("images/forward_button.png"))
        self.forward_button.setIconSize(QSize(icon_size, icon_size))
        self.forward_button.setFixedSize(icon_size + 10, icon_size + 10)
        self.forward_button.setStyleSheet("border: none;")
        self.forward_button.setToolTip("Forward")
        self.forward_button.clicked.connect(self.web_view_forward)

        self.reload_button = QPushButton()
        self.reload_button.setIcon(QIcon("images/reload.png"))
        self.reload_button.setIconSize(QSize(icon_size, icon_size))
        self.reload_button.setFixedSize(icon_size + 10, icon_size + 10)
        self.reload_button.setStyleSheet("border: none;")
        self.reload_button.setToolTip("Reload")
        self.reload_button.clicked.connect(self.web_view_reload)

        self.navigation_layout.addWidget(self.back_button)
        self.navigation_layout.addWidget(self.forward_button)
        self.navigation_layout.addWidget(self.reload_button)
        self.navigation_layout.addStretch(1)  # Add stretchable space to align buttons to the left

        self.layout.addLayout(self.navigation_layout)

        # Create the mobile header
        self.mobile_header = QWidget()
        self.mobile_header.setFixedHeight(20)
        self.mobile_header.setStyleSheet("background-color: lightgrey; border:lightgrey; border-top-left-radius: 16px; border-top-right-radius: 16px;")

        # Create the camera circle
        self.camera_circle = QLabel()
        self.camera_circle.setFixedSize(10, 10)
        self.camera_circle.setStyleSheet("""
            QLabel {
                margin: 0;
                border: 1px solid black;
                background-color: black;
                border-radius: 5px;
            }
        """)
        # Create the notch
        self.notch = QWidget()
        self.notch.setFixedSize(100, 20)
        self.notch.setStyleSheet("""
            QWidget {
                background-color: black;
            }
        """)

        self.mobile_header_layout = QHBoxLayout()
        self.mobile_header_layout.setContentsMargins(10, 0, 10, 0)
        self.mobile_header_layout.setSpacing(10)
        self.mobile_header_layout.addWidget(self.camera_circle, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.mobile_header_layout.addStretch(1)  # Add stretchable space to shift the notch to the left
        self.mobile_header_layout.addWidget(self.notch, alignment=Qt.AlignmentFlag.AlignVCenter)
        self.mobile_header_layout.addStretch(1)  # Add more stretchable space on the right
        self.mobile_header.setLayout(self.mobile_header_layout)
        # Add the mobile header and web view to the container layout
        self.container_layout.addWidget(self.mobile_header)
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("border: black;")
        self.container_layout.addWidget(self.web_view)

        # Add the container widget to the main layout
        self.layout.addWidget(self.container_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        # Set the custom page to handle JS dialogs
        self.web_view.setPage(CustomWebEnginePage(self.web_view))
        # Add the container widget to the main layout
        self.layout.addWidget(self.container_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        self.container_layout.addWidget(self.web_view)

        # Create the zoom buttons
        self.zoom_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.setMinimumHeight(20)
        self.zoom_in_button.setFixedWidth(40)
        self.zoom_in_button.setStyleSheet("background-color:lightblue;font-weight:bold;")
        self.zoom_in_button.setToolTip("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)

        self.zoom_out_button = QPushButton("-")
        self.zoom_out_button.setMinimumHeight(20)
        self.zoom_out_button.setFixedWidth(40)
        self.zoom_out_button.setToolTip("Zoom Out")
        self.zoom_out_button.setStyleSheet("background-color:lightblue;font-weight:bold;")
        self.zoom_out_button.clicked.connect(self.zoom_out)

        self.zoom_layout.addWidget(self.zoom_in_button)
        self.zoom_layout.addWidget(self.zoom_out_button)
        self.zoom_layout.addStretch()
        self.layout.addLayout(self.zoom_layout)

        # Create the JSON tree widget
        self.tree_widget = QTreeWidget()
        self.tree_widget.setStyleSheet("border:none;")
        self.container_layout.addWidget(self.tree_widget)
        self.tree_widget.hide()

        self.set_border_color(None)

        self.web_view.page().profile().downloadRequested.connect(self.handle_download)

    def set_border_color(self, color):
        if color:
            self.setStyleSheet(f"border: 2px solid {color};")
        else:
            self.setStyleSheet("border: none;")

    def zoom_in(self):
        # Set zoom level in percentage (100% is default)
        self.web_view.setZoomFactor(self.web_view.zoomFactor() + 0.1)

    def zoom_out(self):
        # Set zoom level in percentage (100% is default)
        self.web_view.setZoomFactor(self.web_view.zoomFactor() - 0.1)

    def load_file_preview(self, file_path):
        try:
            # Get the file extension
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.json':
                self.show_json_in_tree_view(file_path)
            elif file_extension == '.php' and file_path.endswith('UI.php'):
                # Get the file name without the extension
                file_name = os.path.splitext(os.path.basename(file_path))[0]

                # Get the project directory structure
                project_path = os.path.dirname(file_path)
                htdocs_index = project_path.lower().find('htdocs')

                if htdocs_index == -1:
                    raise ValueError("Project is not located under htdocs directory")

                # Extract the relative path up to the project folder
                relative_path = project_path[htdocs_index + len('htdocs') + 1:]
                relative_path_parts = relative_path.split(os.sep)

                # Determine the project folder name (assuming it is the first folder in the relative path)
                project_folder = relative_path_parts[0]
                project_path_up_to_folder = os.path.join(project_folder)

                # Construct the preview URL
                preview_url = f"http://localhost/{quote(project_path_up_to_folder.replace(os.sep, '/'))}/RDFView.php?ui={file_name}"

                # Load the URL in the web view
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
                self.web_view.setHtml("<html><body></body></html>")  # Clear the web view
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
        # Load a blank page
        self.web_view.setHtml("<html><body></body></html>")
        self.tree_widget.clear()

    def handle_download(self, download):
        try:
            # Choose the default directory and file path
            default_path = os.path.join(os.path.expanduser('~'), download.path().split('/')[-1])

            # Display the save file dialog
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)

            # If the user cancels the dialog, file_path will be empty
            if file_path:
                # Set the path where the file will be saved
                download.setPath(file_path)

                # Accept the download request
                download.accept()
        except Exception as e:
            print(f"Error handling download: {e}")

    def web_view_back(self):
        self.web_view.back()

    def web_view_forward(self):
        self.web_view.forward()

    def web_view_reload(self):
        self.web_view.reload()

if __name__ == '__main__':
    app = QApplication([])
    view = MobileView()
    view.show()
    app.exec()
