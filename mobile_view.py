import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QSlider, QPushButton, QApplication
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt,QSize
from PyQt6.QtGui import QIcon
from urllib.parse import quote


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
        self.back_button.setToolTip("back")
        self.back_button.setIconSize(QSize(icon_size, icon_size))
        self.back_button.setFixedSize(icon_size + 10, icon_size + 10)
        self.back_button.setStyleSheet("border: none;")
        self.back_button.setToolTip("back")
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
        self.forward_button.setToolTip("reload")
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

        # Create the zoom slider
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setStyleSheet("border: none;")
        self.zoom_slider.setMinimum(1)
        self.zoom_slider.setMaximum(500)
        self.zoom_slider.setValue(250)  # Initial zoom level
        self.zoom_slider.valueChanged.connect(self.zoom_changed)

        # Add the zoom slider to the main layout
        self.layout.addWidget(self.zoom_slider)

        self.set_border_color(None)

        self.web_view.page().profile().downloadRequested.connect(self.handle_download)

    def set_border_color(self, color):
        if color:
            self.setStyleSheet(f"border: 2px solid {color};")
        else:
            self.setStyleSheet("border: none;")

    def zoom_changed(self, value):
        # Set zoom level in percentage (100% is default)
        self.web_view.setZoomFactor(value / 500.0)

    def load_file_preview(self, file_path):
        try:
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

            url = QUrl.fromUserInput(preview_url)
            print(url)
            self.web_view.load(url)
        except Exception as e:
            print(f"Failed to load preview: {e}")
            self.web_view.setHtml("<html><body><h1>Failed to load preview</h1></body></html>")

    def clear_view(self):
        # Load a blank page
        self.web_view.setHtml("<html><body></body></html>")

    def handle_download(self, download):
        try:
            # Choose the default directory and file path
            default_path = os.path.join(os.path.expanduser('~'), 'Downloads', download.downloadFileName())

            # Show a file dialog to let the user choose the location
            file_path, _ = QFileDialog.getSaveFileName(self, "Save File", default_path)

            if file_path:
                download.setPath(file_path)
                download.accept()
        except Exception as e:
            print(f"Failed to handle download")

    def web_view_back(self):
        if self.web_view.history().canGoBack():
            self.web_view.back()

    def web_view_forward(self):
        if self.web_view.history().canGoForward():
            self.web_view.forward()

    def web_view_reload(self):
        self.web_view.reload()
