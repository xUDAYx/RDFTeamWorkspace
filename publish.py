# publish.py
import os
import json
import shutil,traceback
from ftplib import FTP, error_perm
from PyQt6.QtCore import QThread, pyqtSignal,QDir,Qt
from PyQt6.QtWidgets import (
    QWizard, QWizardPage,QWidget, QLabel, QLineEdit, QTextEdit, QHBoxLayout, QPushButton,QVBoxLayout,
    QFileDialog, QFormLayout, QGraphicsView, QGraphicsScene, QDialog,QMessageBox,QApplication,QProgressBar
)
from PyQt6.QtGui import QPixmap

class UploadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)

    def __init__(self, server, username, password, local_dir, remote_dir):
        super().__init__()
        self.server = server
        self.username = username
        self.password = password
        self.local_dir = local_dir
        self.remote_dir = remote_dir

    def run(self):
        try:
            self.upload_directory_to_ftp(self.server, self.username, self.password, self.local_dir, self.remote_dir)
            self.finished.emit(True)
        except Exception as e:
            print(f"Upload failed: {e}")
            self.finished.emit(False)

    def upload_directory_to_ftp(self, server, username, password, local_dir, remote_dir):
        ftp = None
        try:
            ftp = FTP(server, timeout=160)
            ftp.login(user=username, passwd=password)

            def make_remote_dirs(remote_directory):
                dirs = remote_directory.lstrip('/').split('/')
                path = ''
                for dir in dirs:
                    if dir:
                        path += f'/{dir}'
                        try:
                            ftp.cwd(path)
                            print(f"Directory exists: {path}")
                        except error_perm:
                            try:
                                ftp.mkd(path)
                                print(f"Created directory: {path}")
                            except error_perm as e:
                                print(f"Could not create directory {path}: {e}")
                                if 'File exists' in str(e):
                                    continue
                                else:
                                    raise

            def upload_file(local_file_path, remote_file_path):
                total_size = os.path.getsize(local_file_path)
                uploaded_size = 0
                
                def upload_progress(block):
                    nonlocal uploaded_size
                    uploaded_size += len(block)
                    progress_percentage = int((uploaded_size / total_size) * 100)
                    self.progress.emit(progress_percentage)
                
                try:
                    with open(local_file_path, 'rb') as file_data:
                        ftp.storbinary(f'STOR {remote_file_path}', file_data, callback=upload_progress)
                        print(f"File uploaded {remote_file_path}")
                except error_perm as e:
                    print(f"Failed to upload {remote_file_path}: {e}")
                    raise

            make_remote_dirs(remote_dir)

            total_files = sum([len(files) for _, _, files in os.walk(local_dir)])
            processed_files = 0

            for root, dirs, files in os.walk(local_dir):
                for directory in dirs:
                    local_dir_path = os.path.join(root, directory)
                    relative_dir_path = os.path.relpath(local_dir_path, local_dir).replace("\\", "/")
                    remote_sub_dir = os.path.join(remote_dir, relative_dir_path).replace("\\", "/")
                    make_remote_dirs(remote_sub_dir)

                for file in files:
                    local_file_path = os.path.join(root, file)
                    relative_file_path = os.path.relpath(local_file_path, local_dir).replace("\\", "/")
                    remote_file_path = os.path.join(remote_dir, relative_file_path).replace("\\", "/")
                    upload_file(local_file_path, remote_file_path)
                    processed_files += 1
                    progress_percentage = int((processed_files / total_files) * 100)
                    self.progress.emit(progress_percentage)

            print("Directory uploaded successfully.")
            return True

        except Exception as e:
            print(f"Failed to upload directory: {e}")
            traceback.print_exc()
            return False
        finally:
            if ftp:
                try:
                    ftp.quit()
                    print("FTP connection closed.")
                except Exception as e:
                    print(f"Failed to close FTP connection: {e}")

class ProjectInfoPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('Project Details')

        self.registerField("upload_dir*", self)

        self.layout = QFormLayout()

        self.title_label = QLabel("Project Title:")
        self.title_input = QLineEdit()
        self.layout.addRow(self.title_label, self.title_input)

        self.description_label = QLabel("Project Description:")
        self.description_input = QLineEdit()
        self.description_input.setFixedHeight(40)
        self.layout.addRow(self.description_label, self.description_input)

        self.version_label = QLabel("Version Details:")
        self.version_input = QLineEdit()
        self.layout.addRow(self.version_label, self.version_input)

        self.keywords_label = QLabel("Search Keywords:")
        self.keywords_input = QLineEdit()
        self.layout.addRow(self.keywords_label, self.keywords_input)

        self.banner_label = QLabel("Banner Image:")
        self.banner_input = QLineEdit()
        self.banner_input.setReadOnly(True)
        self.banner_button = QPushButton("Choose Image")
        self.banner_button.clicked.connect(self.choose_image)
        self.banner_layout = QHBoxLayout()
        self.banner_layout.addWidget(self.banner_input)
        self.banner_layout.addWidget(self.banner_button)

        self.preview_label = QLabel("Preview:")
        self.preview_view = QGraphicsView()
        self.preview_scene = QGraphicsScene()
        self.preview_view.setScene(self.preview_scene)
        self.banner_layout.addWidget(self.preview_label)
        self.banner_layout.addWidget(self.preview_view)
        self.layout.addRow(self.banner_label, self.banner_layout)

        self.registerField("banner_image_path", self.banner_input)
        self.registerField("project_title*", self.title_input)
        self.registerField("project_description*", self.description_input)
        self.registerField("version_details*", self.version_input)
        self.registerField("search_keywords*", self.keywords_input)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.goto_next_page)

        # Create a QHBoxLayout to hold the button
        button_layout = QHBoxLayout()
        button_layout.addStretch()  # Add a stretch to push the button to the right
        button_layout.addWidget(self.next_button)

        # Create a QWidget to hold the button_layout
        button_widget = QWidget()
        button_widget.setLayout(button_layout)

        # Add the button_widget to the form layout
        self.layout.addRow(button_widget)
        self.setLayout(self.layout)

    def choose_image(self):
    # Open file dialog to choose an image
        image_path, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Banner Image", 
            QDir.homePath(),  # Starting directory
            "Images (*.png *.jpg *.bmp)"  # File filter
        )
        
        # Check if a file was selected
        if image_path:
            # Show a preview of the selected image
            self.show_image_preview(image_path)
            
            # Set the banner_image_path field to the selected image path
            self.setField("banner_image_path", image_path)  # Set the field for banner image

    def show_image_preview(self, image_path):
        pixmap = QPixmap(image_path)
        self.preview_scene = QGraphicsScene(self)
        self.preview_scene.addPixmap(pixmap)
        self.preview_view.setScene(self.preview_scene)
        self.preview_view.fitInView(self.preview_scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio) 
        
    def goto_next_page(self):
        self.wizard().next()

    def validatePage(self):
        return True

    def nextId(self):
        return 1  # ID of the next page (FTP credentials page)


class FtpCredentialsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('FTP Credentials')

        self.layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.upload_button = QPushButton("Upload")

        upload_button_layout = QHBoxLayout()
        upload_button_layout.addStretch()
        upload_button_layout.addWidget(self.upload_button)

        upload_widget = QWidget()
        upload_widget.setLayout(upload_button_layout)

        self.layout.addRow("Username:", self.username_input)
        self.layout.addRow("Password:", self.password_input)
        self.layout.addWidget(upload_widget)
        self.setLayout(self.layout)

        self.upload_button.clicked.connect(self.upload)

    def upload(self):
        wizard = self.wizard()
        project_title = wizard.field("project_title")
        project_description = wizard.field("project_description")
        version_details = wizard.field("version_details")
        search_keywords = wizard.field("search_keywords")
        banner_image_path = wizard.field("banner_image_path")

        username = self.username_input.text()
        password = self.password_input.text()

        upload_dir = wizard.get_upload_directory()

        if upload_dir:
            # Validate FTP credentials before proceeding
            if not self.validate_ftp_credentials('ftp.takeitideas.in', username, password):
                QMessageBox.warning(self, 'Error', 'Invalid FTP credentials.')
                return

            project_name = os.path.basename(upload_dir)

            # Show the progress dialog
            self.publish_dialog = PublishDialog(self)
            self.publish_dialog.show()

            project_info_path = os.path.join(upload_dir, "ProjectInfo.json")

            # Update ProjectInfo.json with new fields
            with open(project_info_path, 'r+') as f:
                project_info = json.load(f)
                project_info.update({
                    "title": project_title,
                    "description": project_description,
                    "version": version_details,
                    "keywords": search_keywords
                })
                f.seek(0)
                json.dump(project_info, f, indent=4)
                f.truncate()

            if banner_image_path:
                if os.path.isfile(banner_image_path):
                    banner_dest_path = os.path.join(upload_dir, "banner.png")
                    try:
                        shutil.copy(banner_image_path, banner_dest_path)
                    except FileNotFoundError:
                        QMessageBox.critical(self, "Error", f"Banner image file not found: {banner_image_path}")
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to copy banner image: {e}")
                else:
                    QMessageBox.warning(self, 'Warning', 'Banner image file does not exist.')
            else:
                QMessageBox.warning(self, 'Warning', 'No banner image selected. Skipping image upload.')

            # FTP upload logic
            server = 'ftp.takeitideas.in'
            remote_dir = f'/public_html/RDFProjects_ROOT/{project_name}'
            self.upload_thread = UploadThread(server, username, password, upload_dir, remote_dir)

            self.upload_thread.progress.connect(self.publish_dialog.update_progress)
            self.upload_thread.finished.connect(self.on_upload_finished)

            self.upload_thread.start()

        else:
            QMessageBox.warning(self, 'Error', 'No valid directory for upload.')

    def validate_ftp_credentials(self, server, username, password):
        """Validate FTP credentials by attempting to connect to the FTP server."""
        try:
            ftp = FTP(server)
            ftp.login(user=username, passwd=password)
            ftp.quit()  # Disconnect after successful login
            return True
        except error_perm:
            return False  # Permission error, invalid credentials
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to connect to FTP server: {e}")
            return False

    def on_upload_finished(self, success):
        if success:
        # Show success message box
            QMessageBox.information(self, "Success", "Project uploaded successfully.")
        # Close the progress dialog and the wizard when the upload is complete
        self.publish_dialog.accept()
        self.wizard().accept()  # Ensure the wizard is also closed



class PublishWizard(QWizard):
    def __init__(self, current_tab, parent=None):
        super().__init__(parent)
        self.current_tab = current_tab

        self.setButtonLayout([
            QWizard.WizardButton.Stretch,
            QWizard.WizardButton.BackButton,
            QWizard.WizardButton.CancelButton,
        ])

        # Initialize wizard pages
        self.addPage(ProjectInfoPage(self))
        self.addPage(FtpCredentialsPage(self))

        # Ensure the file_path is valid
        if not self.current_tab.file_path:
            QMessageBox.warning(self, 'Error', 'No file selected for upload.')
            self.reject()

    def get_upload_directory(self):
        if self.current_tab.file_path:
            return os.path.dirname(os.path.dirname(self.current_tab.file_path))
        return None
    
class PublishDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Publishing Project')
        self.setFixedSize(300, 100)
        
        self.layout = QVBoxLayout()
        self.label = QLabel("Uploading...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        QApplication.processEvents()

    def upload_finished(self, success):
        if success:
            QMessageBox.information(self, "Success", "Project uploaded successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to upload project.")
        self.accept()


