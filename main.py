import sys
import traceback
import subprocess
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QCheckBox,  QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt,QEvent
from code_editor import CodeEditor 
from mobile_view import MobileView # Importing the CodeEditor from the separate module
import os
import psutil
import requests
import urllib.parse
from PyQt6.QtCore import QSettings, Qt,pyqtSignal
from datetime import datetime, timedelta

# Custom exception hook for detailed error reporting
def excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("Unhandled exception:", exc_type, exc_value)
    traceback.print_tb(exc_traceback)
    QMessageBox.critical(None, "Unhandled Exception", f"An error occurred: {exc_value}")
    cleanup()

# Install the custom exception hook
sys.excepthook = excepthook

def is_apache_running():
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'httpd.exe' or proc.info['name'] == 'apache.exe':
            return True
    return False

def start_xampp():
    if not is_apache_running():
        try:
            subprocess.Popen([r'C:\xampp\xampp-control.exe'])
            print("Starting XAMPP Control Panel...")
        except Exception as e:
            print(f"Error starting XAMPP: {e}")
    else:
        print("Apache server is already running.")

def cleanup():
    print("Performing cleanup tasks...")

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setLayout(QVBoxLayout())

        # Username and Password fields
        self.username_label = QLabel("Email:")
        self.username_input = QLineEdit()
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        # "Remember Me" checkbox
        self.remember_me_checkbox = QCheckBox("Remember Me")

        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login)

        # Adding widgets to layout
        self.layout().addWidget(self.username_label)
        self.layout().addWidget(self.username_input)
        self.layout().addWidget(self.password_label)
        self.layout().addWidget(self.password_input)
        self.layout().addWidget(self.remember_me_checkbox)
        self.layout().addWidget(self.login_button)

        # Load remembered session if available
        self.load_remembered_session()

    def login(self):
        email = self.username_input.text()
        password = self.password_input.text()

        encoded_email = urllib.parse.quote(email)
        encoded_password = urllib.parse.quote(password)

        url = f"https://takeitideas.in/RDFSTUDIO/UserValidation/validateUser.php?email={encoded_email}&password={encoded_password}"

        try:
            response = requests.get(url)

            if response.text.strip() == "1":
                QMessageBox.information(self, "Login", "Login successful!")
                if self.remember_me_checkbox.isChecked():
                    self.remember_user_session(email)
                self.accept()  # Close dialog and continue
            else:
                QMessageBox.warning(self, "Login Failed", "Incorrect email or password.")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error connecting to server: {e}")

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
                # Automatically log in the user if within 24 hours
                self.username_input.setText(remembered_email)
                self.remember_me_checkbox.setChecked(True)
                self.login()
            else:
                # Clear the remembered session if expired
                settings.clear()



if __name__ == "__main__":
    app = QApplication(sys.argv)

    start_xampp()
    
    # Show login dialog first
    login_dialog = LoginDialog()
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Start the IDE if login is successful
        main_window = CodeEditor(login_dialog.username_input.text())
        main_window.show()
    
    # Start the event loop
    sys.exit(app.exec())