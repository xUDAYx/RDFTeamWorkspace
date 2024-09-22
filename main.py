import sys
import traceback
import subprocess
from PyQt6.QtGui import QIcon, QPixmap, QFont, QPalette, QColor
from PyQt6.QtWidgets import QApplication, QMessageBox, QCheckBox,  QHBoxLayout, QFormLayout, QFrame, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt6.QtCore import Qt, QTimer, QSettings
from datetime import datetime, timedelta
import psutil
import requests
import urllib.parse
from code_editor import CodeEditor  # Assuming your CodeEditor is a separate widget

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
        if proc.info['name'] in ['httpd.exe', 'apache.exe']:
            return True
    return False

def start_xampp():
    if not is_apache_running():
        try:
            subprocess.Popen([r'C:\\xampp\\xampp-control.exe'])
            print("Starting XAMPP Control Panel...")
        except Exception as e:
            print(f"Error starting XAMPP: {e}")
    else:
        print("Apache server is already running.")

def cleanup():
    print("Performing cleanup tasks...")

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_remembered_session()

    def init_ui(self):
        # Create widgets
        self.image_label = QLabel()
        pixmap = QPixmap("images/RDF.png")  # Update with the path to your image
        self.image_label.setPixmap(pixmap.scaled(250, 250, Qt.AspectRatioMode.KeepAspectRatio))

        image_frame = QFrame()
        image_frame.setLayout(QVBoxLayout())
        image_frame.layout().addWidget(self.image_label)
        image_frame.setStyleSheet("""
            QFrame {
                border: 5px solid transparent;
                border-radius: 10px;
                background-color: white;
            }
            QLabel {
                border-radius: 10px;
            }
            QFrame:hover {
                box-shadow: 0px 0px 10px 5px rgba(0, 0, 0, 0.5);
            }
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

        self.apply_styles()

        # Set layouts
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

        # Window settings
        self.setWindowTitle("RDF STUDIO")
        self.setGeometry(500, 200, 700, 400)  # Adjusted height for better layout

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #F0F0F0;
            }
            QLabel {
                font-family: Arial;
                font-size: 14px;
                color: #333;
            }
            QLineEdit {
                border: 1px solid black;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
            QPushButton {
                background-color:Blue;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-family: Arial;
            }
            QPushButton:hover {
                background-color: black;
            }
            QCheckBox {
                font-size: 12px;
            }
        """)

        palette = QPalette()
        gradient = QColor(220, 220, 220)
        palette.setColor(QPalette.ColorRole.Window, gradient)
        self.setAutoFillBackground(True)
        self.setPalette(palette)

    def login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        encoded_email = urllib.parse.quote(email)
        encoded_password = urllib.parse.quote(password)

        url = f"https://takeitideas.in/RDFSTUDIO/UserValidation/validateUser.php?email={encoded_email}&password={encoded_password}"

        try:
            response = requests.get(url)
            if response.text.strip() == "1":
                # No need to show the message here; we will handle success in handle_login
                if self.remember_me_checkbox.isChecked():
                    self.remember_user_session(email)
                return True  # Indicate successful login
            else:
                QMessageBox.warning(self, "Login Failed", "Incorrect email or password.")
                return False  # Indicate failed login
        except requests.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error connecting to server: {e}")
            return False  # Indicate failed login


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

def main():
    app = QApplication(sys.argv)
    start_xampp()  # Assuming this starts your server

    # Create the login page widget
    login_page = LoginPage()

    # Show the login page
    login_page.show()

    # Connect the login button to handle login action
    login_page.login_button.clicked.connect(lambda: handle_login(login_page))

    # Start the event loop
    sys.exit(app.exec())

def handle_login(login_page):
    if login_page.login():  # Call the login method to check credentials
        # Show the success message here, after login succeeds
        QMessageBox.information(login_page, "Login", "Login successful!")
        
        # If login is successful, hide the login page and show the main window
        login_page.hide()

        # Show the main window (CodeEditor)
        main_window = CodeEditor(login_page.email_input.text())  # Pass the email to the CodeEditor
        main_window.show()

        # Keep the main window reference alive to prevent garbage collection
        login_page.main_window = main_window  # Keep a reference to prevent garbage collection

    else:
        QMessageBox.warning(login_page, "Login Failed", "Incorrect email or password.")




if __name__ == '__main__':
    main()
