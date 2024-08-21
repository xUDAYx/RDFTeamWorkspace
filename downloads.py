from ftplib import FTP
import os
import sys
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
import stat

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

        is_update = os.path.exists(local_file_path)
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

            if is_update:
                QMessageBox.information(parent, "Success", "Boilerplate updated successfully!")
            else:
                QMessageBox.information(parent, "Success", "Boilerplate downloaded successfully!")
            # Show success message
            

        except Exception as e:
            # Show error message
            QMessageBox.critical(parent, "Error", f"An error occurred: {e}")


class DownloadThread(QThread):
    update_message = pyqtSignal(str)
    progress_update = pyqtSignal(int, str)
    error_message = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def run(self):
        # FTP connection details
        ftp_server = 'ftp.takeitideas.in'
        ftp_user = 'u257313635'
        ftp_password = 'Vijaysss@123'
        remote_folder_path = '/domains/takeitideas.in/public_html/Downloads/RDF_UI'
        
        base_folder = os.path.dirname(os.path.abspath(sys.argv[0]))
        local_folder_path = os.path.join(base_folder, 'RDF_UI')

        # Determine if this is a new download or an update
        is_update = os.path.exists(local_folder_path)

        def ensure_writable(path, is_file=False):
            """Ensure that the path (file or directory) is writable."""
            if is_file:
                try:
                    with open(path, 'a'):
                        pass
                except Exception as e:
                    self.error_message.emit(f"Failed to set writable permissions for file {path}: {e}")
                    return False
            else:
                if not os.access(path, os.W_OK):
                    try:
                        os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
                    except Exception as e:
                        self.error_message.emit(f"Failed to set writable permissions for directory {path}: {e}")
                        return False
            return True

        def download_directory(ftp, remote_path, local_path):
            """Recursively download a directory from the FTP server."""
            # Ensure the local directory exists and is writable
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            elif not ensure_writable(local_path):
                return
            
            try:
                ftp.cwd(remote_path)
            except Exception as e:
                self.error_message.emit(f"Failed to change directory to {remote_path}: {e}")
                return

            items = ftp.nlst()
            total_items = len(items)
            processed_items = 0

            for item in items:
                if item in ['.', '..']:
                    continue
                
                remote_item_path = os.path.join(remote_path, item).replace('\\', '/')
                local_item_path = os.path.join(local_path, item)
                
                try:
                    ftp.cwd(remote_item_path)  # Try to change into the directory
                    ftp.cwd('..')  # Go back to the previous directory
                    if not os.path.exists(local_item_path):
                        os.makedirs(local_item_path)
                    download_directory(ftp, remote_item_path, local_item_path)
                except Exception:
                    try:
                        with open(local_item_path, 'wb') as local_file:
                            ftp.retrbinary(f'RETR {item}', local_file.write)
                        if not ensure_writable(local_item_path, is_file=True):
                            self.error_message.emit(f"File {local_item_path} is not writable.")
                            return
                        processed_items += 1
                        progress = int((processed_items / total_items) * 100)
                        self.progress_update.emit(progress, item)
                    except Exception as file_error:
                        self.error_message.emit(f"Failed to write file {local_item_path}: {file_error}")
                        return

        try:
            ftp = FTP(ftp_server)
            ftp.login(user=ftp_user, passwd=ftp_password)

            if not os.path.exists(local_folder_path):
                os.makedirs(local_folder_path)
            elif not ensure_writable(local_folder_path):
                return

            download_directory(ftp, remote_folder_path, local_folder_path)

            ftp.quit()

            # Emit success message based on whether it's a new download or an update
            if is_update:
                self.update_message.emit("RDF_UI folder updated successfully!")
            else:
                self.update_message.emit("RDF_UI folder downloaded successfully!")

        except Exception as e:
            self.error_message.emit(f"An error occurred: {e}")