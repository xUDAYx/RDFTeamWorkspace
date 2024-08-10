import re
import json
import os, sys
import logging,chardet
import traceback
from ftplib import FTP,error_perm
import time

from pc_view import PCView
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from PyQt6.QtGui import QSyntaxHighlighter
from PyQt6.Qsci import QsciDocument
from PyQt6.QtWidgets import  QDialog,QPlainTextEdit, QProgressBar,QInputDialog,QLabel, QMainWindow,QLineEdit,QMenu, QVBoxLayout, QWidget, QSplitter, QDialogButtonBox, QTreeView, QToolBar, QFileDialog, QToolButton, QTabWidget, QApplication, QMessageBox, QPushButton, QTextEdit, QScrollBar, QHBoxLayout, QSizePolicy
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

    def setup_editor(self):
        """Initialize editor settings and font."""
        font = QFont("Consolas", self.font_size)
        self.setFont(font)

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
    
    def find_text(self, text):
        self.search_text = text
        self.current_search_pos = 0
        self.find_next()

    def find_next(self):
        if self.search_text:
            self.current_search_pos = self.findFirst(
                self.search_text, False, False, False, True, self.current_search_pos
            )
            if self.current_search_pos == -1:
                self.current_search_pos = 0

    def find_previous(self):
        if self.search_text:
            self.current_search_pos = self.findFirst(
                self.search_text, False, False, False, True, self.current_search_pos - 1, -1
            )
            if self.current_search_pos == -1:
                self.current_search_pos = self.length()

    def replace(self, text):
        try:
            if self.search_text:
                self.replaceSelectedText(text)
                self.find_next()
        except Exception as e:
            QMessageBox.Warning(self,"replace error",f"error in replace{e}")

    def replace_all(self, find_text, replace_text):
        try:
            self.beginUndoAction()
            pos = 0
            while True:
                pos = self.findFirst(find_text, False, False, False, True, pos)
                if pos == -1:
                    break
                self.replaceSelectedText(replace_text)
                pos += len(replace_text)
            self.endUndoAction()
        except Exception as e:
            QMessageBox.Warning(self,"replace all error",f"error in replace all{e}")
        
class CodeEditor(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("RDF STUDIO")
            self.showMaximized()
            self.setWindowFlags(Qt.WindowType.Window)
            self.setGeometry(100, 100, 800, 600)
            self.pc_view = PCView()
            self.mobile_view = MobileView()
            self.terminal = TerminalWidget()
            self.wizard = NewProjectWizard()
            self.open_project_wizard = OpenProjectWizard()
            self.project_view = ProjectView(self)
            self.open_project_wizard.project_opened.connect(self.project_view.update_project_view)
            self.wizard.project_created.connect(self.project_view.update_project_view)
            self.project_view.file_double_clicked.connect(self.open_file_from_project_view)

            self.pc_view_active = False  # Add this line to track PC view state
            
            self.main_layout = QVBoxLayout()
            self.central_widget = QWidget()
            self.central_widget.setLayout(self.main_layout)
            self.setCentralWidget(self.central_widget)

            self.codeEditor = CustomCodeEditor()
            self.hScrollBar = QScrollBar(Qt.Orientation.Horizontal)

            self.hScrollBar.valueChanged.connect(self.syncScrollBar)
            self.codeEditor.horizontalScrollBar().valueChanged.connect(self.syncEditorScrollBar)

            # Create the toolbar
            self.toolbar = QToolBar("Main Toolbar")

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

            project_menu.addAction(self.open_project_action)
            self.addAction(self.open_project_action)
            project_menu.addAction(self.new_project_action)
            project_menu.addAction(self.create_file_action)
            project_menu.addAction(self.save_action)

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

            view_menu.addAction(self.dark_mode_action)
            view_menu.addAction(self.project_view_action)
            view_menu.addAction(self.pc_view_action)

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

            self.rules_directory = os.path.join(os.getcwd(), 'rules')
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
            
            
    
    def toggle_ref_view(self, checked):
        if checked:
            self.ref_view.toggle_stay_on_top(True)
        else:
            self.ref_view.toggle_stay_on_top(False)
            self.ref_view.hide()   
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
                if editor and hasattr(current_widget, 'file_path'):
                    with open(current_widget.file_path, 'w') as file:
                        file.write(editor.text())
                    terminal = current_widget.findChild(TerminalWidget)
                    if terminal:
                        terminal.write(f"Saved file: {current_widget.file_path}\n")
                    self.mobile_view.load_file_preview(current_widget.file_path)
                    self.pc_view.load_file_preview(current_widget.file_path)
                else:
                    terminal.write("No file opened to save.\n")
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


    def open_file_from_project_view(self, file_path):
        try:
            self.open_file_in_new_tab(file_path)
        except Exception as e:
            print(f"Error opening file from project view: {e}")
            logging.error(f"Error opening file from project view: {e}")
    
    def open_file_in_new_tab(self, file_path):
        try:
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i).file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return

            tab = QWidget()
            tab.file_path = file_path
            layout = QVBoxLayout()
            editor = CustomCodeEditor()
            editor.setFont(QFont("Consolas", 12))
            terminal = TerminalWidget()

            find_button = QPushButton("find")
            find_button.clicked.connect(lambda:self.show_find_replace_dialog(editor))
            find_button.setStyleSheet("background-color:#f0f0f0;border-radius:5px;padding:4px 10px;border:1px solid #ccc")
            
            publish_button = QPushButton("Upload")
            publish_button.setStyleSheet("background-color:red;color:white;font-weight:bold;border-radius:5px;padding:5px 10px")
            publish_button.clicked.connect(self.on_publish)

            format_button = QPushButton("Format Code")
            format_button.clicked.connect(lambda: self.format_current_code(editor, file_path))
            format_button.setStyleSheet("background-color:#f0f0f0;border-radius:5px;padding:4px 10px;border:1px solid #ccc")
            
            # Create an instance of ReferenceView
            self.ref_view = ReferenceView()

            # Add a button to the toolbar to show/hide the reference view
            self.ref_view_action = QAction(QIcon("ref_view.png"), "Reference View", self)
            self.ref_view_action.setCheckable(True)
            self.ref_view_action.toggled.connect(self.toggle_ref_view)
            self.toolbar.addAction(self.ref_view_action)

            search_tab_layout = QHBoxLayout()
            search_tab_layout.addStretch()
            search_tab_layout.addWidget(find_button)
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

            toggle_button.clicked.connect(lambda: self.toggle_terminal(splitter, toggle_button))

            try:
                with open(file_path, 'rb') as file:
                    raw_data = file.read()
                    result = chardet.detect(raw_data)
                    encoding = result['encoding']

                with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                    file_contents = file.read()
                    editor.setText(file_contents)
                    terminal.write(f"Loaded file: {file_path}\n")
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

        except Exception as e:
            print(f"Failed to open new tab: {e}")

    def show_find_replace_dialog(self, editor):
        try:
            find_replace_widget = QWidget(self)
            find_replace_layout = QHBoxLayout(find_replace_widget)

            find_edit = QLineEdit(find_replace_widget)
            find_edit.setPlaceholderText("Find")
            replace_edit = QLineEdit(find_replace_widget)
            replace_edit.setPlaceholderText("Replace")

            find_button = QPushButton("Find", find_replace_widget)
            replace_button = QPushButton("Replace", find_replace_widget)
            replace_all_button = QPushButton("Replace All", find_replace_widget)

            find_replace_layout.addWidget(find_edit)
            find_replace_layout.addWidget(replace_edit)
            find_replace_layout.addWidget(find_button)
            find_replace_layout.addWidget(replace_button)
            find_replace_layout.addWidget(replace_all_button)

            find_replace_widget.setLayout(find_replace_layout)
            find_replace_widget.setWindowFlags(Qt.WindowType.Tool)
            find_replace_widget.show()

            # Connect buttons to editor's methods
            find_button.clicked.connect(lambda: editor.find_text(find_edit.text()))
            replace_button.clicked.connect(lambda: editor.replace(find_edit.text(), replace_edit.text()))
            replace_all_button.clicked.connect(lambda: editor.replace_all(find_edit.text(), replace_edit.text()))

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to show find and replace dialog: {e}")
            logging.error(f"Failed to show find and replace dialog: {e}")

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
        server = 'ftp.takeitideas.in'

        while True:  # Loop until valid inputs are provided
            login_dialog = LoginDialog(self)
            if login_dialog.exec() == QDialog.DialogCode.Accepted:
                username, password = login_dialog.get_credentials()

                if not username:
                    QMessageBox.warning(self, 'Error', 'Username is required.')
                    continue  # Stay in the loop, keep the dialog open

                if not password:
                    QMessageBox.warning(self, 'Error', 'Password is required.')
                    continue  # Stay in the loop, keep the dialog open

                # Validate FTP credentials
                if not self.validate_ftp_credentials(server, username, password):
                    QMessageBox.warning(self, 'Error', 'Invalid username or password.')
                    continue  # Stay in the loop, keep the dialog open

                # Break the loop if both username and password are valid
                break

            else:
                # User cancelled the dialog
                QMessageBox.information(self, 'Cancelled', 'Publishing cancelled.')
                return

        current_index = self.tab_widget.currentIndex()
        current_tab = self.tab_widget.widget(current_index)
        project_dir = os.path.dirname(os.path.dirname(current_tab.file_path))
        project_name = os.path.basename(project_dir)
        remote_dir = f'/public_html/RDFProjects_ROOT/{project_name}'

        # Create and show the progress dialog
        dialog = PublishDialog(self)
        dialog.show()

        # Start the upload in a separate thread
        self.upload_thread = UploadThread(server, username, password, project_dir, remote_dir)
        self.upload_thread.progress.connect(dialog.update_progress)
        self.upload_thread.finished.connect(dialog.upload_finished)
        self.upload_thread.start()
    

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
                qapp = QApplication.instance()
                qapp.quit()
                QProcess.startDetached(sys.executable, sys.argv)
            else:
                print("Restart cancelled by user.")
        except Exception as e:
            print(f"Error restarting application: {e}")
            logging.error(f"Error restarting application: {e}")


    def eventFilter(self, obj, event):
        try:
            if event.type() == event.Type.KeyPress:
                if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                    self.show_find_replace_dialog()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to handle event: {e}")
            logging.error(f"Failed to handle event: {e}")
        return super().eventFilter(obj, event)
    
            

    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()

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

    def upload_directory_to_ftp(self,server, username, password, local_dir, remote_dir):
        
        
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
                        print(f"file uploaded {remote_file_path}")
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

class PublishDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Publishing Project')
        self.setFixedSize(300, 100)
        
        self.layout = QVBoxLayout()
        self.label = QLabel("Uploading...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.file_label = QLabel("Current file: None")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.layout.addWidget(self.file_label)
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
class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('FTP Login')

        self.layout = QVBoxLayout(self)

        self.username_label = QLabel("Username:")
        self.layout.addWidget(self.username_label)
        self.username_input = QLineEdit(self)
        self.layout.addWidget(self.username_input)

        self.password_label = QLabel("Password:")
        self.layout.addWidget(self.password_label)
        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, self)
        self.layout.addWidget(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()   