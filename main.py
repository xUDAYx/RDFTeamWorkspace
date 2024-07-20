import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication
from code_editor import CodeEditor

import os
import psutil

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
    # psutil does not require special cleanup, but this is where you would do it if needed

if __name__ == "__main__":
    # Start XAMPP control panel
    try:
        app = QApplication(sys.argv)
        editor = CodeEditor()
        editor.show()

        start_xampp()
        
        # Ensure cleanup is called on exit
        app.aboutToQuit.connect(cleanup)

        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Error running application: {e}")
        cleanup()  # Ensure cleanup is called in case of an exception
