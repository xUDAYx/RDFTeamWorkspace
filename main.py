import sys
import traceback
import subprocess
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication
from code_editor import CodeEditor
import os
import psutil

# Custom exception hook for detailed error reporting
def excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("Unhandled exception:", exc_type, exc_value)
    traceback.print_tb(exc_traceback)
    QMessageBox.critical(None, "Unhandled Exception", f"An error occurred: {exc_value}")
    cleanup()  # Ensure cleanup is called in case of an exception

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
            # Replace the path with your XAMPP control panel executable
            subprocess.Popen([r'C:\xampp\xampp-control.exe'])
            print("Starting XAMPP Control Panel...")
        except Exception as e:
            print(f"Error starting XAMPP: {e}")
    else:
        print("Apache server is already running.")

def cleanup():
    print("Performing cleanup tasks...")
    # Add any additional cleanup tasks here if needed

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        editor = CodeEditor()
        editor.show()
        app.setWindowIcon(QIcon(r"E:\RDFTeamWorkspace\icon\rdf_icon.ico"))

        start_xampp()
        
        # Ensure cleanup is called on exit
        app.aboutToQuit.connect(cleanup)

        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Error running application: {e}")
        cleanup()  # Ensure cleanup is called in case of an exception
