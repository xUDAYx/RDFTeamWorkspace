import re
import json
import os, sys
import logging,chardet
import traceback
from ftplib import FTP,error_perm
import time
import shutil

from pc_view import PCView
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from PyQt6.QtGui import QSyntaxHighlighter,QIcon
from PyQt6.Qsci import QsciDocument
from PyQt6.QtWidgets import QWizard, QDialog,QPlainTextEdit,QProgressDialog, QProgressBar,QInputDialog,QLabel, QMainWindow,QLineEdit,QMenu, QVBoxLayout, QWidget, QSplitter, QDialogButtonBox, QTreeView, QToolBar, QFileDialog, QToolButton, QTabWidget, QApplication, QMessageBox, QPushButton, QTextEdit, QScrollBar, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import  QTextCharFormat,QAction, QPixmap, QFileSystemModel, QIcon, QFont, QPainter, QColor, QTextFormat, QTextCursor, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QModelIndex, QTimer, QDir,QThread, pyqtSlot, QSize, QRect, QProcess, QPoint, pyqtSignal
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerHTML, QsciLexerJavaScript, QsciLexerCSS

from terminal_widget import TerminalWidget
from mobile_view import MobileView
from project_view import ProjectView
from new_project import NewProjectWizard
from theme import DarkTheme
from PyQt6.Qsci import QsciAbstractAPIs, QsciScintilla, QsciDocument,QsciLexerJSON
from autocompleter import AutoCompleter
from Rule_Engine import RuleEngine
from code_formatter import CodeFormatter
from OpenProject import OpenProjectWizard
from ref_view import ReferenceView
from publish import PublishWizard
from file_view import FileView
from downloads import Download,DownloadThread,DownloadDailog,DownloadProjectsThread

class MultiLanguageHighlighter(QsciAbstractAPIs):
    def __init__(self, editor: QsciScintilla):
        super().__init__(editor)
        self.editor = editor
        self.highlighter_rules = {}

    def set_language(self, language):
        if language == "html":
            self.editor.setLexer(QsciLexerHTML())
        elif language == "javascript":
            self.editor.setLexer(QsciLexerJavaScript())
        elif language == "css":
            self.editor.setLexer(QsciLexerCSS())
        elif language == "python":
            self.editor.setLexer(QsciLexerPython())
            
    
    def autoCompletionSource(self, source):
        return self.highlighter_rules.get(source, [])

class MultiLanguageHighlighter(QSyntaxHighlighter):
    def __init__(self, parent: QsciDocument):
        super().__init__(parent)
        self.highlighter_rules = {}

    def set_language(self, language):
        if language == "html":
            self.setCurrentBlockState(0)
            self.setCurrentBlockUserData(0)
            self.highlightingRules = self.highlighter_rules.get("html", [])
        elif language == "javascript":
            self.setCurrentBlockState(0)
            self.setCurrentBlockUserData(0)
            self.highlightingRules = self.highlighter_rules.get("javascript", [])
        elif language == "css":
            self.setCurrentBlockState(0)
            self.setCurrentBlockUserData(0)
            self.highlightingRules = self.highlighter_rules.get("css", [])
        elif language == "python":
            self.setCurrentBlockState(0)
            self.setCurrentBlockUserData(0)
            self.highlightingRules = self.highlighter_rules.get("python", [])


class CustomCodeEditor(QsciScintilla):
    def __init__(self):
        try:
            super().__init__()
            self.font_size = 12  # Default font size
            self.setup_editor()
        except Exception as e:
            print(f"Error initializing CustomCodeEditor: {e}")
            
            
    
    def show_context_menu(self, pos):
        # Create the context menu
        menu = self.createStandardContextMenu()
        
        # Add the "Insert Boilerplate" action to the context menu
        insert_boilerplate_action = QAction("Insert Boilerplate", self)
        insert_boilerplate_action.triggered.connect(self.contextMenuEvent)
        menu.addAction(insert_boilerplate_action)
        
        # Show the context menu
        menu.exec_(self.mapToGlobal(pos))

    def contextMenuEvent(self, event):
        # Determine the directory of the EXE or script
        if getattr(sys, 'frozen', False):
            # If the application is running as an EXE
            base_dir = os.path.dirname(sys.executable)
        else:
            # If the application is running as a script
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the boilerplate.json
        json_path = os.path.join(base_dir, 'boilerplate.json')

        if not os.path.exists(json_path):
            # Show a message box if the boilerplate.json file does not exist
            QMessageBox.warning(self, "File Not Found", "boilerplate.json does not exist in the same folder as the application.")
            return
        
        # Create the context menu
        menu = QMenu(self)
        
        # Add the "Insert Boilerplate" submenu
        insert_boilerplate_menu = QMenu("Insert Boilerplate", self)
        menu.addMenu(insert_boilerplate_menu)
        
        # Add the category submenus
        easy_html_tags_menu = QMenu("Easy HTML Tags", insert_boilerplate_menu)
        complex_html_tags_menu = QMenu("Complex HTML Tags", insert_boilerplate_menu)
        ready_made_menu = QMenu("Ready Made", insert_boilerplate_menu)
        insert_boilerplate_menu.addMenu(easy_html_tags_menu)
        insert_boilerplate_menu.addMenu(complex_html_tags_menu)
        insert_boilerplate_menu.addMenu(ready_made_menu)
        
        # Load the boilerplate options from the JSON file
        with open(json_path, 'r') as f:
            boilerplate_data = json.load(f)
        
        # Add each boilerplate option to the appropriate submenu
        for boilerplate_name, boilerplate_code in boilerplate_data.items():
            if boilerplate_name.startswith("Easy HTML Tags:"):
                boilerplate_action = QAction(boilerplate_name.split(":")[1], self)
                boilerplate_action.triggered.connect(lambda checked, code=boilerplate_code: self.insert_boilerplate(code))
                easy_html_tags_menu.addAction(boilerplate_action)
            elif boilerplate_name.startswith("Complex HTML Tags:"):
                boilerplate_action = QAction(boilerplate_name.split(":")[1], self)
                boilerplate_action.triggered.connect(lambda checked, code=boilerplate_code: self.insert_boilerplate(code))
                complex_html_tags_menu.addAction(boilerplate_action)
            elif boilerplate_name.startswith("Ready Made:"):
                boilerplate_action = QAction(boilerplate_name.split(":")[1], self)
                boilerplate_action.triggered.connect(lambda checked, code=boilerplate_code: self.insert_boilerplate(code))
                ready_made_menu.addAction(boilerplate_action)
        
        # Show the context menu
        menu.exec(event.globalPos())

    def insert_boilerplate(self, boilerplate_code):
        # Get the current cursor position
        line, index = self.getCursorPosition()
        
        # Insert the boilerplate code at the current cursor position
        self.insertAt(boilerplate_code, line, index)
        
        # Move the cursor to the beginning of the boilerplate code
        self.setCursorPosition(line, index)

        
    def setup_editor(self):
        """Initialize editor settings and font."""
        font = QFont("Consolas", self.font_size)
        self.setFont(font)

        # Connect the context menu request signal to a custom method
        self.SCI_CONTEXTMENU.connect(self.show_context_menu)
        
        
        # Adjust line number margin settings
        self.setMarginLineNumbers(0, True)
        self.setMarginWidth(0, self.fontMetrics().horizontalAdvance('0000') + 6)
        self.setMarginsBackgroundColor(QColor("#FFFFFF"))  # Set background color of margins
        self.setMarginsForegroundColor(QColor("#808080"))  # Set text color of margins

        self.setEdgeMode(QsciScintilla.EdgeMode.EdgeLine)
        self.setEdgeColumn(80)
        self.setIndentationGuides(True)
        self.setAutoIndent(True)
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)

        lexer = QsciLexerPython()
        self.setLexer(lexer)
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#E0E0E0"))

        # Auto-completion settings
        self.setAutoCompletionSource(QsciScintilla.AutoCompletionSource.AcsAll)
        self.setAutoCompletionThreshold(1)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionUseSingle(QsciScintilla.AutoCompletionUseSingle.AcusNever)

    def set_font_size(self, size):
        """Sets the font size for the editor."""
        if size > 0:  # Ensure the size is valid
            font = self.font()
            font.setPointSize(size)
            self.setFont(font)

    def zoom_in(self):
        """Increases the font size."""
        self.font_size += 2
        self.set_font_size(self.font_size)

    def zoom_out(self):
        """Decreases the font size."""
        if self.font_size > 2:  # Minimum font size limit
            self.font_size -= 2
            self.set_font_size(self.font_size)

    @pyqtSlot()
    def format_code(self):
        """Example formatting: replace tabs with 4 spaces."""
        text = self.text()
        formatted_text = text.replace('\t', '    ')
        self.setText(formatted_text)

    def syncScrollBar(self, value):
        """Syncs horizontal scrollbar."""
        self.horizontalScrollBar().setValue(value)

    def syncEditorScrollBar(self):
        """Syncs the scrollbar from an external QScrollBar."""
        self.horizontalScrollBar().setValue(self.hScrollBar.value())

    def print_editor_content(self):
        """Prints the editor content."""
        try:
            content = self.text()
            print("Editor Content:")
            print(content)
        except Exception as e:
            print(f"Error printing editor content: {e}")

    def keyPressEvent(self, event):
        """Handles zooming via keyboard shortcuts."""
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_Plus:
                self.zoom_in()
                return
            elif event.key() == Qt.Key.Key_Minus:
                self.zoom_out()
                return
        super().keyPressEvent(event)
    
        
class CodeEditor(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("RDF STUDIO")
            self.showMaximized()
            self.setWindowFlags(Qt.WindowType.Window)

            self.setWindowIcon(QIcon(r"E:\RDFTeamWorkspace\icon\rdf_icon.ico"))
            
            self.setGeometry(100, 100, 800, 600)
            self.pc_view = PCView()
            self.mobile_view = MobileView()
            self.terminal = TerminalWidget()
            self.wizard = NewProjectWizard()
            self.open_project_wizard = OpenProjectWizard()
            self.ref_view = ReferenceView()
            self.project_view = ProjectView(self)
            self.open_project_wizard.project_opened.connect(self.project_view.update_project_view)
            self.wizard.project_created.connect(self.project_view.update_project_view)
            self.project_view.file_double_clicked.connect(self.open_file_from_project_view)
            self.project_view.path_changed.connect(self.update_file_view_path)

            self.pc_view_active = False  # Add this line to track PC view state
            
            self.main_layout = QVBoxLayout()
            self.central_widget = QWidget()
            self.central_widget.setLayout(self.main_layout)
            self.setCentralWidget(self.central_widget)

            

            self.base_dir = getattr(sys, '_MEIPASS', os.getcwd())

            self.codeEditor = CustomCodeEditor()
            self.hScrollBar = QScrollBar(Qt.Orientation.Horizontal)

            self.hScrollBar.valueChanged.connect(self.syncScrollBar)
            self.codeEditor.horizontalScrollBar().valueChanged.connect(self.syncEditorScrollBar)

            # Create the toolbar
            self.toolbar = QToolBar("Main Toolbar")

            self.ref_view_action = QAction("Reference View", self)
            
            self.ref_view_action.triggered.connect(self.toggle_ref_view)
           

            # Create Project menu and actions
            project_menu = QMenu("Project", self)
            self.open_project_action = QAction("Open Project", self)
            self.open_project_action.setShortcut(QKeySequence("Ctrl+O"))
            self.open_project_action.triggered.connect(self.open_project)
            self.new_project_action = QAction("Create Project", self)
            self.new_project_action.triggered.connect(self.new_project)
            self.create_file_action = QAction('Create File ', self)
            self.create_file_action.triggered.connect(self.project_view.create_new_file)
            self.save_action = QAction("Save     Ctrl+S ", self)
            self.save_action.triggered.connect(self.save_file)
            self.save_as_action = QAction("Save As", self)
            self.save_as_action.triggered.connect(self.save_as)
            self.export_action = QAction("Export Project", self)
            self.export_action.triggered.connect(self.export_project)


            project_menu.addAction(self.open_project_action)
            self.addAction(self.open_project_action)
            project_menu.addAction(self.new_project_action)
            project_menu.addAction(self.create_file_action)
            project_menu.addAction(self.save_action)
            project_menu.addAction(self.ref_view_action)
            project_menu.addAction(self.save_as_action)
            project_menu.addAction(self.export_action)

            # Create a Project button with the project menu
            project_button = QToolButton(self)
            project_button.setText("Project")
            project_button.setMenu(project_menu)
            project_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            project_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")

                     
            
            
            
            self.toolbar.addWidget(project_button)

            # Create View menu and actions
            view_menu = QMenu("view",self)

            self.project_view_action = QAction(QIcon("project_view.png"), "Reset View", self)
            self.project_view_action.triggered.connect(self.toggle_sidebar)
            self.dark_mode_action = QAction("Dark Mode", self)
            self.dark_mode_action.triggered.connect(self.toggle_dark_theme)
            self.pc_view_action = QAction("PC View", self)
            self.pc_view_action.triggered.connect(self.toggle_pc_view)
            self.file_view_action = QAction("file View", self)
            self.file_view_action.triggered.connect(self.files_view)

            view_menu.addAction(self.dark_mode_action)
            view_menu.addAction(self.project_view_action)
            view_menu.addAction(self.pc_view_action)
            view_menu.addAction(self.file_view_action)

            # Create a View button with the view menu
            view_button = QToolButton(self)
            view_button.setText("View") 
            view_button.setMenu(view_menu)
            view_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            view_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")

            self.toolbar.addWidget(view_button)

            # Create additional toolbar buttons and actions
            self.restart_application_button = QAction("Restart", self)
            self.restart_application_button.triggered.connect(self.restart_application)

            validation_menu = QMenu("Validation", self) 
            try:
                self.validate_project_action = QAction("Validate Project")
                self.validate_project_action.triggered.connect(self.validate_project)
            except Exception as e:
                print(f"{e}")
            self.validate_action = QAction("Validate File")
            self.validate_action.triggered.connect(self.validate_file)
            validation_menu.addAction(self.validate_action)
            validation_menu.addAction(self.validate_project_action)


            validation_button = QToolButton(self)
            validation_button.setText("Validation") 
            validation_button.setMenu(validation_menu)
            validation_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            validation_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")

            self.toolbar.addWidget(validation_button)  

            update_menu = QMenu("update",self)

            self.boilerplate_update_action = QAction("update boilerplate")
            self.boilerplate_update_action.triggered.connect(self.Download_boilerPlate)

            self.ui_Update_action = QAction("Update Ui's")
            self.ui_Update_action.triggered.connect(self.update_Ui)

            self.project_download_action =QAction("Update Projects")
            self.project_download_action.triggered.connect(self.Download_projects)

            update_menu.addAction(self.boilerplate_update_action)
            update_menu.addAction(self.ui_Update_action)
            update_menu.addAction(self.project_download_action)
            


            update_button = QToolButton(self)
            update_button.setText("update")
            update_button.setMenu(update_menu)
            update_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            update_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")
            self.toolbar.addWidget(update_button)
    
            # Add actions directly to the toolbar

            self.toolbar.addAction(self.restart_application_button)            
            

            # Add the toolbar to the main layout

            self.main_layout.addWidget(self.toolbar)

            self.tab_widget = QTabWidget()
            self.tab_widget.setTabsClosable(True)
            self.tab_widget.tabCloseRequested.connect(self.close_tab)
            self.tab_widget.currentChanged.connect(self.update_live_preview)

            self.splitter = QSplitter(Qt.Orientation.Horizontal)
            self.splitter.addWidget(self.project_view)
            self.splitter.addWidget(self.tab_widget)
            self.splitter.setSizes([500, 900])  # Set initial sizes for the project view and tab widget

            self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
            self.main_splitter.addWidget(self.splitter)
            self.main_splitter.addWidget(self.mobile_view)
            self.main_splitter.addWidget(self.pc_view)
            self.main_splitter.setSizes([1000, 300, 300])  # Set initial sizes for the main splitter
            self.pc_view.hide()  # Hide the pc_view initially
            self.main_layout.addWidget(self.main_splitter)

            self.live_preview_timer = QTimer()
            self.live_preview_timer.setInterval(1000)
            self.live_preview_timer.timeout.connect(self.update_live_preview)

            self.save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
            self.save_shortcut.activated.connect(self.save_file)

            self.current_file_path = None
            self.project_view.show()

            self.rules_directory = os.path.join(self.base_dir, 'rules')
            self.rules = {
                "UI": os.path.join(self.rules_directory, "rules_ui.json"),
                "Data": os.path.join(self.rules_directory, "rules_json.json"),
                "BW": os.path.join(self.rules_directory, "rules_bw.json"),
                "BVO": os.path.join(self.rules_directory, "rules_bvo.json"),
                "Action": os.path.join(self.rules_directory, "rules_action.json")
            }
            self.rule_engine = RuleEngine(self.tab_widget, self.rules, self.mobile_view)

            self.dark_theme_enabled = False

            self.installEventFilter(self)
        except Exception as e:
            print(f"Error initializing CodeEditor: {e}")
            logging.error(f"Error initializing CodeEditor: {e}")

    def update_file_view_path(self, path):
        if hasattr(self, 'file_viewer'):
            self.file_viewer.set_path(path)

    def Download_boilerPlate(self):
        self.Downloader = Download()
        self.download_dialog = DownloadDailog(self)
        self.download_dialog.show()
        self.Downloader.update_boilerplate()
        self.download_dialog.accept()

    def Download_projects(self):
        self.download_dialog = DownloadDailog(self)
        self.download_thread = DownloadProjectsThread(self.download_dialog)
        self.download_thread.progress_update.connect(self.download_dialog.update_progress)
        self.download_thread.update_message.connect(self.show_success_message)
        self.download_thread.error_message.connect(self.show_error_message)
        self.download_thread.update_message.connect(self.download_dialog.accept)
        self.download_dialog.show()
        self.download_thread.start()
        
    
    def update_Ui(self):
        self.download_dialog = DownloadDailog(self)
        self.download_thread = DownloadThread(dialog=self.download_dialog)
        self.download_thread.update_message.connect(self.show_success_message)
        self.download_thread.progress_update.connect(self.download_dialog.update_progress)
        self.download_thread.error_message.connect(self.show_error_message)
        self.download_thread.finished.connect(self.download_dialog.accept)  # Close the dialog when done

        self.download_dialog.show()
        self.download_thread.start()

    def show_success_message(self, message):
        QMessageBox.information(self, "Success", message)

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def files_view(self):
        self.file_viewer = FileView()
        current_path = self.project_view.get_path()  # Retrieve the current path
        self.file_viewer.set_path(current_path)  # Pass the path to FileView
        self.file_viewer.show()
        
    def save_as(self):
        try:
            # Get the current project's directory from the ProjectView
            current_project_path = self.project_view.path_line_edit.text()
            
            # Open a dialog to select the directory where the user wants to save the project
            new_folder_path = QFileDialog.getSaveFileName(
                self, "Save Folder As", current_project_path, "Directories (*)"
            )[0]

            if new_folder_path:
                # If the user provides a file name, it may include an extension (e.g., .txt).
                # We need to strip the extension to get just the folder name.
                new_folder_path = os.path.splitext(new_folder_path)[0]

                # Ensure the new folder name does not exist; if it does, we need to remove it
                if os.path.exists(new_folder_path):
                    shutil.rmtree(new_folder_path)

                # Copy the entire project directory to the new location
                shutil.copytree(current_project_path, new_folder_path)

                # Update the project view or any other relevant UI component
                self.project_view.update_project_view(new_folder_path)

                # Log the operation in the terminal
                terminal = self.findChild(TerminalWidget)
                if terminal:
                    terminal.write(f"Saved project folder as: {new_folder_path}\n")
            else:
                terminal = self.findChild(TerminalWidget)
                if terminal:
                    terminal.write("Save As operation was canceled.\n")
        except Exception as e:
            print(f"Error saving folder as: {e}")
            logging.error(f"Error saving folder as: {e}")

    def export_project(self):
        try:
            # Get the current project's directory from the ProjectView
            current_project_path = self.project_view.path_line_edit.text()
            project_name = os.path.basename(current_project_path)

            # Open a dialog to select where the ZIP file should be saved
            zip_file_path, _ = QFileDialog.getSaveFileName(
                self, "Export as ZIP", os.path.join(current_project_path, project_name), "ZIP Files (*.zip);;All Files (*)"
            )

            if zip_file_path:
                # Ensure the selected file has a .zip extension
                if not zip_file_path.endswith(".zip"):
                    zip_file_path += ".zip"

                # Create a ZIP file from the project folder
                shutil.make_archive(os.path.splitext(zip_file_path)[0], 'zip', current_project_path)

                # Log the operation in the terminal
                terminal = self.findChild(TerminalWidget)
                if terminal:
                    terminal.write(f"Exported project as ZIP: {zip_file_path}\n")
            else:
                terminal = self.findChild(TerminalWidget)
                if terminal:
                    terminal.write("Export operation was canceled.\n")
        except Exception as e:
            print(f"Error exporting project as ZIP: {e}")
            logging.error(f"Error exporting project as ZIP: {e}")
    def toggle_ref_view(self, checked):
        if checked:
            self.ref_view.toggle_stay_on_top(True)
        else:
            self.ref_view.toggle_stay_on_top(False)
             
    def toggle_pc_view(self):
        if not self.pc_view_active:
            # Activate PC view
            self.pc_view.show()
            self.mobile_view.hide()
            
            # Store current sizes
            self.stored_sizes = self.main_splitter.sizes()
            
            # Set the width of code editor, terminal, and project view to 0
            new_sizes = [0, 0, self.main_splitter.width()]
            self.main_splitter.setSizes(new_sizes)
            
            self.pc_view_active = True
        else:
            # Deactivate PC view
            self.pc_view.hide()
            self.mobile_view.show()
            
            # Restore previous sizes
            self.main_splitter.setSizes(self.stored_sizes)
            
            self.pc_view_active = False    
            
    def toggle_sidebar(self):
        try:
            if self.project_view.isHidden():
                self.project_view.show()
            else:
                self.project_view.hide()
        except Exception as e:
            print(f"Error toggling sidebar: {e}")
            logging.error(f"Error toggling sidebar: {e}")

    def close_tab(self, index):
        try:
            self.tab_widget.removeTab(index)
        except Exception as e:
            print(f"Error closing tab: {e}")
            logging.error(f"Error closing tab: {e}")

    def close_all_tabs(self):
        try:
            while self.tab_widget.count() > 0:
                self.tab_widget.removeTab(0)
        except Exception as e:
            QMessageBox.warning(self, f"Error closing tabs: {e}")
            logging.warning(f"Error closing tabs: {e}")

    def new_project_workspace(self):
        try:
            if self.tab_widget.count() == 0:
                self.project_view.select_workspace()
            else:
                self.close_all_tabs()
                self.mobile_view.clear_view()
                self.pc_view.clear_view()
                self.project_view.select_workspace()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating new project workspace: {e}")
            logging.error(f"Error creating new project workspace: {e}")

    def open_project(self):
        try:
            if self.tab_widget.count() == 0:
                self.open_project_wizard.exec()
            else:
                self.close_all_tabs()
                self.mobile_view.clear_view()
                self.pc_view.clear_view()
                self.mobile_view.clear_url_display()
                self.open_project_wizard.exec()
        except Exception as e:
            print(f'error opening a wizard{e}')
    

    def new_project(self):
        try:
            self.wizard.exec()
        except Exception as e:
            print(f"Error creating new project: {e}")
            logging.error(f"Error creating new project: {e}")

    def load_file(self, index: QModelIndex):
        try:
            if self.sidebar_model.isDir(index):
                return
            file_path = self.sidebar_model.filePath(index)
            self.open_file_in_new_tab(file_path)
        except Exception as e:
            print(f"Error loading file: {e}")
            logging.error(f"Error loading file: {e}")

    def save_file(self):
        try:
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                editor = current_widget.findChild(QsciScintilla)
                if editor and hasattr(current_widget, 'file_path') and current_widget.file_path:
                    normalized_file_path = os.path.normpath(current_widget.file_path)
                    temp_file_path = current_widget.file_path + ".tmp"

                    with open(temp_file_path, 'w') as temp_file:
                        temp_file.write(editor.text())
                        temp_file.flush()
                        os.fsync(temp_file.fileno())

                    os.replace(temp_file_path, current_widget.file_path)  # Safely replace the original file

                    terminal = current_widget.findChild(TerminalWidget)
                    if terminal:
                        terminal.write(f"Saved file: {normalized_file_path}\n")

                    # Reload the file preview
                    self.mobile_view.load_file_preview(current_widget.file_path)
                    self.pc_view.load_file_preview(current_widget.file_path)

                else:
                    terminal = current_widget.findChild(TerminalWidget)
                    if terminal:
                        terminal.write("No file opened to save.\n")
            else:
                print("No current widget to save.")
        except Exception as e:
            print(f"Error saving file: {e}")
            logging.error(f"Error saving file: {e}")

    def toggle_live_preview(self, checked):
        try:
            if checked:
                self.live_preview_timer.start()
            else:
                self.live_preview_timer.stop()
        except Exception as e:
            print(f"Error toggling live preview: {e}")
            logging.error(f"Error toggling live preview: {e}")

    def update_live_preview(self):
        try:
            current_widget = self.tab_widget.currentWidget()
            if current_widget:
                self.mobile_view.load_file_preview(current_widget.file_path)
                self.pc_view.load_file_preview(current_widget.file_path)
        except Exception as e:
            print(f"Error updating live preview: {e}")
            logging.error(f"Error updating live preview: {e}")

    def validate_file(self):
        self.rule_engine.validate_file()

    def validate_project(self):
        try:
            project_path, rules_mapping, rules_dict = self.project_view.initialize_validator()
            files_with_errors = self.project_view.validate_files(project_path, rules_mapping, rules_dict)
            self.project_view.show_results(files_with_errors)

        except Exception as e:
            QMessageBox.critical(None, "Error", str(e))

    def show_progress_dialog(self, message="Opening file...", minimum=0, maximum=100):
        progress_dialog = QProgressDialog(message, None, minimum, maximum)
        progress_dialog.setWindowTitle("Please Wait")
        progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)  # Use Qt.WindowModality for PyQt6
        progress_dialog.setAutoClose(False)
        progress_dialog.setAutoReset(False)
        progress_dialog.setValue(minimum)
        return progress_dialog

    def open_file_from_project_view(self, file_path):
        progress_dialog = self.show_progress_dialog()
        try:
            self.open_file_in_new_tab(file_path,progress_dialog)
        except Exception as e:
            print(f"Error opening file from project view: {e}")
            logging.error(f"Error opening file from project view: {e}")
        finally:
            progress_dialog.close()
    
    def open_file_in_new_tab(self, file_path,progress_dialog):
        try:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i).file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    progress_dialog.setValue(100)
                    return
            progress_dialog.setValue(20)

            tab = QWidget()
            tab.file_path = file_path
            layout = QVBoxLayout()
            editor = CustomCodeEditor()
            editor.setFont(QFont("Consolas", 12))
            terminal = TerminalWidget()

            
            
            publish_button = QPushButton("Upload")
            publish_button.setStyleSheet("background-color:red;color:white;font-weight:bold;border-radius:5px;padding:5px 10px")
            publish_button.clicked.connect(self.on_publish)

            format_button = QPushButton("Format Code")
            format_button.clicked.connect(lambda: self.format_current_code(editor, file_path))
            format_button.setStyleSheet("background-color:#f0f0f0;border-radius:5px;padding:4px 10px;border:1px solid #ccc")
            
            # Create an instance of ReferenceView
            

            # Add a button to the toolbar to show/hide the reference view
            

            search_tab_layout = QHBoxLayout()
            search_tab_layout.addStretch()
            
            search_tab_layout.addWidget(publish_button)
            search_tab_layout.addWidget(format_button)  # Add the format button to the layout
            layout.addLayout(search_tab_layout)

            splitter = QSplitter(Qt.Orientation.Vertical)
            splitter.addWidget(editor)
            splitter.addWidget(terminal)
            splitter.setSizes([int(self.height() * 0.75), int(self.height() * 0.25)])

            layout.addWidget(splitter)

            button_layout = QHBoxLayout()
            toggle_button = QPushButton("▲")
            toggle_button.setFixedSize(30, 30)
            button_layout.addWidget(toggle_button)
            button_layout.addStretch()
            layout.addLayout(button_layout)

            tab.setLayout(layout)
            self.tab_widget.addTab(tab, os.path.basename(file_path))
            self.tab_widget.setCurrentWidget(tab)

            progress_dialog.setValue(60)

            toggle_button.clicked.connect(lambda: self.toggle_terminal(splitter, toggle_button))

            try:
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']

                progress_dialog.setValue(80)

                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    file_contents = file.read()
                    editor.setText(file_contents)
                    correct_file_path = os.path.normpath(file_path)
                    terminal.write(f"Loaded file: {correct_file_path}\n")
                    self.rule_engine.validate_and_apply_rules(file_path)

                    extension = os.path.splitext(file_path)[1][1:]
                    language = self.get_language_from_extension(extension)
                    lexer = self.get_lexer_for_language(language)
                    editor.setLexer(lexer)

                    autocompleter = AutoCompleter(lexer)
                    autocompleter.add_custom_apis([
                        "<table class=\"section\">", "<tr>", "<td>", "</td>", "</tr>", "</table>",
                        "<td style=\"width: 90%;\">", "getYYY()", "yyyBVO.php",
                        "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA",
                        "inline", "width", "height", "background-color", "color"
                    ])
                    autocompleter.prepare()

                editor.setAutoCompletionThreshold(1)
                editor.setAutoCompletionCaseSensitivity(False)
                editor.setAutoCompletionReplaceWord(False)

            except Exception as e:
                print(f"Failed to open file: {e}")
            progress_dialog.setValue(100)

        except Exception as e:
            print(f"Failed to open new tab: {e}")

    def format_current_code(self, editor, file_path):
        try:
            input_code = editor.text()
            formatted_code = CodeFormatter.format_code(file_path, input_code)
            editor.setText(formatted_code)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to format code: {e}")

    

    def validate_ftp_credentials(self, server, username, password):
        print("validating ftp credentials")
        try:
            with FTP(server, timeout=160) as ftp:
                ftp.login(user=username, passwd=password)
            return True
        except error_perm as e:
            print(f"FTP login failed: {e}")
            return False
    
    def on_publish(self):
        current_index = self.tab_widget.currentIndex()
        current_tab = self.tab_widget.widget(current_index)

        if not current_tab.file_path:
            QMessageBox.warning(self, 'Error', 'No file selected for upload.')
            return

        wizard = PublishWizard(current_tab, self)
        result = wizard.exec()

        # Check if publishing has started before deciding to show cancellation
        if hasattr(self, 'publishing_started') and self.publishing_started:
            # The publishing has started, so do not show cancellation message
            return

        if result == QWizard.DialogCode.Rejected:
            # Show cancellation message only if the user explicitly cancels
            QMessageBox.information(self, 'Cancelled', 'Publishing cancelled.')



    def get_language_from_extension(self, extension):
        extension_map = {
            'py': 'python',
            'html': 'html',
            'js': 'javascript',
            'css': 'css',
            'php': 'php',
            'json': 'json',
        }
        return extension_map.get(extension, 'python')

    def get_lexer_for_language(self, language):
        if language == 'python':
            return QsciLexerPython()
        elif language == 'html':
            return QsciLexerHTML()
        elif language == 'javascript':
            return QsciLexerJavaScript()
        elif language == 'css':
            return QsciLexerCSS()
        elif language == 'php':
            return QsciLexerHTML()  # QsciLexerHTML can handle PHP
        elif language == 'json':
            return QsciLexerJSON()  # You may need to import QsciLexerJSON
        else:
            return QsciLexerPython()
        
    def toggle_terminal(self, splitter, toggle_button):
        try:
            if splitter.sizes()[1] == 0:
                splitter.setSizes([int(self.height() * 0.75), int(self.height() * 0.25)])
                toggle_button.setText("▼")
            else:
                splitter.setSizes([int(self.height() * 0.75), 0])
                toggle_button.setText("▲")
        except Exception as e:
            print(f"Error toggling terminal: {e}")
            logging.error(f"Error toggling terminal: {e}")

    def set_highlighter_language(self, file_path, highlighter):
        try:
            extension = os.path.splitext(file_path)[1][1:]
            if extension == "html":
                highlighter.set_language("html")
            elif extension == "js":
                highlighter.set_language("javascript")
            elif extension == "php":
                highlighter.set_language("php")
            elif extension == "json":
                highlighter.set_language("json")
            highlighter.rehighlight()
        except Exception as e:
            QMessageBox.critical(self, "Syntax Highlighting Error", f"An error occurred while setting syntax highlighting: {str(e)}")
            logging.error(f"Error setting syntax highlighting: {e}")

    def toggle_dark_theme(self):
        try:
            if self.dark_theme_enabled:
                QApplication.instance().setPalette(QApplication.style().standardPalette())
            else:
                DarkTheme.apply()
            self.dark_theme_enabled = not self.dark_theme_enabled
        except Exception as e:
            print(f"Error toggling dark theme: {e}")
            logging.error(f"Error toggling dark theme: {e}")
    
    def syncScrollBar(self, value):
        try:
            self.codeEditor.horizontalScrollBar().setValue(value)
        except Exception as e:
            print(f"Error syncing scroll bar: {e}")
            logging.error(f"Error syncing scroll bar: {e}")
    
    def syncEditorScrollBar(self):
        try:
            self.hScrollBar.setValue(self.codeEditor.horizontalScrollBar().value())
        except Exception as e:
            print(f"Error syncing editor scroll bar: {e}")
            logging.error(f"Error syncing editor scroll bar: {e}")

    def restart_application(self):
        try:
            reply = QMessageBox.question(self, 'Restart Application', 
                                        'Do you want to restart the application?',
                                        QMessageBox.StandardButton.Yes | 
                                        QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                # Log the restart attempt
                logging.info("Restarting the application...")
                
                # Quit the current application
                QApplication.instance().quit()

                # Restart the application using os.execl
                os.execl(sys.executable, sys.executable, *sys.argv)
            else:
                logging.info("Restart cancelled by user.")
        except Exception as e:
            logging.error(f"Error restarting application: {e}")


    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()



