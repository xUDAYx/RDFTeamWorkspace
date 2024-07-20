from PyQt6.QtWidgets import QWidget, QVBoxLayout,QScrollArea, QTableWidget, QPushButton, QFileDialog, QTableWidgetItem, QHeaderView, QLineEdit, QHBoxLayout,QLabel,QMessageBox,QMenu,QInputDialog, QDialog
from PyQt6.QtCore import Qt, QDir, pyqtSignal, QSettings
from PyQt6.QtGui import QMouseEvent,QAction

from PyQt6.QtGui import QColor, QFont
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerHTML, QsciLexerJavaScript, QsciLexerCSS

import os
import json
import re
import shutil
from pathlib import Path
import config


CURRENT_PROJECT_PATH = None

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


class ProjectView(QWidget):
    file_double_clicked = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.showMaximized()
        self.setWindowFlags(Qt.WindowType.Window)
        self.setWindowTitle("Project View")

        # Create the main layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the "Select Workspace" button and QLineEdit
        button_layout = QHBoxLayout()
        self.path_line_edit = QLineEdit()
        self.path_line_edit.setReadOnly(True)
        button_layout.addWidget(self.path_line_edit)

        refresh_button = QPushButton("Refresh")
        refresh_button.setMaximumWidth(100)
        refresh_button.clicked.connect(self.refresh_directory)
        button_layout.addWidget(refresh_button)

        merge_button = QPushButton("Merge")
        merge_button.setMaximumWidth(100)
        merge_button.clicked.connect(self.merge_project)
        button_layout.addWidget(merge_button)

        

        layout.addLayout(button_layout)

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
    
    def show_context_menu(self, pos):
        table = self.sender()
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

            

            self.context_menu.exec(table.mapToGlobal(pos))
        elif item:
            # Right-click on table item
            self.context_menu.exec(table.mapToGlobal(pos))

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
            self.folder_path = folder_path  # Store the folder path
            self.populate_tables(folder_path)
            global CURRENT_PROJECT_PATH
            config.CURRENT_PROJECT_PATH = folder_path
            
            
    def merge_project(self):
    # Prompt the user to select another project folder to merge
        try:
            merge_folder_path = QFileDialog.getExistingDirectory(self, "Select Project to Merge", QDir.homePath())
            if merge_folder_path:
                current_project_path = self.path_line_edit.text()
            if current_project_path:
                success = self.merge_project_data(current_project_path, merge_folder_path)
                if success:
                    QMessageBox.information(self, "Merge Successful", "Project merged successfully.")
                else:
                    QMessageBox.critical(self, "Merge Failed", "Failed to merge project.")
                    self.populate_tables(current_project_path)
        except Exception as e:
            print(f"{e}")

    def merge_project_data(self, current_project_path, merge_folder_path):
        try:
            current_linked_files = read_project_info(current_project_path)
            merge_linked_files = read_project_info(merge_folder_path)

            # Combine dictionaries
            combined_linked_files = {**current_linked_files, **merge_linked_files}

            # Copy files from the merge project to the current project
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

            return True

        except Exception as e:
            print(f"Error merging project: {e}")
            return False

    
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
        table = self.sender()  # Get the table that triggered the event

        if table == self.table_view:
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
                column_map = {0: 'RDF_UI', 1: 'RDF_ACTION', 2: 'RDF_BW', 3: 'RDF_BVO', 4: 'RDF_DATA'}
                folder_name = column_map.get(column)
                if folder_name:
                    file_name = self.table_view.item(row, column).text()
                    if file_name:
                        file_path = os.path.join(self.folder_path, folder_name, file_name)
                        if os.path.exists(file_path):
                            self.file_double_clicked.emit(file_path)

        elif table == self.unlinked_table:
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

        # Prevent editing the cell on double-click
        self.table_view.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.unlinked_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

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
        # Clear both tables
        self.table_view.setRowCount(0)
        self.table_view.setColumnCount(5)
        self.table_view.setHorizontalHeaderLabels(["RDF_UI", "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA"])
        self.unlinked_table.setRowCount(0)

        # Get the linked files
        ui_file_map = read_project_info(folder_path)

        # Get all file names in the selected directory and its subdirectories
        all_file_names = get_all_file_names(folder_path)

        # Create a set of all linked files
        all_linked_files = set()
        for files in ui_file_map.values():
            all_linked_files.update(files)
        all_linked_files.update(ui_file_map.keys())

        # Create a list of unlinked files
        unlinked_files = [filename for filename in all_file_names if filename not in all_linked_files and not (filename == "ProjectInfo.json" or filename == "RDFView.php")]

        # Populate the table view with linked files
        row = 0
        for ui_file, related_files in ui_file_map.items():
            if file_exists_in_folder(os.path.join(folder_path, "RDF_UI"), ui_file):
                self.table_view.insertRow(row)
                self.table_view.setItem(row, 0, QTableWidgetItem(ui_file))

                for file in related_files:
                    if file.endswith(".js") and file_exists_in_folder(os.path.join(folder_path, "RDF_ACTION"), file):
                        self.table_view.setItem(row, 1, QTableWidgetItem(file))
                    elif file.endswith("BW.php") and file_exists_in_folder(os.path.join(folder_path, "RDF_BW"), file):
                        self.table_view.setItem(row, 2, QTableWidgetItem(file))
                    elif file.endswith("BVO.php") and file_exists_in_folder(os.path.join(folder_path, "RDF_BVO"), file):
                        self.table_view.setItem(row, 3, QTableWidgetItem(file))
                    elif file.endswith("Data.json") and file_exists_in_folder(os.path.join(folder_path, "RDF_DATA"), file):
                        self.table_view.setItem(row, 4, QTableWidgetItem(file))

                row += 1

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

        # self.table_view.resizeColumnsToContents()
        # self.unlinked_table.resizeColumnsToContents()
    def rename_file(self):
        table = self.sender().parent()
        if table == self.table_view:
            current_item = self.table_view.currentItem()
            if current_item:
                current_file_name = current_item.text()
                new_file_name, ok = QInputDialog.getText(self, "Rename File", "Enter new file name:", text=current_file_name)
                if ok and new_file_name != current_file_name:
                    current_row = self.table_view.currentRow()
                    current_column = self.table_view.currentColumn()
                    folder_name = self.get_folder_name_from_column(current_column)
                    old_file_path = os.path.join(self.folder_path, folder_name, current_file_name)
                    new_file_path = os.path.join(self.folder_path, folder_name, new_file_name)

                    try:
                        os.rename(old_file_path, new_file_path)
                        self.table_view.setItem(current_row, current_column, QTableWidgetItem(new_file_name))
                        self.refresh_directory()  # Refresh the directory after renaming the file
                        self.update_linked_files(current_row, current_column, new_file_name)  # Update the linked files
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to rename file: {e}")
        else:
            item = self.unlinked_table.currentItem()
            if item:
                current_file_name = item.text()
                new_file_name, ok = QInputDialog.getText(self, "Rename File", "Enter new file name:", text=current_file_name)
                if ok and new_file_name != current_file_name:
                    folder_name = self.get_folder_name_from_extension(current_file_name)
                    old_file_path = os.path.join(self.folder_path, folder_name, current_file_name)
                    new_file_path = os.path.join(self.folder_path, folder_name, new_file_name)

                    try:
                        os.rename(old_file_path, new_file_path)
                        row = self.unlinked_table.currentRow()
                        self.unlinked_table.setItem(row, 0, QTableWidgetItem(new_file_name))
                        self.refresh_directory()  # Refresh the directory after renaming the file
                    except Exception as e:
                        QMessageBox.warning(self, "Error", f"Failed to rename file: {e}")

    def initialize_validator(self, rules_path="rules"):
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
        with open(file, 'r') as f:
            return json.load(f)

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
