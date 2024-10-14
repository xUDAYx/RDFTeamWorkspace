import sys
import os
import threading
import traceback
import subprocess
import time
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor, QPixmap
from PyQt6.QtWidgets import QApplication, QMessageBox, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QFrame, QHBoxLayout, QFormLayout, QCheckBox
from PyQt6.QtCore import Qt, QTimer, QThread, QSettings
from datetime import datetime, timedelta
import psutil
import requests
import urllib.parse
from code_editor import CodeEditor  # Assuming your CodeEditor is a separate widget

# Custom exception hook for error reporting
def excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("Unhandled exception:", exc_type, exc_value)
    traceback.print_tb(exc_traceback)
    QMessageBox.critical(None, "Unhandled Exception", f"An error occurred: {exc_value}")

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

sys.excepthook = excepthook

def is_apache_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] in ['httpd.exe', 'apache.exe']:
            return True
    return False

def start_xampp():
    if not is_apache_running():
        try:
            subprocess.Popen([r'C:\\xampp\\xampp-control.exe'])
            print("Starting XAMPP Control Panel...")
            time.sleep(5)  # Simulating wait for XAMPP to start
        except Exception as e:
            print(f"Error starting XAMPP: {e}")
    else:
        print("Apache server is already running.")

class BackgroundTasks(QThread):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True

    def run(self):
        """This will run in a separate thread."""
        while self._is_running:
            start_xampp()
            self._is_running = False  # Stop the thread after starting XAMPP

    def stop(self):
        """Gracefully stop the thread."""
        self._is_running = False
        self.quit()
        self.wait()

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_remembered_session()
        self.background_thread = None

    def init_ui(self):
        # Initialize UI elements (similar to before)
        self.image_label = QLabel()
        pixmap = QPixmap(resource_path('images/RDF.png'))
        self.image_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))

        image_frame = QFrame()
        image_frame.setLayout(QVBoxLayout())
        image_frame.layout().addWidget(self.image_label)
        image_frame.setStyleSheet("""
            QFrame { border: 5px solid transparent; border-radius: 10px; background-color: white; }
            QLabel { border-radius: 10px; }
        """)

        welcome_label = QLabel("Welcome to RDF Studio")
        welcome_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("color: black; font-size: 25px;")

        email_label = QLabel("Email:")
        password_label = QLabel("Password:")

        self.email_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        self.remember_me_checkbox = QCheckBox("Remember Me")
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(70)
        self.login_button.setStyleSheet("background-color: blue;")
        self.login_button.clicked.connect(self.login)

        form_layout = QFormLayout()
        form_layout.addRow(email_label, self.email_input)
        form_layout.addRow(password_label, self.password_input)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.remember_me_checkbox)
        button_layout.addStretch(1)
        button_layout.addWidget(self.login_button)

        left_layout = QVBoxLayout()
        left_layout.addStretch()
        left_layout.addLayout(form_layout)
        left_layout.addStretch()
        left_layout.addLayout(button_layout)

        left_frame = QFrame()
        left_frame.setLayout(left_layout)
        left_frame.setStyleSheet("background-color:#E3F2FD;")

        right_layout = QVBoxLayout()
        right_layout.setSpacing(0)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.addWidget(image_frame, alignment=Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(welcome_label, alignment=Qt.AlignmentFlag.AlignCenter)

        right_frame = QFrame()
        right_frame.setLayout(right_layout)
        right_frame.setStyleSheet("background-color: white; padding: 20px;")

        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(left_frame, 6)
        main_layout.addWidget(right_frame, 5)

        self.setLayout(main_layout)
        self.setWindowTitle("RDF STUDIO")
        self.setGeometry(500, 200, 700, 400)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()
        encoded_email = urllib.parse.quote(email)
        encoded_password = urllib.parse.quote(password)

        url = f"https://takeitideas.in/RDFSTUDIO/UserValidation/validateUser.php?email={encoded_email}&password={encoded_password}"

        try:
            response = requests.get(url)
            if response.text.strip() == "1":
                if self.remember_me_checkbox.isChecked():
                    self.remember_user_session(email)
                QMessageBox.information(self, "Login", "Login successful!")
                
                # Now, show the main window and close the login window
                self.open_main_window()
                
                # Start the background thread to run XAMPP after login
                self.background_thread = BackgroundTasks()
                self.background_thread.start()

            else:
                QMessageBox.warning(self, "Login Failed", "Incorrect email or password.")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error connecting to server: {e}")

    def open_main_window(self):
        """Open the CodeEditor (main application window) and close the login page."""
        self.main_window = CodeEditor(self.email_input.text())  # Pass the user email to CodeEditor
        self.main_window.show()
        self.close()  # Close the login page

    def closeEvent(self, event):
        """Override the close event to stop the thread when the app closes."""
        if self.background_thread and self.background_thread.isRunning():
            self.background_thread.stop()  # Gracefully stop the thread
        super().closeEvent(event)

    def remember_user_session(self, email):
        settings = QSettings("YourCompany", "YourApp")
        expiration_time = datetime.now() + timedelta(hours=24)
        settings.setValue("remembered_email", email)
        settings.setValue("remembered_expiration", expiration_time.timestamp())

    def load_remembered_session(self):
        settings = QSettings("YourCompany", "YourApp")
        remembered_email = settings.value("remembered_email")
        remembered_expiration = settings.value("remembered_expiration", type=float)

        if remembered_email and remembered_expiration:
            expiration_time = datetime.fromtimestamp(remembered_expiration)
            if datetime.now() < expiration_time:
                self.email_input.setText(remembered_email)
                self.remember_me_checkbox.setChecked(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    login_page = LoginPage()
    login_page.show()
    
    sys.exit(app.exec())
