from PyQt6.QtWidgets import QApplication,QWidget, QWizard,QWizardPage,QVBoxLayout,QScrollArea, QTableWidget,QProgressDialog, QPushButton,QListWidget, QFileDialog, QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout,QLabel,QMessageBox,QMenu,QInputDialog, QDialog, QComboBox
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QUrl
from PyQt6.QtGui import QMouseEvent,QAction

from PyQt6.QtGui import QColor, QFont,QDesktopServices
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerHTML, QsciLexerJavaScript, QsciLexerCSS
from PyQt6.QtWebEngineWidgets import QWebEngineView
import os
import json
import re,sys
import shutil
from pathlib import Path
import config

CURRENT_PROJECT_PATH = None

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def find_files(file_contents, pattern):
    try:
        return [os.path.basename(match) for match in re.findall(pattern, file_contents)]
    except Exception as e:
        print(f"Error in find_files: {e}")
        return []

def file_exists_in_folder(folder_path, file_name):
    for root, dirs, files in os.walk(folder_path):
        if file_name in files:
            return True
    return False

def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8",errors="replace") as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def read_project_info(folder_path):
    ui_file_map = {}

    project_info_path = os.path.join(folder_path, "ProjectInfo.json")

    if os.path.isfile(project_info_path):
        print(f"ProjectInfo.json file found at: {project_info_path}")
        try:
            with open(project_info_path, "r", encoding="utf-8") as f:
                project_info = json.load(f)
        except Exception as e:
            print(f"Error loading ProjectInfo.json: {e}")
            return ui_file_map

        init_file = project_info.get("init", "")
        if isinstance(init_file, str) and init_file.endswith("UI.php"):
            try:
                ui_file_map = find_linked_files(folder_path, init_file)
            except Exception as e:
                print(f"Error finding linked files: {e}")
    else:
        ui_files = [f for f in os.listdir(os.path.join(folder_path, "RDF_UI")) if f.endswith("UI.php")]
        if ui_files:
            selected_ui_file, ok = QInputDialog.getItem(None, "Select Main UI File", "Select the main UI file:", ui_files, 0, False)
            if ok and selected_ui_file:
                project_info = {
                    "init": selected_ui_file
                }
                with open(project_info_path, 'w') as file:
                    json.dump(project_info, file, indent=4)
                ui_file_map = find_linked_files(folder_path, selected_ui_file)
        else:
            print(f"No UI files found in {os.path.join(folder_path, 'RDF_UI')}")
            show_alert(f"Warning: No UI files found in the project directory. All files will be marked as Unlinked.")

    return ui_file_map

def find_linked_files(folder_path, init_file):
    ui_file_map = {init_file: []}
    found_ui_files = set()

    def process_ui_file(ui_file):
        ui_file_path = os.path.join(folder_path, "RDF_UI", ui_file)
        if os.path.isfile(ui_file_path):
            try:
                ui_file_contents = read_file(ui_file_path)
                
                # Find .js files in the UI.php file
                js_files = find_files(ui_file_contents, r'"(.*?\.js)"')
                ui_file_map[ui_file].extend([js_file for js_file in js_files if file_exists_in_folder(os.path.join(folder_path, "RDF_ACTION"), js_file)])

                # Find UI.php files in the UI.php file
                connected_ui_files = find_files(ui_file_contents, r'''ui=([^&'"]+)''')
                connected_ui_files_2 = find_files(ui_file_contents, r'''RDF_UI\/[^'"]*UI''')
                connected_ui_files.extend(connected_ui_files_2)

                additional_ui_files = [f"{ui_file}.php" for ui_file in connected_ui_files if file_exists_in_folder(os.path.join(folder_path, "RDF_UI"), f"{ui_file}.php")]
                found_ui_files.update(additional_ui_files)

                # Add new UI files to ui_file_map
                for additional_ui_file in additional_ui_files:
                    if additional_ui_file not in ui_file_map:
                        ui_file_map[additional_ui_file] = []
                

                # connected_ui_files += find_files(ui_file_contents, r'"(.*?UI\.php)"')
                additional_ui_files = [f"{ui_file}.php" for ui_file in connected_ui_files]
                found_ui_files.update(additional_ui_files)

                # Process .js files
                for js_file in js_files:
                    if file_exists_in_folder(os.path.join(folder_path, "RDF_ACTION"), js_file):
                        process_js_file(js_file, ui_file)

            except Exception as e:
                print(f"Error processing UI file {ui_file_path}: {e}")

    def process_js_file(js_file, parent_ui):
        js_file_path = os.path.join(folder_path, "RDF_ACTION", js_file)
        if os.path.isfile(js_file_path):
            try:
                js_file_contents = read_file(js_file_path)

                # Find BW.php files in the .js file
                bw_files = find_files(js_file_contents, r'[\w\/]+\/(.*?BW\.php)')
                ui_file_map[parent_ui].extend(bw_files)

                # Find UI.php files in the .js file
                connected_ui_files_js = find_files(js_file_contents, r'''RDFView\.php\?ui=([^'"]+)''')
                connected_ui_files_js = [f"{ui_file}.php" for ui_file in connected_ui_files_js]
                found_ui_files.update(connected_ui_files_js)

                # Process BW files
                for bw_file in bw_files:
                    process_bw_file(bw_file, parent_ui)

            except Exception as e:
                print(f"Error processing JS file {js_file_path}: {e}")

    def process_bw_file(bw_file, parent_ui):
        bw_file_path = os.path.join(folder_path, "RDF_BW", bw_file)
        if os.path.isfile(bw_file_path):
            try:
                bw_file_contents = read_file(bw_file_path)

                # Find BVO.php files in the BW.php file
                bvo_files = find_files(bw_file_contents, r'[\w\/]+\/(.*?BVO\.php)')
                ui_file_map[parent_ui].extend(bvo_files)

                # Process BVO files
                for bvo_file in bvo_files:
                    process_bvo_file(bvo_file, parent_ui)

            except Exception as e:
                print(f"Error processing BW file {bw_file_path}: {e}")

    def process_bvo_file(bvo_file, parent_ui):
        bvo_file_path = os.path.join(folder_path, "RDF_BVO", bvo_file)
        if os.path.isfile(bvo_file_path):
            try:
                bvo_file_contents = read_file(bvo_file_path)

                # Find Data.json files in the BVO.php file
                data_files = find_files(bvo_file_contents, r'[\w\/]+\/(.*?Data\.json)')
                ui_file_map[parent_ui].extend(data_files)

            except Exception as e:
                print(f"Error processing BVO file {bvo_file_path}: {e}")

    # Start processing with the initial UI file
    process_ui_file(init_file)

    # Process additional UI files
    processed_ui_files = set()
    while found_ui_files:
        additional_ui_file = found_ui_files.pop()
        if additional_ui_file in processed_ui_files:
            print(f"Warning: Circular reference detected for {additional_ui_file}. Skipping...")
            continue
        processed_ui_files.add(additional_ui_file)
        print(f"Processing additional UI file: {additional_ui_file}")
        ui_file_map[additional_ui_file] = []
        process_ui_file(additional_ui_file)
        
    print(ui_file_map)
    return ui_file_map

def process_additional_ui_file(folder_path, ui_file_name):
    linked_files = set()
    found_ui_files = set()
    ui_file_path = os.path.join(folder_path, "RDF_UI", ui_file_name)
    if os.path.isfile(ui_file_path):
        try:
            ui_file_contents = read_file(ui_file_path)
            linked_files.add(ui_file_name)
        except Exception as e:
            print(f"Error reading UI file {ui_file_path}: {e}")

        # Find .js files in the UI.php file
        try:
            js_files = find_files(ui_file_contents, r'"(.*?\.js)"')
            linked_files.update(js_files)
        except Exception as e:
            print(f"Error finding .js files in UI file: {e}")

        # Search for .js files in the RDF_ACTION folder
        for js_file in js_files:
            js_file_path = os.path.join(folder_path, "RDF_ACTION", js_file)
            if os.path.isfile(js_file_path):
                try:
                    js_file_contents = read_file(js_file_path)
                except Exception as e:
                    print(f"Error reading .js file {js_file_path}: {e}")
                    continue

                # Find BW.php files in the .js file
                try:
                    bw_files = find_files(js_file_contents, r'[\w\/]+\/(.*?BW\.php)')
                    linked_files.update(bw_files)
                except Exception as e:
                    print(f"Error finding BW.php files in .js file: {e}")

                # Find UI.php files in the .js file
                try:
                    connected_ui_files_js = find_files(js_file_contents, r'RDFView\.php\?ui=([^"]+)')
                    connected_ui_files_js = [f"{ui_file}.php" for ui_file in connected_ui_files_js]
                    found_ui_files.update(connected_ui_files_js)
                except Exception as e:
                    print(f"Error finding connected UI files in Main js file: {e}")

                # Search for BW.php files in the RDF_BW folder
                for bw_file in bw_files:
                    bw_file_path = os.path.join(folder_path, "RDF_BW", bw_file)
                    if os.path.isfile(bw_file_path):
                        try:
                            bw_file_contents = read_file(bw_file_path)
                        except Exception as e:
                            print(f"Error reading BW.php file {bw_file_path}: {e}")
                            continue

                        # Find BVO.php files in the BW.php file
                        try:
                            bvo_files = find_files(bw_file_contents, r'[\w\/]+\/(.*?BVO\.php)')
                            linked_files.update(bvo_files)
                        except Exception as e:
                            print(f"Error finding BVO.php files in BW.php file: {e}")

                        # Search for BVO.php files in the RDF_BVO folder
                        for bvo_file in bvo_files:
                            bvo_file_path = os.path.join(folder_path, "RDF_BVO", bvo_file)
                            if os.path.isfile(bvo_file_path):
                                try:
                                    bvo_file_contents = read_file(bvo_file_path)
                                except Exception as e:
                                    print(f"Error reading BVO.php file {bvo_file_path}: {e}")
                                    continue

                                # Find Data.json files in the BVO.php file
                                try:
                                    data_files = find_files(bvo_file_contents, r'[\w\/]+\/(.*?Data\.json)')
                                    linked_files.update(data_files)
                                except Exception as e:
                                    print(f"Error finding Data.json files in BVO.php file: {e}")

    return list(linked_files), found_ui_files   


def show_alert(message):
    alert = QMessageBox()
    alert.setIcon(QMessageBox.Icon.Warning)
    alert.setText(message)
    alert.setWindowTitle("Warning")
    alert.exec()

def get_all_file_names(directory):
    file_names = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_names.append(file)
    return file_names

class CopyWizard(QWizard):
    def __init__(self, copied_file_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Copy File to Project Folder")
        self.setGeometry(300, 200, 500, 400)

        self.copied_file_path = copied_file_path
        self.addPage(self.createCopyPage())

    def createCopyPage(self):
        page = QWizardPage()
        page.setTitle("Select Destination Project")

        layout = QVBoxLayout()
        # Search bar for filtering folders
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search for a project folder...")
        self.search_bar.textChanged.connect(self.filter_folders)
        layout.addWidget(self.search_bar)

        # List view for displaying folders
        self.folder_list = QListWidget()
        self.load_project_folders()
        layout.addWidget(self.folder_list)

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self.copy_file_to_selected_folder)
        layout.addWidget(self.copy_button)

        page.setLayout(layout)
        return page
    def filter_folders(self, text):
        # Filter folder list based on the search bar text
        for i in range(self.folder_list.count()):
            item = self.folder_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
    def load_project_folders(self):
        project_root_path = "C:/xampp/htdocs/RDFProjects_ROOT"
        if os.path.exists(project_root_path):
            for folder_name in os.listdir(project_root_path):
                full_path = os.path.join(project_root_path, folder_name)
                if os.path.isdir(full_path):
                    self.folder_list.addItem(folder_name)

    def get_target_folder(self, filename):
        if filename.endswith('UI.php'):
            return 'RDF_UI'
        elif filename.endswith('Action.js'):
            return 'RDF_ACTION'
        elif filename.endswith('BW,php'):
            return 'RDF_BW'
        elif filename.endswith('BVO.php'):
            return 'RDF_BVO'
        elif filename.endswith('Data.php'):
            return 'RDF_DATA'
        return None

    def copy_file_to_selected_folder(self):
        selected_item = self.folder_list.currentItem()
        if selected_item:
            selected_folder = selected_item.text()
            project_folder_path = os.path.join("C:/xampp/htdocs/RDFProjects_ROOT", selected_folder)
            filename = os.path.basename(self.copied_file_path)
            target_subfolder = self.get_target_folder(filename)

            if target_subfolder:
                destination_folder = os.path.join(project_folder_path, target_subfolder)
                destination_path = os.path.join(destination_folder, filename)

                if not os.path.exists(destination_folder):
                    os.makedirs(destination_folder)

                try:
                    shutil.copy(self.copied_file_path, destination_path)
                    QMessageBox.information(self, "Success", f"File '{filename}' copied to '{destination_folder}'")
                    self.accept()
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to copy file '{filename}': {e}")
            else:
                QMessageBox.warning(self, "Warning", f"File '{filename}' does not match any naming rules and was not copied.")
        else:
            QMessageBox.warning(self, "Warning", "No destination project folder selected.")

class ProjectView(QWidget):
    file_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.showMaximized()
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("Project View")

        self.copied_file_path = None  # Track the copied file path
        self.context_menu_table = None  
        # Store the table that requested the context menu
        # Create the main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Determine the base directory for file paths
        self.base_dir = getattr(sys, '_MEIPASS', os.getcwd())
        self.rules_path = os.path.join(self.base_dir, 'rules')

        # Create the "Select Workspace" button and QLineEdit
        button_layout = QHBoxLayout()
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setReadOnly(True)
        self.path_line_edit.setMaximumWidth(300)
        self.path_line_edit.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CCCCCC; border-radius: 5px; padding: 5px;")
        button_layout.addWidget(self.path_line_edit)
        refresh_button = QPushButton("Refresh")
        refresh_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 5px; padding: 5px;")
        refresh_button.setMaximumWidth(100)
        refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        refresh_button.clicked.connect(self.refresh_directory)
        button_layout.addWidget(refresh_button)

        open_another_project_button = QPushButton("Open Another Project")
        open_another_project_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; border-radius: 5px; padding: 5px;")
        open_another_project_button.clicked.connect(self.select_workspace)
        open_another_project_button.setMaximumWidth(150)
        open_another_project_button.setCursor(Qt.CursorShape.PointingHandCursor)

        button_layout.addWidget(open_another_project_button)

        layout.addLayout(button_layout)

        # Create a horizontal layout for the additional buttons
        additional_buttons_layout = QHBoxLayout()

        open_source_folder_button = QPushButton("Open Source Folder")
        open_source_folder_button.setStyleSheet("background-color: #FF4081; color: white; border: none; border-radius: 5px; padding: 5px;")
        open_source_folder_button.setMaximumWidth(150)
        open_source_folder_button.setCursor(Qt.CursorShape.PointingHandCursor)
        open_source_folder_button.clicked.connect(self.open_source_folder)
        additional_buttons_layout.addWidget(open_source_folder_button)

        self.merge_other_uis_button = QPushButton("Add UI Templates")
        self.merge_other_uis_button.setStyleSheet("background-color: #2196F3; color: white; border: none; border-radius: 5px; padding: 5px;")
        self.merge_other_uis_button.setMaximumWidth(150)
        self.merge_other_uis_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.merge_other_uis_button.clicked.connect(self.open_ui_merger)
        additional_buttons_layout.addWidget(self.merge_other_uis_button)

        merge_other_projects_button = QPushButton("Add Feature")
        merge_other_projects_button.setStyleSheet("background-color: #FF9800; color: white; border: none; border-radius: 5px; padding: 5px;")
        merge_other_projects_button.clicked.connect(self.open_feature_merger)
        merge_other_projects_button.setMaximumWidth(150)
        merge_other_projects_button.setCursor(Qt.CursorShape.PointingHandCursor)
        additional_buttons_layout.addWidget(merge_other_projects_button)


        layout.addLayout(additional_buttons_layout)
        # Create the table view
        self.table_view = QTableWidget()
        self.table_view.setColumnCount(5)
        self.table_view.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_view)
        self.table_view.cellDoubleClicked.connect(self.cell_double_clicked)

        # Add a title for the unlinked files table
        unlinked_files_title = QLabel("Unlinked Files")
        unlinked_files_title.setStyleSheet("font-weight: bold;")  # Make the title bold
        layout.addWidget(unlinked_files_title)

        

        # Create the unlinked files table
        self.unlinked_table = QTableWidget()
        self.unlinked_table.setColumnCount(1)
        self.unlinked_table.setHorizontalHeaderLabels(["Unlinked Files"])
        self.unlinked_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.unlinked_table)
        self.unlinked_table.cellDoubleClicked.connect(self.cell_double_clicked)

        self.table_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

        self.unlinked_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.unlinked_table.customContextMenuRequested.connect(self.show_context_menu)
        
        self.context_menu = QMenu(self)

        rename_action = QAction("Rename", self)
        rename_action.triggered.connect(self.rename_file)
        self.context_menu.addAction(rename_action)

        copy_action = QAction("Copy", self)
        copy_action.triggered.connect(self.copy_file)
        self.context_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste_file)
        self.context_menu.addAction(paste_action)

        delete_action = QAction("Delete", self)
        delete_action.triggered.connect(self.delete_file)
        self.context_menu.addAction(delete_action)

    
    
    def show_context_menu(self, pos):
        table = self.sender()
        self.context_menu_table = table  # Store the table requesting the context menu

        if table == self.table_view:
            item = self.table_view.itemAt(pos)
            column = self.table_view.currentColumn()
            header_item = self.table_view.horizontalHeaderItem(column)
        else:
            item = self.unlinked_table.itemAt(pos)
            column = self.unlinked_table.currentColumn()
            header_item = self.unlinked_table.horizontalHeaderItem(column)

        if header_item and not item:
            # Right-click on column header
            self.context_menu = QMenu(self)
            rename_action = QAction("Rename", self)
            rename_action.triggered.connect(self.rename_file)
            self.context_menu.addAction(rename_action)

            copy_action = QAction("Copy", self)
            copy_action.triggered.connect(self.copy_file)
            self.context_menu.addAction(copy_action)

            paste_action = QAction("Paste", self)
            paste_action.triggered.connect(self.paste_file)
            self.context_menu.addAction(paste_action)

            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(self.delete_file)
            self.context_menu.addAction(delete_action)

            self.context_menu.exec(table.mapToGlobal(pos))
        elif item:
            # Right-click on table item
            self.context_menu.exec(table.mapToGlobal(pos))

    def copy_file(self):
        table = self.context_menu_table  # Use the stored table reference
        current_item = table.currentItem()
        if current_item:
            current_file_name = current_item.text()
            if table == self.table_view:
                current_column = self.table_view.currentColumn()
                folder_name = self.get_folder_name_from_column(current_column)
                self.copied_file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
            elif table == self.unlinked_table:
                current_column = self.unlinked_table.currentColumn()
                folder_name = self.get_folder_name_from_column(current_column)
                self.copied_file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
            else:
                self.copied_file_path = os.path.join(self.path_line_edit.text(), current_file_name)
            
            if not os.path.exists(self.copied_file_path):
                QMessageBox.critical(self, "Error", f"File does not exist: {self.copied_file_path}")
            else:
                self.open_copy_wizard()

    def open_copy_wizard(self):
        wizard = CopyWizard(self.copied_file_path, self)
        wizard.exec()

    def paste_file(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()

        def get_target_folder(filename):
            if filename.endswith('UI.php'):
                return 'RDF_UI'
            elif filename.endswith('Action.js'):
                return 'RDF_ACTION'
            elif filename.endswith('BW.php'):
                return 'RDF_BW'
            elif filename.endswith('BVO.php'):
                return 'RDF_BVO'
            elif filename.endswith('Data.json'):
                return 'RDF_DATA'
            return None

        if mime_data.hasUrls():
            for url in mime_data.urls():
                source_path = url.toLocalFile()
                filename = os.path.basename(source_path)
                target_folder = get_target_folder(filename)

                if target_folder:
                    destination_folder = os.path.join(self.path_line_edit.text(), target_folder)
                    destination_path = os.path.join(destination_folder, filename)

                    if not os.path.exists(destination_folder):
                        os.makedirs(destination_folder)

                    try:
                        shutil.copy(source_path, destination_path)
                        QMessageBox.information(self, "Success", f"File '{filename}' pasted to '{destination_folder}'")
                        self.refresh_directory()  # Refresh the directory to show the new file
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to paste file '{filename}': {e}")
                else:
                    QMessageBox.warning(self, "Warning", f"File '{filename}' does not match any naming rules and was not pasted.")
        else:
            QMessageBox.warning(self, "Warning", "No valid file in clipboard to paste.")

    def delete_file(self):
        table = self.context_menu_table  # Use the stored table reference
        current_item = table.currentItem()
        if current_item:
            current_file_name = current_item.text()
            if table == self.table_view:
                current_column = self.table_view.currentColumn()
                folder_name = self.get_folder_name_from_column(current_column)
                file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
            elif table == self.unlinked_table:
                current_column = self.unlinked_table.currentColumn()
                folder_name = self.get_folder_name_from_column(current_column)
                file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
            else:
                file_path = os.path.join(self.path_line_edit.text(), current_file_name)

            confirm = QMessageBox.question(
            self,
            "Confirm Delete",
            f"<font color='red'>Are you sure you want to delete {current_file_name}? This file will be permanently deleted.</font>",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
            if confirm == QMessageBox.StandardButton.Yes:
                try:
                    os.remove(file_path)
                    self.refresh_directory()  # Refresh the directory after deleting the file
                    QMessageBox.information(self, "Success", f"File {current_file_name} deleted successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to delete file: {e}")

            
    def create_new_file(self):
        if not hasattr(self, 'folder_path') or not self.folder_path:
                QMessageBox.warning(self, "Project Not Opened", "Open a project first to create a new file.")
                return

        # Define the list of folders
        folders = ['RDF_UI', 'RDF_ACTION', 'RDF_BW', 'RDF_BVO', 'RDF_DATA']

        # Show the folder selection dialog
        folder_name, ok = QInputDialog.getItem(self, "Select Folder", "Select a folder to create a new file:", folders, 0, False)
        
        if ok and folder_name:
            # Determine the file naming convention note
            if folder_name == 'RDF_UI':
                naming_note = " (filename should end with 'UI')"
                expected_suffix = 'UI'
            elif folder_name == 'RDF_ACTION':
                naming_note = " (filename should end with 'Action')"
                expected_suffix = 'Action'
            elif folder_name == 'RDF_BW':
                naming_note = " (filename should end with 'BW')"
                expected_suffix = 'BW'
            elif folder_name == 'RDF_BVO':
                naming_note = " (filename should end with 'BVO')"
                expected_suffix = 'BVO'
            elif folder_name == 'RDF_DATA':
                naming_note = " (filename should end with 'Data')"
                expected_suffix = 'Data'
            else:
                naming_note = ""
                expected_suffix = ""

            while True:
                # Ask for the file name
                file_name, ok = QInputDialog.getText(self, "Create New File", f"Enter the name for the new file in {folder_name}{naming_note}:\nNote: Do not include the file extension.")
                
                if not ok:
                    return  # User canceled the dialog

                if file_name.endswith(expected_suffix):
                    break  # Valid filename, exit the loop

                QMessageBox.warning(self, "Invalid Filename", f"The filename must end with '{expected_suffix}' for files in the {folder_name} folder.")
            
            # Determine the file extension based on the selected folder
            if folder_name == 'RDF_UI' or folder_name == 'RDF_BW' or folder_name == 'RDF_BVO':
                extension = '.php'
            elif folder_name == 'RDF_ACTION':
                extension = '.js'
            elif folder_name == 'RDF_DATA':
                extension = '.json'
            else:
                extension = ''

            # Construct the file path
            file_path = os.path.join(self.folder_path, folder_name, file_name + extension)

            try:
                # Create the file
                with open(file_path, "w") as file:
                    file.write("")  # Create an empty file

                # Optionally refresh the directory view or update UI
                self.refresh_directory()  # Replace with your own logic

                QMessageBox.information(self, "File Created", f"Successfully created file:\n{file_path}")

            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to create new file: {e}")

    def copy_file(self):
        table = self.context_menu_table  # Use the stored table reference
        current_item = table.currentItem()
    
        if current_item:
            current_file_name = current_item.text()
            if table == self.table_view:
                current_column = self.table_view.currentColumn()
                folder_name = self.get_folder_name_from_column(current_column)
                self.copied_file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
            elif table == self.unlinked_table:
                current_column = self.unlinked_table.currentColumn()
                folder_name = self.get_folder_name_from_column(current_column)
                self.copied_file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
            else:
                self.copied_file_path = os.path.join(self.path_line_edit.text(), current_file_name)
        
            if self.copied_file_path and os.path.exists(self.copied_file_path):
                destination_path = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.path_line_edit.text())
                if destination_path:
                    try:
                        shutil.copy(self.copied_file_path, destination_path)
                        QMessageBox.information(self, "Success", f"File copied to {destination_path}")
                        self.refresh_directory()  # Refresh the directory to show the new file
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to copy file: {e}")
            else:
                QMessageBox.critical(self, "Error", f"File does not exist: {self.copied_file_path}")
    def paste_file(self):
        clipboard = QApplication.clipboard()
        mime_data = clipboard.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            for url in urls:
                source_path = url.toLocalFile()
                if os.path.exists(source_path):
                    destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.path_line_edit.text())
                    if destination_folder:
                        try:
                            shutil.copy(source_path, destination_folder)
                            QMessageBox.information(self, "Success", f"File pasted to {destination_folder}")
                            self.refresh_directory()  # Refresh the directory to show the new file
                        except Exception as e:
                            QMessageBox.critical(self, "Error", f"Failed to paste file: {e}")
                else:
                    QMessageBox.critical(self, "Error", "No file to paste or file does not exist")

    
    def get_folder_name_from_column(self, column):
        folder_names = ["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"]
        if column >= 0 and column < len(folder_names):
            return folder_names[column]
        return None

    def highlight_cell(self, row, column):
        item = self.table_view.item(row, column)
        if item:
            item.setBackground(Qt.GlobalColor.yellow)

    def highlight_unlinked_cell(self, row, column):
        item = self.unlinked_table.item(row, column)
        if item:
            item.setBackground(Qt.GlobalColor.yellow)

    def unhighlight_cells(self):
        for row in range(self.table_view.rowCount()):
            for column in range(self.table_view.columnCount()):
                item = self.table_view.item(row, column)
                if item:
                    item.setBackground(Qt.GlobalColor.white)
    def select_workspace(self):
        # Open a file dialog to select a directory
        folder_path = QFileDialog.getExistingDirectory(self, "Select Workspace")

        if folder_path:
            self.path_line_edit.setText(folder_path)
            self.folder_path = folder_path
            self.populate_tables(folder_path)
            global CURRENT_PROJECT_PATH
            config.CURRENT_PROJECT_PATH = folder_path

    def open_source_folder(self):
        folder_path = self.path_line_edit.text()
        if os.path.exists(folder_path):
            QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
        else:
            print("Folder does not exist:", folder_path)
            
            
    def open_feature_merger(self):
        """
        Opens the Feature merger dialog where the user can select and merge projects ending with '_feature'.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Feature Merger")
        dialog.setGeometry(530, 180, 200, 200)

        main_layout = QVBoxLayout()
        dialog.setLayout(main_layout)

        # Feature Project Selection Layout
        feature_layout = QHBoxLayout()

        # Feature Project Selection using QListWidget
        feature_file_layout = QVBoxLayout()
        feature_file_label = QLabel("Select Feature Project:")
        feature_file_list = QListWidget()
        feature_file_list.setFixedHeight(250)
        feature_file_list.setFixedWidth(230)
        self.populate_feature_files(feature_file_list)  # Populate QListWidget with Feature projects
        feature_file_layout.addWidget(feature_file_label)
        feature_file_layout.addWidget(feature_file_list)
        feature_file_layout.addStretch()
        feature_layout.addLayout(feature_file_layout)

        main_layout.addLayout(feature_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()

        # Merge Button
        merge_button = QPushButton("Merge Feature Project")
        merge_button.clicked.connect(lambda: self.merge_selected_feature(feature_file_list, dialog))
        buttons_layout.addWidget(merge_button)

        main_layout.addLayout(buttons_layout)

        # Apply modern CSS styles
        dialog.setStyleSheet("""
            QDialog {
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-size: 16px;
            }
            QListWidget {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        dialog.exec()

    def populate_feature_files(self, feature_file_list):
        """
        Populates the QListWidget with projects ending with '_feature'.
        """
        # Determine the base path depending on the execution environment
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))

        # Define the directory path where projects are located
        project_directory = os.path.join(base_path, "c:/xampp/htdocs/RDFProjects_ROOT")

        # Clear the list before populating
        feature_file_list.clear()

        try:
            # List all directories in the project_directory
            for project_name in os.listdir(project_directory):
                project_path = os.path.join(project_directory, project_name)
                if project_name.endswith('_Feature') and os.path.isdir(project_path):   
                    feature_file_list.addItem(project_name)
        except Exception as e:
            print(f"Error populating feature files: {e}")
            QMessageBox.critical(self, "Error", "Failed to load feature projects.")

    def merge_selected_feature(self, feature_file_list, dialog):
        if not hasattr(self, 'folder_path') or not self.folder_path:
            QMessageBox.warning(self, "Project Not Opened", "Open a project first to merge Feature")
            return
        
        selected_item = feature_file_list.currentItem()
        if selected_item is None:
            QMessageBox.warning(self, "No Project Selected", "Please select a project to merge.")
            return

        # Determine the base path depending on the execution environment
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))

        # Define the directory path where projects are located
        merge_folder_name = selected_item.text()
        merge_folder_path = os.path.join(base_path, "c:/xampp/htdocs/RDFProjects_ROOT", merge_folder_name)

        try:
            # Assuming `self.folder_path` is the path to the currently open project
            current_project_path = self.folder_path

            # Read project information
            current_linked_files = read_project_info(current_project_path)
            merge_linked_files = read_project_info(merge_folder_path)

            # Combine dictionaries
            combined_linked_files = {**current_linked_files, **merge_linked_files}

            # Define the folders to copy files from
            folders = ["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"]

            for folder in folders:
                current_folder_path = os.path.join(current_project_path, folder)
                merge_folder_path_specific = os.path.join(merge_folder_path, folder)

                if os.path.exists(merge_folder_path_specific):
                    for file_name in os.listdir(merge_folder_path_specific):
                        merge_file_path = os.path.join(merge_folder_path_specific, file_name)
                        current_file_path = os.path.join(current_folder_path, file_name)

                        if os.path.isfile(merge_file_path):
                            # Ensure the current folder exists
                            os.makedirs(current_folder_path, exist_ok=True)

                            # Copy file to the current project folder
                            shutil.copy2(merge_file_path, current_file_path)

                            # Add the file to the corresponding table column
                            column_index = folders.index(folder)
                            row_count = self.table_view.rowCount()
                            self.table_view.insertRow(row_count)
                            file_item = QTableWidgetItem(file_name)
                            self.table_view.setItem(row_count, column_index, file_item)

            # Populate tables with the updated project information
            self.populate_tables(current_project_path)

            # Show success message
            QMessageBox.information(self, "Merge Successful", f"'{merge_folder_name}' merged successfully.")
            self.refresh_directory()
            dialog.accept()

        except Exception as e:
            print(f"Error merging project: {e}")
            QMessageBox.critical(self, "Merge Failed", f"Failed to merge '{merge_folder_name}'.")

        
    def update_project_view(self, project_dir):
        try:
            print(f"Updating project view with: {project_dir}")  # Debug statement
            if project_dir:  # Ensure the project_dir is not empty
                self.folder_path = project_dir
                self.populate_tables(project_dir)
                global CURRENT_PROJECT_PATH
                CURRENT_PROJECT_PATH = project_dir  # Update the global variable
                config.CURRENT_PROJECT_PATH = project_dir
        except Exception as e:
            print(f"Error in update_project_view: {e}")
    
    def project_created_handler(self, folder_path):
        try:
            self.path_line_edit.setText(folder_path)
            self.populate_tables(folder_path)  # Update tables with new project data
        except Exception as e:
            print(f"An error occurred in project_created_handler: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred in project_created_handler: {e}")

    def refresh_directory(self):
        folder_path = self.path_line_edit.text()
        if folder_path:
            self.populate_tables(folder_path)

    def cell_double_clicked(self, row, column):
        try:
            table = self.sender()  # Get the table that triggered the event

            if table == self.table_view:
                try:
                    if row == 0:
                        folder_name_item = self.table_view.horizontalHeaderItem(column)
                        file_name_item = self.table_view.item(row, column)
                        if folder_name_item and file_name_item:
                            folder_name = folder_name_item.text()
                            file_name = file_name_item.text()
                            if file_name:
                                file_path = os.path.join(self.folder_path, folder_name, file_name)
                                if os.path.exists(file_path):
                                    self.file_double_clicked.emit(file_path)
                                else:
                                    print(f"File not found: {file_path}")
                            else:
                                print("File name is empty.")
                        else:
                            print("Folder name or file name item is None.")
                    else:
                        column_map = {0: 'RDF_UI', 1: 'RDF_ACTION', 2: 'RDF_BW', 3: 'RDF_BVO', 4: 'RDF_DATA'}
                        folder_name = column_map.get(column)
                        if folder_name:
                            file_name = self.table_view.item(row, column).text()
                            if file_name:
                                file_path = os.path.join(self.folder_path, folder_name, file_name)
                                if os.path.exists(file_path):
                                    self.file_double_clicked.emit(file_path)
                                else:
                                    print(f"File not found: {file_path}")
                            else:
                                print("File name is empty.")
                        else:
                            print(f"Invalid column index: {column}")
                except Exception as e:
                    print(f"Error processing table_view double-click: {e}")

            elif table == self.unlinked_table:
                try:
                    if self.unlinked_table.currentItem():
                        file_name = self.unlinked_table.currentItem().text()
                        folder_name = self.get_folder_name_from_extension(file_name)
                        if folder_name:
                            file_path = os.path.join(self.folder_path, folder_name, file_name)
                            if os.path.exists(file_path):
                                self.file_double_clicked.emit(file_path)
                            else:
                                print(f"Unlinked file not found: {file_path}")
                        else:
                            print(f"Unable to determine folder for unlinked file: {file_name}")
                except Exception as e:
                    print(f"Error processing unlinked_table double-click: {e}")

            # Prevent editing the cell on double-click
            try:
                self.table_view.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
                self.unlinked_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            except Exception as e:
                print(f"Error setting edit triggers: {e}")

        except Exception as e:
            print(f"Unexpected error in cell_double_clicked: {e}")

    def get_folder_name_from_extension(self, file_name):
        if file_name.endswith("UI.php"):
            return "RDF_UI"
        elif file_name.endswith(".js"):
            return "RDF_ACTION"
        elif file_name.endswith("BW.php"):
            return "RDF_BW"
        elif file_name.endswith("BVO.php"):
            return "RDF_BVO"
        elif file_name.endswith("Data.json"):
            return "RDF_DATA"
        else:
            return ""

    def populate_tables(self, folder_path):
        if folder_path is None:
            print("populate_tables was called with a None value.")
            return 
        correct_path = os.path.normpath(folder_path)
        self.path_line_edit.setText(correct_path)
        print(f"Populating tables for path: {correct_path}")
        try:
            # Clear both tables
            self.table_view.setRowCount(0)
            self.table_view.setColumnCount(5)
            self.table_view.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])
            self.unlinked_table.setRowCount(0)
        except Exception as e:
            print(f"Error clearing tables: {e}")

        try:
            # Get the linked files
            ui_file_map = read_project_info(folder_path)
        except Exception as e:
            print(f"Error reading project info: {e}")
            ui_file_map = {}

        try:
            # Get all file names in the selected directory and its subdirectories
            all_file_names = get_all_file_names(folder_path)
        except Exception as e:
            print(f"Error getting all file names: {e}")
            all_file_names = []

        try:
            # Create a set of all linked files
            all_linked_files = set()
            for files in ui_file_map.values():
                all_linked_files.update(files)
            all_linked_files.update(ui_file_map.keys())
        except Exception as e:
            print(f"Error creating set of all linked files: {e}")
            all_linked_files = set()

        try:
            # Create a list of unlinked files
            unlinked_files = [filename for filename in all_file_names if filename not in all_linked_files and not (filename == "ProjectInfo.json" or filename == "RDFView.php")]
        except Exception as e:
            print(f"Error creating list of unlinked files: {e}")
            unlinked_files = []

        try:
            # Populate the table view with linked files
            row = 0
            for ui_file, related_files in ui_file_map.items():
                if file_exists_in_folder(os.path.join(folder_path, "RDF_UI"), ui_file):
                    self.table_view.insertRow(row)
                    self.table_view.setItem(row, 0, QTableWidgetItem(ui_file))

                    for file in related_files:
                        try:
                            if file.endswith(".js") and file_exists_in_folder(os.path.join(folder_path, "RDF_ACTION"), file):
                                self.table_view.setItem(row, 1, QTableWidgetItem(file))
                            elif file.endswith("BW.php") and file_exists_in_folder(os.path.join(folder_path, "RDF_BW"), file):
                                self.table_view.setItem(row, 2, QTableWidgetItem(file))
                            elif file.endswith("BVO.php") and file_exists_in_folder(os.path.join(folder_path, "RDF_BVO"), file):
                                self.table_view.setItem(row, 3, QTableWidgetItem(file))
                            elif file.endswith("Data.json") and file_exists_in_folder(os.path.join(folder_path, "RDF_DATA"), file):
                                self.table_view.setItem(row, 4, QTableWidgetItem(file))
                        except Exception as e:
                            print(f"Error populating table view with linked file '{file}': {e}")

                    row += 1
        except Exception as e:
            print(f"Error populating table view with linked files: {e}")

        try:
            # Populate the unlinked files table
            self.unlinked_table.setColumnCount(5)
            self.unlinked_table.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])

            unlinked_ui_files = [file for file in unlinked_files if file.endswith("UI.php")]
            unlinked_action_files = [file for file in unlinked_files if file.endswith(".js")]
            unlinked_bw_files = [file for file in unlinked_files if file.endswith("BW.php")]
            unlinked_bvo_files = [file for file in unlinked_files if file.endswith("BVO.php")]
            unlinked_data_files = [file for file in unlinked_files if file.endswith("Data.json")]

            max_unlinked = max(len(unlinked_ui_files), len(unlinked_action_files), len(unlinked_bw_files), len(unlinked_bvo_files), len(unlinked_data_files))
            self.unlinked_table.setRowCount(max_unlinked)

            for row in range(max_unlinked):
                try:
                    if row < len(unlinked_ui_files):
                        self.unlinked_table.setItem(row, 0, QTableWidgetItem(unlinked_ui_files[row]))
                    if row < len(unlinked_action_files):
                        self.unlinked_table.setItem(row, 1, QTableWidgetItem(unlinked_action_files[row]))
                    if row < len(unlinked_bw_files):
                        self.unlinked_table.setItem(row, 2, QTableWidgetItem(unlinked_bw_files[row]))
                    if row < len(unlinked_bvo_files):
                        self.unlinked_table.setItem(row, 3, QTableWidgetItem(unlinked_bvo_files[row]))
                    if row < len(unlinked_data_files):
                        self.unlinked_table.setItem(row, 4, QTableWidgetItem(unlinked_data_files[row]))
                except Exception as e:
                    print(f"Error populating unlinked files table at row {row}: {e}")
        except Exception as e:
            print(f"Error populating unlinked files table: {e}")



    

        


     
    def rename_file(self):
        try:
            table = self.context_menu_table  # Use the stored table reference
            current_item = table.currentItem()
        
            if current_item:
                current_file_name = current_item.text()
                new_file_name, ok = QInputDialog.getText(self, "Rename File", "Enter new file name:", text=current_file_name)
                if ok and new_file_name != current_file_name:
                    if table == self.table_view:
                        current_row = self.table_view.currentRow()
                        current_column = self.table_view.currentColumn()
                        folder_name = self.get_folder_name_from_column(current_column)
                        old_file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
                        new_file_path = os.path.join(self.path_line_edit.text(), folder_name, new_file_name)

                    elif table == self.unlinked_table:
                        current_row = self.unlinked_table.currentRow()
                        current_column = self.unlinked_table.currentColumn()
                        folder_name = self.get_folder_name_from_column(current_column)
                        old_file_path = os.path.join(self.path_line_edit.text(), folder_name, current_file_name)
                        new_file_path = os.path.join(self.path_line_edit.text(), folder_name, new_file_name)

                    else:
                        old_file_path = os.path.join(self.path_line_edit.text(), current_file_name)
                        new_file_path = os.path.join(self.path_line_edit.text(), new_file_name)
                
                    try:
                        os.rename(old_file_path, new_file_path)
                        current_item.setText(new_file_name)
                        self.refresh_directory()  # Refresh the directory after renaming the file
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to rename file: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to rename file: {e}")
            print(f"error in rename{e}")
            
    

    def initialize_validator(self, rules_path=None):
        if rules_path is None:
            rules_path = self.rules_path

        try:
            project_path = config.CURRENT_PROJECT_PATH
            if not project_path:
                raise ValueError("Project path is not set. Please ensure the path is valid.")
            
            rules_mapping = {
                'Action.js': 'rules_action.json',
                'BVO.php': 'rules_bvo.json',
                'BW.php': 'rules_bw.json',
                'Data.json': 'rules_json.json',
                'UI.php': 'rules_ui.json',
            }
            
            rules_dict = self.collect_rules(rules_path)
            return project_path, rules_mapping, rules_dict
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to initialize validator: {e}")

    def read_rules(self, file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read rules file: {e}")

    def collect_rules(self, rules_path):
        try:
            rules_dict = {}
            for rule_file in os.listdir(rules_path):
                rule_path = os.path.join(rules_path, rule_file)
                rules_dict[rule_file] = self.read_rules(rule_path)
            return rules_dict
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to collect rules: {e}")

    def collect_files_to_validate(self, project_path):
        try:
            if not project_path:
                raise ValueError("Project path is not set. Please ensure the path is valid.")
            
            files_to_validate = []
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    files_to_validate.append(file_path)
            return files_to_validate
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to collect files to validate: {e}")

    def apply_rules(self, content, rules):
        try:
            errors = []
            table_rule_present = False
            section_rule_present = False
            table_rule = None
            section_rule = None

            lines = content.splitlines()

            for rule in rules["rules"]:
                if rule["description"] == "Table tag should be present":
                    table_rule_present = True
                    table_rule = rule
                    continue

                elif rule["description"] == "File must contain a table tag with class 'section'":
                    section_rule_present = True
                    section_rule = rule
                    continue

                # Apply other rules
                for i, line in enumerate(lines, start=1):
                    if re.search(rule["pattern"], line):
                        errors.append(f"Line {i}: {rule['description']}")

            if table_rule_present:
                table_found = any(re.search(table_rule["pattern"], line) for line in lines)
                if not table_found:
                    errors.append("Line N/A: Table tag should be present")

            if section_rule_present:
                section_found = any(re.search(section_rule["pattern"], line) for line in lines)
                if not section_found:
                    errors.append("Line N/A: Class section should be present in Table Tag")

            return errors
        except Exception as e:
            return [f"Error applying rules: {e}"]
        
    def validate_and_apply_rules(self, file_path, rules_mapping, rules_dict):
        try:
            file_name = os.path.basename(file_path)
            rule_file = None

            for key, value in rules_mapping.items():
                if key in file_name:
                    rule_file = value
                    break

            print(f"Validating {file_path} with rule file {rule_file}")

            if rule_file:
                rules = rules_dict.get(rule_file)
                if not rules:
                    return [f"Rule file {rule_file} not found in rules_dict"]

                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        errors = self.apply_rules(content, rules)
                    return errors
                except Exception as e:
                    return [f"Error loading file content: {e}"]
            else:
                return ["Filename should be according to the RDF rules"]
        except Exception as e:
            return [f"Error validating file: {e}"]

    def validate_files(self, project_path, rules_mapping, rules_dict):
        try:
            self.files_with_errors = {}  
            files_to_validate = self.collect_files_to_validate(project_path)
            self.files_with_errors.clear()
            exclude_files = {"ProjectInfo.json", "RDFView.php"}

            for file_path in files_to_validate:
                if os.path.basename(file_path) in exclude_files:
                    print(f"Skipping validation for {file_path}")
                    continue

                errors = self.validate_and_apply_rules(file_path, rules_mapping, rules_dict)
                if errors:
                    self.files_with_errors[file_path] = errors
                    print(f"File with errors: {os.path.basename(file_path)}")
            self.highlight_files_with_errors()
            return self.files_with_errors
        except Exception as e:
            print(f"Error validating files: {e}")

    def show_results(self, files_with_errors):
        try:
            dialog = QDialog()
            dialog.setWindowTitle("Validation Results")
            
            layout = QVBoxLayout()
            if files_with_errors:
                label = QLabel(f"{len(files_with_errors)} files have validation errors. Please go to red-colored files in the project view to see the errors.")
                layout.addWidget(label)
            else:
                label = QLabel("All files validated successfully.")
                layout.addWidget(label)

            dialog.setLayout(layout)
            dialog.exec()
        except Exception as e:
            print(f"Error showing results: {e}")

    def show_file_errors(self, file, errors):
        try:
            error_dialog = QMessageBox()
            error_dialog.setWindowTitle(f"Errors in {file}")
            error_dialog.setText("\n".join(f"Line {error['line']}: {error['message']}" if isinstance(error, dict) else error for error in errors))
            error_dialog.exec()
        except Exception as e:
            print(f"Error showing file errors: {e}")
            
    def highlight_files_with_errors(self):
        for row in range(self.table_view.rowCount()):
            for col in range(self.table_view.columnCount()):
                item = self.table_view.item(row, col)
                if item and item.text():
                    file_name = item.text()
                    for error_file in self.files_with_errors.keys():
                        if file_name == os.path.basename(error_file):
                            item.setBackground(Qt.GlobalColor.red)
                            break

    def open_ui_merger(self):
        """
        Opens the UI merger dialog where the user can select and merge UI files.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("UI Merger")
        dialog.setGeometry(530, 180, 500, 600)

        main_layout = QVBoxLayout()
        dialog.setLayout(main_layout)

        # UI File Selection and Mobile View Layout
        ui_mobile_layout = QHBoxLayout()

        # UI File Selection using QListWidget
        ui_file_layout = QVBoxLayout()
        ui_file_label = QLabel("Select UI File:")
        ui_file_list = QListWidget()
        ui_file_list.setFixedHeight(500) 
        ui_file_list.setFixedWidth(230)
        self.populate_ui_files(ui_file_list)  # Populate QListWidget with UI files
        ui_file_layout.addWidget(ui_file_label)
        ui_file_layout.addWidget(ui_file_list)
        ui_file_layout.addStretch()
        ui_mobile_layout.addLayout(ui_file_layout)

        # Mobile View for UI File Preview
        self.mobile_view_layout = QVBoxLayout()
        self.Mobile_label = QLabel("Preview:")
        self.mobile_view = QWebEngineView()
        self.mobile_view.setFixedSize(300, 500)
        self.mobile_view.setStyleSheet("border: 2px solid black; border-radius: 4px;")
        self.mobile_view_layout.addWidget(self.Mobile_label)
        self.mobile_view_layout.addWidget(self.mobile_view)
        self.mobile_view_layout.addStretch()
        ui_mobile_layout.addLayout(self.mobile_view_layout)

        main_layout.addLayout(ui_mobile_layout)

        # Buttons Layout
        buttons_layout = QVBoxLayout()

        # Merge Button
        merge_button = QPushButton("Merge UI Files")
        merge_button.clicked.connect(lambda: self.merge_ui_files(ui_file_list, dialog))
        buttons_layout.addWidget(merge_button)

        main_layout.addLayout(buttons_layout)

        # Connect the UI file list selection change to update the mobile view
        ui_file_list.currentItemChanged.connect(lambda: self.update_mobile_view(ui_file_list.currentItem().text() if ui_file_list.currentItem() else ""))

        # Apply modern CSS styles
        dialog.setStyleSheet("""
            QDialog {
                color: #ffffff;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-size: 16px;
            }
            QListWidget {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #ffffff;
                color: #000000;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                border: none;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        dialog.exec()

    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores the path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def populate_ui_files(self, ui_file_list):
        """
        Populates the QListWidget with UI files from the 'C:/xampp/htdocs/RDFProjects_ROOT/RDF_UIProjects' directory.
        """
        ui_files_dir = resource_path('C:/xampp/htdocs/RDFProjects_ROOT/RDF_UIProjects/RDF_UI')
        if not os.path.exists(ui_files_dir):
            QMessageBox.warning(self, "Directory Not Found", f"Directory '{ui_files_dir}' not found.")
            return

        ui_files = [f for f in os.listdir(ui_files_dir) if f.endswith('.php')]
        ui_file_list.clear()
        ui_file_list.addItems(ui_files)

    def merge_ui_files(self, ui_file_list, dialog):
        if not hasattr(self, 'folder_path') or not self.folder_path:
            QMessageBox.warning(self, "Project Not Opened", "Open a project first to merge UI files")
            return

        """
        Merges the selected UI file into the RDF_UI folder of the current project.
        """
        project_path = config.CURRENT_PROJECT_PATH
        if not project_path:
            QMessageBox.warning(self, "Project Not Opened", "Open a project first to merge UI files.")
            return

        selected_ui_file = ui_file_list.currentItem().text() if ui_file_list.currentItem() else ""
        if not selected_ui_file:
            QMessageBox.warning(self, "No UI File Selected", "Please select a UI file to merge.")
            return

        src_file = resource_path(os.path.join('C:/xampp/htdocs/RDFProjects_ROOT/RDF_UIProjects/RDF_UI', selected_ui_file))
        dst_dir = os.path.join(project_path, 'RDF_UI')
        os.makedirs(dst_dir, exist_ok=True)
        dst_file = os.path.join(dst_dir, selected_ui_file)

        try:
            shutil.copy(src_file, dst_file)
            QMessageBox.information(self, "Success", f"UI file '{selected_ui_file}' merged successfully!")
            self.file_double_clicked.emit(dst_file)
            print(dst_file)
            dialog.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while merging the UI file: {str(e)}")

        self.refresh_directory()

    def update_mobile_view(self, selected_ui_file):
        if not selected_ui_file:
            return

        # Ensure the selected file has the correct extension
        if not selected_ui_file.endswith('.php'):
            selected_ui_file += '.php'

        sample_ui_dir = resource_path('C:/xampp/htdocs/RDFProjects_ROOT/RDF_UIProjects/RDF_UI')
        file_path = os.path.normpath(os.path.join(sample_ui_dir, selected_ui_file))

        print(f"Loading UI file from: {file_path}")  # Debug: Print the file path
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    html_content = file.read()
                    self.mobile_view.setHtml(html_content)
        except Exception as e:
            print(f"Error updating mobile view: {e}")

   