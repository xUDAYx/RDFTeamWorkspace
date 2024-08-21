from ftplib import FTP
import os
import sys
from PyQt6.QtWidgets import QMessageBox

class Download:
    def update_boilerplate(self, parent=None):
        # FTP connection details
        ftp_server = 'ftp.takeitideas.in'
        ftp_user = 'u257313635'  # Replace with your FTP username
        ftp_password = 'Vijaysss@123'  # Replace with your FTP password
        remote_file_path = '/domains/takeitideas.in/public_html/Downloads/Boilerplates/boilerplate.json'
        
        # Determine the path of the base folder (where the script or executable is located)
        base_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        print(base_folder)
        local_file_path = os.path.join(base_folder, 'boilerplate.json')

        try:
            # Connect to the FTP server
            ftp = FTP(ftp_server)
            ftp.login(user=ftp_user, passwd=ftp_password)

            # Navigate to the directory containing the file
            remote_folder = os.path.dirname(remote_file_path)
            ftp.cwd(remote_folder)

            # Download the file
            with open(local_file_path, 'wb') as local_file:
                ftp.retrbinary(f'RETR {os.path.basename(remote_file_path)}', local_file.write)

            ftp.quit()

            # Show success message
            QMessageBox.information(parent, "Success", "Boilerplate downloaded successfully!")

        except Exception as e:
            # Show error message
            QMessageBox.critical(parent, "Error", f"An error occurred: {e}")

