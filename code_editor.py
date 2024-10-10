import re
import json,requests
import os, sys
import logging,chardet,subprocess
import traceback
from ftplib import FTP,error_perm
from datetime import datetime, timedelta
from urllib.parse import urlsplit
import urllib.parse
import graphviz
from io import BytesIO
from PIL import Image

import time
import shutil
from pc_view import PCView
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from PyQt6.QtGui import QSyntaxHighlighter,QIcon,QImage
from PyQt6.Qsci import QsciDocument
from PyQt6.QtWidgets import QWizard,QWizardPage,QScrollArea, QDialog,QPlainTextEdit,QProgressDialog, QProgressBar,QInputDialog,QLabel, QMainWindow,QLineEdit,QMenu, QVBoxLayout, QWidget, QSplitter, QDialogButtonBox, QTreeView, QToolBar, QFileDialog, QToolButton, QTabWidget, QApplication, QMessageBox, QPushButton, QTextEdit, QScrollBar, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import  QTextCharFormat,QAction, QPixmap, QFileSystemModel, QIcon, QFont, QPainter, QColor, QTextFormat, QTextCursor, QKeySequence, QShortcut
from PyQt6.QtCore import Qt,QEvent, QModelIndex, QSettings,QTimer, QDir,QThread, pyqtSlot, QSize, QRect, QProcess, QPoint, pyqtSignal,QCoreApplication
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerHTML, QsciLexerJavaScript, QsciLexerCSS

from terminal_widget import TerminalWidget
from mobile_view import MobileView
from project_view import ProjectView
from new_project import NewProjectWizard
from theme import DarkTheme
from PyQt6.Qsci import QsciAbstractAPIs, QsciScintilla, QsciDocument,QsciLexerJSON,QsciLexerCPP
from autocompleter import AutoCompleter
from Rule_Engine import RuleEngine
from code_formatter import CodeFormatter
from OpenProject import OpenProjectWizard
from ref_view import ReferenceView
from publish import PublishWizard
from AI import CodeFormatter,ImproveAlgorithm,CommentAdder,ImprovedCode,CodeImprover
from file_view import FileView
from downloads import Download,DownloadUIThread,DownloadDailog,DownloadProjectsThread,DownloadFeaturesThread

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
        elif language == "php":
            self.editor.setLexer(QsciLexerCPP())
            
    
    def autoCompletionSource(self, source):
        return self.highlighter_rules.get(source, [])


class CustomCodeEditor(QsciScintilla):
    def __init__(self):
        try:
            super().__init__()
            self.font_size = 12  # Default font size
            self.setup_editor()
            self.SCI_CONTEXTMENU = QMenu(self)
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
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        boilerplate_dir = os.path.join(base_dir, 'Boilerplates')

        # Check if the Boilerplates directory exists
        if not os.path.exists(boilerplate_dir):
            QMessageBox.warning(self, "Boilerplates Not Found", "The Boilerplates folder was not found. Please update Boilerplates from the toolbar.")
            return

        menu = QMenu(self)
        insert_boilerplate_menu = QMenu("Insert Boilerplate", self)
        menu.addMenu(insert_boilerplate_menu)

        categories = {
            "Easy HTML Tags": os.path.join(boilerplate_dir, "easy_html_tags"),
            "Complex HTML Tags": os.path.join(boilerplate_dir, "complex_html_tags"),
            "Ready Made": os.path.join(boilerplate_dir, "ready_made")
        }

        error_folders = []

        for category, folder_path in categories.items():
            category_menu = QMenu(category, insert_boilerplate_menu)
            insert_boilerplate_menu.addMenu(category_menu)

            if not os.path.exists(folder_path):
                error_folders.append(category)
                continue

            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            
            if not json_files:
                error_folders.append(category)
                continue

            for json_file in json_files:
                try:
                    with open(os.path.join(folder_path, json_file), 'r') as f:
                        boilerplate_data = json.load(f)
                    
                    for boilerplate_name, boilerplate_code in boilerplate_data.items():
                        boilerplate_action = QAction(boilerplate_name, self)
                        boilerplate_action.triggered.connect(lambda checked, code=boilerplate_code: self.insert_boilerplate(code))
                        category_menu.addAction(boilerplate_action)
                except json.JSONDecodeError:
                    error_folders.append(category)

        if error_folders:
            error_message = f"Error in Boilerplate file(s). The following folder(s) have issues: {', '.join(error_folders)}. Contact Server Admin."
            QMessageBox.critical(self, "Error", error_message)

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

        # Enable line numbers in the first margin (Margin 0)
        self.setMarginType(0, QsciScintilla.MarginType.NumberMargin)  # Margin type for line numbers
        self.setMarginLineNumbers(0, True)  # Enable line numbers

        # Adjust the margin width dynamically based on the number of lines in the editor
        self.setMarginWidth(0, "0000")  # Adjust width for up to 9999 lines

        # Set custom colors for the margin where line numbers appear
        self.setMarginsBackgroundColor(QColor("#F0F0F0"))  # Light gray background
        self.setMarginsForegroundColor(QColor("#000000"))  # Black text for line numbers

        # Set indentation guides and auto-indentation
        self.setIndentationGuides(True)
        self.setAutoIndent(True)

        # Set no line wrapping
        self.setWrapMode(QsciScintilla.WrapMode.WrapNone)

        # Enable syntax highlighting (you can change the lexer for different languages)
        lexer = QsciLexerHTML()
        self.setLexer(lexer)

        # Set custom color and style for indentation guides
        # QsciScintilla uses style index 16 for indentation guides
        lexer.setColor(QColor("#D3D3D3"), QsciLexerHTML.Default)  # Use 'Default' or another valid style index for whitespace
        lexer.setFont(QFont("Consolas", self.font_size), QsciLexerHTML.Default)  # Set the font for the default style
  # Set the font for the guides (affects line thickness)

        # Enable highlighting for the current line
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#FFEB3B"))

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
    urlGenerated = pyqtSignal(str)
    def __init__(self,email):
        try:
            super().__init__()
            self.setWindowTitle("RDF STUDIO")
            self.showMaximized()
            self.setWindowFlags(Qt.WindowType.Window)
            self.email = email
            self.start_time = None
            self.end_time = None
            self.setWindowState(Qt.WindowState.WindowMaximized)
            self.start_timer()
            self.installEventFilter(self)

            self.setWindowIcon(QIcon(r"E:\RDFTeamWorkspace-exe\icon\rdf_icon.ico"))
            
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
            self.urlGenerated.connect(self.mobile_view.load_time_tracking_url)

            api_key = "AIzaSyC9yY9s7dH-TAvszp-skbdUlegWe9h3Z2E"
            api_key_2 = "AIzaSyCI3ULZp4GBUnsplCvP-J-r5A4DkGDDbFs"
            api_key_3 = "AIzaSyD2JD4H3CQDF-nal_XGkqfVKhru4rNciiE"
            self.code_formatter = CodeFormatter(api_key)
            self.improve_algorithm =ImproveAlgorithm(api_key_2)
            self.comment_adder = CommentAdder(api_key_3)
            self.improvecode = ImprovedCode(api_key)
            self.code_improver = CodeImprover(api_key)

            self.pc_view_active = False  # Add this line to track PC view state
            self.update_thread = None
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

            self.boilerplate_update_action = QAction("Update Boilerplate")
            self.boilerplate_update_action.triggered.connect(self.Download_boilerPlate)

            self.ui_Update_action = QAction("Update Ui's")
            self.ui_Update_action.triggered.connect(self.update_Ui)

            self.project_download_action =QAction("Update Projects")
            self.project_download_action.triggered.connect(self.Download_projects)

            self.project_Features_action =QAction("Update Features")
            self.project_Features_action.triggered.connect(self.Download_Features)

            self.exe_update_action =QAction("Update Exe")
            self.exe_update_action.triggered.connect(self.check_for_updates)

            update_menu.addAction(self.boilerplate_update_action)
            update_menu.addAction(self.ui_Update_action)
            update_menu.addAction(self.project_download_action)
            update_menu.addAction(self.project_Features_action)
            update_menu.addAction(self.exe_update_action)
            


            update_button = QToolButton(self)
            update_button.setText("Update")
            update_button.setMenu(update_menu)
            update_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            update_button.setStyleSheet("QToolButton::menu-indicator { image: none; }")
            self.toolbar.addWidget(update_button)
    
            # Add actions directly to the toolbar
            AI_menu = QMenu("AI menu",self)

            self.code_format_action = QAction("Code Format",self)
            self.code_format_action.triggered.connect(self.on_format_code_clicked)

            self.Add_Comment_Action = QAction("Add Comments")
            self.Add_Comment_Action.triggered.connect(self.on_comment_code_clicked)

            self.Add_Code_Quality_Action = QAction("Add code Quality",self)

            self.Imrove_Variable_Names_Action = QAction("Improve Variable and function names",self)
            self.Imrove_Variable_Names_Action.triggered.connect(self.on_improve_code_clicked)
            # self.Improve_Code_Quality = QAction("Improve Code Quality",self)
            self.suggest_an_improved_Algorithm_Action = QAction("Suggest an improved algorithm", self)
            self.suggest_an_improved_Algorithm_Action.triggered.connect(self.on_improve_algorithm_clicked)
             # Add the actions for flowchart, pseudocode, algorithm
            self.flowchart_action = QAction("Generate Flowchart", self)
            self.flowchart_action.triggered.connect(self.on_generate_flowchart_clicked)

            self.pseudocode_action = QAction("Generate Pseudocode", self)
            self.pseudocode_action.triggered.connect(self.on_generate_pseudocode_clicked)

            self.algorithm_action = QAction("Generate Algorithm", self)
            self.algorithm_action.triggered.connect(self.on_generate_algorithm_clicked)

            AI_menu.addAction(self.code_format_action)
            AI_menu.addAction(self.Add_Comment_Action)
            AI_menu.addAction(self.Add_Code_Quality_Action)
            AI_menu.addAction(self.Imrove_Variable_Names_Action)
            AI_menu.addAction(self.flowchart_action)
            AI_menu.addAction(self.pseudocode_action)
            AI_menu.addAction(self.algorithm_action)
            AI_menu.addAction(self.suggest_an_improved_Algorithm_Action)



            AI_Power_Button = QToolButton(self)
            AI_Power_Button.setText("AI Power") 
            AI_Power_Button.setMenu(AI_menu)
            AI_Power_Button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
            AI_Power_Button.setStyleSheet("QToolButton::menu-indicator { image: none; }")

            self.toolbar.addWidget(AI_Power_Button)

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

    def start_timer(self):
        self.start_time = datetime.now()
        print(f"[DEBUG] Timer started at {self.start_time}")  # Debug statement

    def stop_timer(self):
        if self.start_time:
            self.end_time = datetime.now()
            print(f"[DEBUG] Timer stopped at {self.end_time}")  # Debug statement
            self.send_time_data(self.start_time, self.end_time)
            self.start_time = None

    def send_time_data(self, start_time, end_time):
        encoded_email = urllib.parse.quote(self.email)
        start_timestamp = int(start_time.timestamp())
        end_timestamp = int(end_time.timestamp())

        url = f"https://takeitideas.in/RDFSTUDIO/UserTimeTracking/timemanagement.php?email={encoded_email}&startTime={start_timestamp}&endTime={end_timestamp}"
        print(f"[DEBUG] Sending data to URL: {url}")  # Debug statement

        try:
            response = requests.get(url)
            print(f"[DEBUG] Server response: {response.text} (Status code: {response.status_code})")  # Debug statement
            if response.status_code == 200:
                print(f"[DEBUG] Time data sent successfully")
                self.urlGenerated.emit(url)
            else:
                print(f"[DEBUG] Failed to send time data: {response.status_code}")
        except requests.RequestException as e:
            print(f"[DEBUG] Error sending time data: {e}")

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if self.windowState() & Qt.WindowState.WindowMinimized:
                self.stop_timer()
            elif self.windowState() & Qt.WindowState.WindowMaximized:
                self.start_timer()
        elif event.type() == QEvent.Type.Close:
            self.stop_timer()

        return super().eventFilter(source, event)

    def check_for_updates(self):
        self.update_thread = UpdateCheckThread()
        self.update_thread.updateAvailable.connect(self.on_update_available)
        self.update_thread.noUpdateAvailable.connect(self.on_no_update)
        self.update_thread.errorOccurred.connect(self.on_update_error)
        self.update_thread.finished.connect(self.cleanup_thread)  # Clean up after thread finishes
        self.update_thread.start()

    def cleanup_thread(self):
        self.update_thread = None 
        
    def on_update_available(self, server_version):
        self.download_update(server_version)

    def on_no_update(self):
        QMessageBox.information(self, "Update", "No update is available.")

    def on_update_error(self, error_message):
        QMessageBox.critical(self, "Update Error", f"Error checking updates: {error_message}")

    def download_update(self, server_version):
        updates_txt_url = 'https://takeitideas.in/RDFSTUDIO/updates.txt'
        exe_download_url = 'http://takeitideas.in/RDFSTUDIO/RDF STUDIO.exe'

        exe_dir = os.path.dirname(sys.executable)
        
        # Paths for the final files
        updates_txt_path = os.path.join(exe_dir, 'updates.txt')
        temp_exe_download_path = os.path.join(exe_dir, 'RDF STUDIO_temp.exe')

        # Function to handle the download of the exe file after the txt file is downloaded
        def on_txt_download_finished():
            # Now start downloading the RDF STUDIO.exe file
            self.download_thread = DownloadThread(exe_download_url, temp_exe_download_path, self)
            self.download_thread.progressUpdated.connect(self.on_download_progress)
            self.download_thread.downloadFinished.connect(self.on_download_finished)
            self.download_thread.errorOccurred.connect(self.on_download_error)
            self.download_thread.start()

        # Create and start the thread to download the updates.txt file
        self.update_thread = DownloadThread(updates_txt_url, updates_txt_path, self)
        self.update_thread.progressUpdated.connect(self.on_download_progress)
        self.update_thread.downloadFinished.connect(on_txt_download_finished)
        self.update_thread.errorOccurred.connect(self.on_download_error)

        # Initialize the progress dialog in the main thread
        self.progress_dialog = QProgressDialog("Downloading update...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Update")
        self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self.progress_dialog.canceled.connect(self.on_cancel_download)
        self.progress_dialog.show()

        # Start by downloading the updates.txt file
        self.update_thread.start()



    def on_download_progress(self, value):
        # Update the progress dialog value
        self.progress_dialog.setValue(value)

    def on_cancel_download(self):
        if self.download_thread.isRunning():
            self.download_thread.requestInterruption()

    def on_download_finished(self, temp_download_path):
        self.progress_dialog.close()
        QMessageBox.information(self, "Download Complete", "The update has been downloaded successfully.")
        self.replace_old_exe(temp_download_path)

    def on_download_error(self, error_message):
        self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"Failed to download update: {error_message}")


    def replace_old_exe(self, temp_exe_path):
        exe_dir = os.path.dirname(sys.executable)
        old_exe_name = self.get_executable_name(exe_dir)

        if not old_exe_name:
            QMessageBox.critical(self, "Error", "No matching executable found for replacement.")
            return

        old_exe_path = os.path.join(exe_dir, old_exe_name)
        backup_exe_path = os.path.join(exe_dir, f"{old_exe_name}_backup.exe")

        # Rename old executable to backup
        try:
            os.rename(old_exe_path, backup_exe_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to rename old executable: {e}")
            return

        # Move the new executable to the original location
        try:
            shutil.move(temp_exe_path, old_exe_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to move new executable: {e}")
            # Restore old executable if replacement fails
            if os.path.exists(backup_exe_path):
                os.rename(backup_exe_path, old_exe_path)
            return

        # Notify the user
        QMessageBox.information(self, "Update", "Update installed successfully. Please restart the application.")
        

    def get_executable_name(self, exe_dir):
        for filename in os.listdir(exe_dir):
            if filename.endswith(".exe") and "RDF" in filename:
                return filename
        return None

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

    def Download_Features(self):
        self.download_dialog = DownloadDailog(self)
        self.download_thread = DownloadFeaturesThread(self.download_dialog)
        self.download_thread.progress_update.connect(self.download_dialog.update_progress)
        self.download_thread.update_message.connect(self.show_success_message)
        self.download_thread.error_message.connect(self.show_error_message)
        self.download_thread.update_message.connect(self.download_dialog.accept)
        self.download_dialog.show()
        self.download_thread.start()
        
    
    def update_Ui(self):
        self.download_dialog = DownloadDailog(self)
        self.download_thread = DownloadUIThread(dialog=self.download_dialog)
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

            search_tab_layout = QHBoxLayout()
            search_tab_layout.addStretch()
            
            search_tab_layout.addWidget(publish_button)  
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

    def on_improved_code_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                file_path = current_widget.file_path
                self.improve_current_code(editor, file_path)
    
    def improve_current_code(self, editor, file_path):
        try:
            input_code = editor.text()
            language = self.get_language_from_extension(file_path)
            
            if language == "Unknown":
                QMessageBox.warning(self, "Warning", f"Could not determine the language for {file_path}")
                return

            improved_code = self.improvecode.improve_code(input_code)
            editor.setText(improved_code)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"failed to improve code: {e}")


    def on_comment_code_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                file_path = current_widget.file_path
                self.add_comments_to_code(editor, file_path)

    def add_comments_to_code(self, editor, file_path):
        try:
            input_code = editor.text()
            if not input_code:
                QMessageBox.warning(self, "Warning", "No code to add comments!")
                return

            language = self.get_language_from_extension(file_path)
            if language == "Unknown":
                QMessageBox.warning(self, "Warning", f"Could not determine the language for {file_path}")
                return
            
            commented_code = self.comment_adder.add_comments(input_code)
            editor.setText(commented_code)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add comments: {e}")

    def on_generate_flowchart_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                code = editor.text()  # Get the code from the editor
                self.generate_flowchart(code)

    def on_generate_pseudocode_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                code = editor.text()  # Get the code from the editor
                self.generate_pseudocode(code)

    def on_generate_algorithm_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                code = editor.text()  # Get the code from the editor
                self.generate_algorithm(code)


    def generate_flowchart(self, code):
        flowchart_dot = self.code_to_flowchart_dot(code)
        if flowchart_dot:
            self.display_flowchart(flowchart_dot)

    def code_to_flowchart_dot(self, code):
        # Simple DOT format flowchart generation
        lines = code.splitlines()
        dot = graphviz.Digraph()
        dot.node('Start', 'Start')
        previous_node = 'Start'
        
        for i, line in enumerate(lines):
            current_node = f'node{i}'
            if "if" in line:
                dot.node(current_node, f'Decision: {line.strip()}')
                dot.edge(previous_node, current_node)
                previous_node = current_node
            elif "for" in line or "while" in line:
                dot.node(current_node, f'Loop: {line.strip()}')
                dot.edge(previous_node, current_node)
                previous_node = current_node
            else:
                dot.node(current_node, f'Process: {line.strip()}')
                dot.edge(previous_node, current_node)
                previous_node = current_node

        dot.node('End', 'End')
        dot.edge(previous_node, 'End')
        
        return dot

    def generate_pseudocode(self, code):
        pseudocode = self.code_to_pseudocode(code)
        self.show_message(pseudocode, "Pseudocode")

    def generate_algorithm(self, code):
        algorithm = self.code_to_algorithm(code)
        self.show_message(algorithm, "Algorithm")

    def on_improve_algorithm_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                if not editor:
                    QMessageBox.warning(self, "Error", "No code editor found to improve the algorithm.")
                    return
                file_path = current_widget.file_path
                self.improve_current_algo(editor, file_path)


    def improve_current_algo(self, editor, file_path):
        try:
            input_code = editor.text()
            language = self.get_language_from_extension(file_path)
            
            if language == "Unknown":
                QMessageBox.warning(self, "Warning", f"Could not determine the language for {file_path}")
                return

            improved_algorithm = self.improve_algorithm.improve_algorithm(input_code)
            editor.setText(improved_algorithm)
    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to improve algo: {e}")

    def show_message(self, message, title):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def code_to_pseudocode(self, code):
        lines = code.splitlines()
        pseudocode = ""
        for line in lines:
            if "{" in line or "}" in line:
                continue
            pseudocode += line.strip() + "\n"
        return pseudocode.strip()
    
    def code_to_algorithm(self, code):
        lines = code.splitlines()
        algorithm = "Algorithm Steps:\n"
        step_count = 1
        for line in lines:
            if "{" in line or "}" in line:
                continue
            algorithm += f"Step {step_count}: " + line.strip() + "\n"
            step_count += 1
        return algorithm.strip()
    
    def display_flowchart(self, flowchart):
        try:
            # Render the flowchart directly into memory (byte array)
            flowchart_png = flowchart.pipe(format='png')
        
            # Load the byte data into an image (using Pillow)
            image = Image.open(BytesIO(flowchart_png))
            image_data = image.convert("RGBA")  # Ensure it's in RGBA format
        
            # Convert the image to QImage
            width, height = image_data.size
            qimage = QImage(image_data.tobytes(), width, height, QImage.Format.Format_RGBA8888)
        
            # Convert QImage to QPixmap
            pixmap = QPixmap.fromImage(qimage)
        
            # Show the flowchart in the wizard
            self.show_flowchart_wizard(pixmap)
    
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def show_flowchart_wizard(self, pixmap):
        wizard = QWizard(self)
        wizard.setWindowTitle("Flowchart Wizard")
        
        # Create a wizard page to hold the flowchart
        page = QWizardPage()
        page.setTitle("Flowchart")
        
        # Create a QLabel to display the flowchart image
        label = QLabel()
        label.setPixmap(pixmap)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create a QScrollArea to allow scrolling if the image is large
        scroll_area = QScrollArea()
        scroll_area.setWidget(label)
        scroll_area.setWidgetResizable(True)  # Automatically adjust the scroll area for resizing
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Center the image in the scroll area
        
        # Set the scroll area in the layout of the wizard page
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        page.setLayout(layout)
        
        # Add the page to the wizard
        wizard.addPage(page)
        
        # Show the wizard
        wizard.exec()

    def on_improve_code_clicked(self):
        current_tab = self.tab_widget.currentWidget()
        if current_tab is not None and hasattr(current_tab, 'file_path'):
            code_editor = current_tab.findChild(CustomCodeEditor)
            if code_editor:
                current_file_path = current_tab.file_path
                self.improve_code_names(code_editor, current_file_path)


    def improve_code_names(self, code_editor, current_file_path):
        try:
            unrefined_code = code_editor.text()
            programming_language = self.get_language_from_extension(current_file_path)

            if programming_language == "Unknown":
                QMessageBox.warning(self, "Warning", f"Could not determine the language for {current_file_path}")
                return

            improved_code = self.code_improver.improve_names(unrefined_code)
            code_editor.setText(improved_code)

        except Exception as error_message:
            QMessageBox.critical(self, "Error", f"Failed to improve code: {error_message}")
        
    def on_format_code_clicked(self):
        current_widget = self.tab_widget.currentWidget()
        if current_widget is not None and hasattr(current_widget, 'file_path'):
            editor = current_widget.findChild(CustomCodeEditor)
            if editor:
                file_path = current_widget.file_path
                self.format_current_code(editor, file_path)


    def format_current_code(self, editor, file_path):
        try:
            input_code = editor.text()
            language = self.get_language_from_extension(file_path)
            
            if language == "Unknown":
                QMessageBox.warning(self, "Warning", f"Could not determine the language for {file_path}")
                return

            formatted_code = self.code_formatter.format_code(input_code)
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
            return QsciLexerCPP()  # QsciLexerHTML can handle PHP
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

class UpdateCheckThread(QThread):
    updateAvailable = pyqtSignal(str)
    noUpdateAvailable = pyqtSignal()
    errorOccurred = pyqtSignal(str)

    def run(self):
        server_url = 'http://takeitideas.in/RDFSTUDIO/updates.txt'
        exe_dir = os.path.dirname(sys.executable)
        local_update_file = os.path.join(exe_dir, 'updates.txt')

        try:
            # Fetch the server version
            server_response = requests.get(server_url)
            server_response.raise_for_status()  # Ensure we got a valid response
            server_version = server_response.text.strip()

            # Read the local version
            if os.path.exists(local_update_file):
                with open(local_update_file, 'r') as file:
                    local_version = file.read().strip()
            else:
                local_version = ""

            # Check if the server version is different from the local version
            if server_version != local_version:
                self.updateAvailable.emit(server_version)
            else:
                self.noUpdateAvailable.emit()

        except Exception as e:
            self.errorOccurred.emit(str(e))

class DownloadThread(QThread):
    downloadFinished = pyqtSignal(str)
    errorOccurred = pyqtSignal(str)
    progressUpdated = pyqtSignal(int)  # Signal to emit progress

    def __init__(self, download_url, temp_download_path, parent=None):
        super().__init__(parent)
        self.download_url = download_url
        self.temp_download_path = temp_download_path

    def run(self):
        try:
            response = requests.get(self.download_url, stream=True)
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KiB

            downloaded_size = 0
            with open(self.temp_download_path, 'wb') as file:
                for data in response.iter_content(block_size):
                    if self.isInterruptionRequested():
                        raise Exception("Download canceled")

                    file.write(data)
                    downloaded_size += len(data)
                    
                    # Calculate the percentage and emit the progress signal
                    if total_size > 0:  # Prevent division by zero
                        progress_percentage = (downloaded_size / total_size) * 100
                        self.progressUpdated.emit(int(progress_percentage))

            self.downloadFinished.emit(self.temp_download_path)

        except Exception as e:
            self.errorOccurred.emit(str(e))





