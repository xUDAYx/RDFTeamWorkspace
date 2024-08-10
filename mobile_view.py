import os
import json
import logging
import webbrowser,subprocess
from PIL import Image
import qrcode
from io import BytesIO
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, QSlider, QDialogButtonBox,
    QPushButton, QApplication, QMessageBox, QInputDialog, QTreeWidget, QDialog, QTreeWidgetItem, QLineEdit, QRadioButton, QButtonGroup, QAbstractItemView,QTreeView
)
from PyQt6.QtWebEngineWidgets import QWebEngineView  # type: ignore
from PyQt6.QtCore import QUrl, Qt, QSize, QPoint, QThread, pyqtSignal,QRegularExpression,  QSortFilterProxyModel,QModelIndex
from PyQt6.QtGui import QIcon,QGuiApplication,QPixmap, QImage,QStandardItemModel, QStandardItem
from urllib.parse import quote
from PyQt6.QtWebEngineCore import QWebEnginePage 
from workers import QRCodeWorker, ClipboardWorker


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
        try:
            super().__init__(parent)
            self.layout = QVBoxLayout()
            self.setLayout(self.layout)

            # Create a container widget for the web view
            self.container_widget = QWidget()
            self.container_widget.setFixedWidth(300)

            screen = QGuiApplication.primaryScreen().availableGeometry()
            screen_height = screen.height()

            container_height = int(screen_height * 0.7)
            self.container_widget.setFixedHeight(container_height)

            self.container_widget.setStyleSheet("""
                QWidget { 
                
                    border: 5px solid #333333;
                    border-radius: 20px;
                    background-color: white;
                    padding: 10px;
                }
            """)
            self.container_layout = QVBoxLayout()
            self.container_layout.setSpacing(0)
            self.container_widget.setLayout(self.container_layout)

            # Add navigation buttons
            self.navigation_layout = QHBoxLayout()
            self.navigation_layout.setSpacing(0)

            port_radio_layout = QHBoxLayout()

            self.port_input = QLineEdit()
            self.port_label = QLabel("Enter your port number:")
            self.port_input.setPlaceholderText("80")
            self.port_input.setFixedWidth(50)
            port_radio_layout.addWidget(self.port_label)
            port_radio_layout.addWidget(self.port_input)

            # Add local/server toggle
            self.local_radio = QRadioButton("Local")

            self.server_radio = QRadioButton("Server")
    
            self.button_group = QButtonGroup()
            self.button_group.addButton(self.local_radio)
            self.button_group.addButton(self.server_radio)
            self.local_radio.setChecked(True)

            self.local_radio.toggled.connect(self.reload_preview)
            self.server_radio.toggled.connect(self.reload_preview)

            port_radio_layout.addStretch()
            port_radio_layout.addWidget(self.local_radio)
            port_radio_layout.addWidget(self.server_radio)

            self.layout.addLayout(port_radio_layout)

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

            self.bookmark_button = QPushButton("Bookmarks")
            self.bookmark_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196f3;
                        color: white;
                    
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        margin-left: 2px;
                        margin-right: 2px;
                    }
                """)        
            self.QR_button = QPushButton("QR Code")
            self.QR_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196f3;
                        color: white;
                    
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        margin-left: 2px;
                        margin-right: 2px;
                    }
                """)
            self.QR_button.clicked.connect(self.show_qr_code)
        
            self.copy_url_button = QPushButton("Copy URL")
            self.copy_url_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196f3;
                        color: white;
                    
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        margin-left: 2px;
                        margin-right: 2px;
                    }
                """)
            self.copy_url_button.clicked.connect(self.copy_url_to_clipboard)

            self.navigation_layout.addWidget(self.back_button)
            self.navigation_layout.addWidget(self.forward_button)
            self.navigation_layout.addWidget(self.reload_button)
            self.navigation_layout.addWidget(self.bookmark_button)
            self.navigation_layout.addWidget(self.QR_button)
            self.navigation_layout.addWidget(self.copy_url_button)
            self.navigation_layout.addStretch(1)  
        
            # Add stretchable space to align buttons to the left

            self.layout.addLayout(self.navigation_layout)

            # Add previewed URL display
            self.url_layout = QHBoxLayout()
            self.url_label = QLabel("Previewed URL:")
            self.url_label.setStyleSheet("color: #333;")
            self.url_display = QLineEdit()
            self.url_display.setFixedHeight(25)
            self.url_display.setReadOnly(True)
            self.url_display.setStyleSheet("""
                QLineEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px 5px;
                    font-size: 14px;
                }
            """)
            self.open_in_browser_button = QPushButton("Open in browser")
            self.open_in_browser_button.setStyleSheet("""
                    QPushButton {
                        background-color: #2196f3;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px;
                        margin-left: 2px;
                        margin-right: 2px;
                    }
                """)
            self.open_in_browser_button.clicked.connect(self.open_in_browser)


            self.url_layout.addWidget(self.url_label)
            self.url_layout.addWidget(self.url_display)
            self.url_layout.addWidget(self.open_in_browser_button)
            self.layout.addLayout(self.url_layout)

            # Create the mobile header
            self.mobile_header = QWidget()
            self.mobile_header.setFixedHeight(40)
            self.mobile_header.setStyleSheet("""
                background-color: #e5e5e5;
                border: none;
                    """)
            # Create the camera circle
            self.camera_circle = QLabel()
            self.camera_circle.setFixedSize(12, 12)
            self.camera_circle.setStyleSheet("""
                QLabel {
                    margin: 0;
                    border: none;
                    background-color: #333;
                    border-radius: 6px;
                }
            """)

            # Create the notch
            self.notch = QWidget()
            self.notch.setFixedSize(120, 15)
            self.notch.setStyleSheet("""
                QWidget {
                    background-color: #333;
                    border-radius: 7px;
                }
            """)

            self.mobile_header_layout = QHBoxLayout()
            self.mobile_header_layout.setContentsMargins(15, 0, 15, 0)
            self.mobile_header_layout.setSpacing(15)
            self.mobile_header_layout.addWidget(self.camera_circle, alignment=Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.mobile_header_layout.addStretch(1)
            self.mobile_header_layout.addWidget(self.notch, alignment=Qt.AlignmentFlag.AlignVCenter)
            self.mobile_header_layout.addStretch(1)
            self.mobile_header.setLayout(self.mobile_header_layout)

            # Add the mobile header and web view to the container layout
            self.container_layout.addWidget(self.mobile_header)
            self.web_view = QWebEngineView()
            self.web_view.setStyleSheet("border: none; border-bottom-left-radius: 20px; border-bottom-right-radius: 20px;")
            self.container_layout.addWidget(self.web_view)

            # Add the container widget to the main layout
            self.layout.addWidget(self.container_widget, alignment=Qt.AlignmentFlag.AlignCenter)

            # Set the custom page to handle JS dialogs
            self.web_view.setPage(CustomWebEnginePage(self.web_view))

            # Create the zoom buttons
            self.zoom_layout = QHBoxLayout()
            self.zoom_in_button = QPushButton("+")
            self.zoom_in_button.setMinimumHeight(20)
            self.zoom_in_button.setFixedWidth(40)
            self.zoom_in_button.setStyleSheet("background-color:#f0f0f0;border-radius:5px;padding:4px 10px;border:1px solid #ccc;font-weight: bold;")
            self.zoom_in_button.setToolTip("Zoom In")
            self.zoom_in_button.clicked.connect(self.zoom_in)

            self.zoom_out_button = QPushButton("-")
            self.zoom_out_button.setMinimumHeight(20)
            self.zoom_out_button.setFixedWidth(40)
            self.zoom_out_button.setToolTip("Zoom Out")
            self.zoom_out_button.setStyleSheet("background-color:#f0f0f0;border-radius:5px;padding:4px 10px;border:1px solid #ccc;font-weight: bold;")
            self.zoom_out_button.clicked.connect(self.zoom_out)

            self.toggle_pc_view_button = QPushButton("Toggle PC View")
            self.toggle_pc_view_button.setMinimumHeight(20)
            self.toggle_pc_view_button.setStyleSheet("background-color: #2196f3; color: white; border: none; border-radius: 5px; padding: 5px; ")           
            self.toggle_pc_view_button.clicked.connect(self.toggle_pc_view)

        
            self.zoom_layout.addWidget(self.zoom_in_button)
            self.zoom_layout.addWidget(self.zoom_out_button)
            self.zoom_layout.addWidget(self.toggle_pc_view_button)
            self.zoom_layout.addStretch(1)
            # Add the zoom buttons to the main layout
            self.layout.addLayout(self.zoom_layout)
        
            # Add toggle PC view button
            self.tree_widget = QTreeWidget()
            self.tree_widget.setStyleSheet("border:none;")
            self.container_layout.addWidget(self.tree_widget)
            self.tree_widget.hide()

            self.set_border_color(None)

            self.web_view.page().profile().downloadRequested.connect(self.handle_download)
        except Exception as e:
            print(f"An error occurred during initialization: {str(e)}")

        

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

    def reload_preview(self):
        if self.current_file_path:
            self.load_file_preview(self.current_file_path)

    def load_file_preview(self, file_path):
        self.current_file_path = file_path
        try:
            file_extension = os.path.splitext(file_path)[1].lower()

            if file_extension == '.json':
                self.show_json_in_tree_view(file_path)
            elif file_extension == '.php' and file_path.endswith('UI.php'):
                project_path = os.path.dirname(file_path)
                htdocs_index = project_path.lower().find('htdocs')

                if htdocs_index == -1:
                    raise ValueError("Project is not located under htdocs directory")

                # Get the relative path after 'htdocs/RDFProjects_ROOT'
                relative_path = project_path[htdocs_index + len('htdocs/RDFProjects_ROOT') + 1:]
                # Get only the first folder after RDFProjects_ROOT (the immediate project folder)
                project_folder = relative_path.split(os.sep)[0]

                file_name = os.path.splitext(os.path.basename(file_path))[0]

                port = self.port_input.text() or "80"
                self.port_input.setPlaceholderText("80")
                is_local = self.local_radio.isChecked()

                if is_local:
                    preview_url = f"http://localhost:{port}/RDFProjects_ROOT/{project_folder}/RDFView.php?ui={file_name}"
                else:
                    preview_url = f"https://takeitideas.in/RDFProjects_ROOT/{project_folder}/RDFView.php?ui={file_name}"

                url = QUrl.fromUserInput(preview_url)
                self.url_display.setText(preview_url)  
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

         
    def toggle_pc_view(self):
        parent = self.parent()
        while parent:
            if hasattr(parent, 'toggle_pc_view'):
                parent.toggle_pc_view()
                break
            parent = parent.parent()

    def clear_url_display(self):
        self.url_display.clear()

    def show_qr_code(self):
        url = self.url_display.text()
        
        if not url:
            QMessageBox.warning(self, "No URL", "No URL available to generate QR code.")
            return
        
        self.qr_worker = QRCodeWorker(url)
        self.qr_worker.finished.connect(self.display_qr_code)
        self.qr_worker.error.connect(lambda e: QMessageBox.warning(self, "Error", f"Error generating QR code: {e}"))
        self.qr_worker.start()

    def display_qr_code(self, pixmap, url):
        dialog = QDialog(self)
        dialog.setWindowTitle("QR Code")
        layout = QVBoxLayout(dialog)
        label = QLabel(dialog)
        label.setPixmap(pixmap)
        layout.addWidget(label)

        url_label = QLabel(f"QR code for URL: {url}", dialog)
        url_label.setWordWrap(True)
        layout.addWidget(url_label)
            
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.exec()
    

    def copy_url_to_clipboard(self):
        url = self.url_display.text()
        
        if not url:
            QMessageBox.warning(self, "No URL", "No URL available to copy.")
            return

        self.clipboard_worker = ClipboardWorker(url)
        self.clipboard_worker.finished.connect(lambda msg: QMessageBox.information(self, "URL Copied", msg))
        self.clipboard_worker.error.connect(lambda e: QMessageBox.warning(self, "Copy Error", f"Error copying URL: {e}"))
        self.clipboard_worker.start()

    def open_in_browser(self):
        url = self.url_display.text()
        if url:
            self.browser_opener = BrowserOpener(url)
            self.browser_opener.finished.connect(self.handle_browser_opened)
            self.browser_opener.start()
        else:
            QMessageBox.warning(None, "No URL", "No URL to open in the browser. Please preview a file first.")

    def handle_browser_opened(self):
        self.browser_opener.finished.disconnect(self.handle_browser_opened)
        self.browser_opener = None

class BrowserOpener(QThread):
    finished = pyqtSignal()

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        chrome_path = self.find_chrome()
        if chrome_path:
            try:
                subprocess.run([chrome_path, self.url])
            except Exception as e:
                self.show_error_message(f"Could not open the URL in Chrome: {str(e)}")
        else:
            self.show_error_message("Could not find Chrome installation. Please ensure Chrome is installed.")
        self.finished.emit()

    def find_chrome(self):
        # Define potential Chrome paths
        chrome_paths = [
            "C:/Program Files/Google/Chrome/Application/chrome.exe",
            "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/usr/bin/google-chrome",
            "/usr/local/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/local/bin/chromium-browser",
        ]

        for path in chrome_paths:
            if os.path.exists(path):
                return path
        return None

    def show_error_message(self, message):
        QMessageBox.warning(None, "Error", message)