import re
import json
import os, sys
import logging,chardet
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
from PyQt6.QtGui import QSyntaxHighlighter
from PyQt6.Qsci import QsciDocument
from PyQt6.QtWidgets import QPlainTextEdit,QLabel, QMainWindow,QLineEdit,QMenu, QVBoxLayout, QWidget, QSplitter, QTreeView, QToolBar, QFileDialog, QToolButton, QTabWidget, QApplication, QMessageBox, QPushButton, QTextEdit, QScrollBar, QHBoxLayout, QSizePolicy
from PyQt6.QtGui import  QTextCharFormat,QAction, QPixmap, QFileSystemModel, QIcon, QFont, QPainter, QColor, QTextFormat, QTextCursor, QKeySequence, QShortcut
from PyQt6.QtCore import Qt, QModelIndex, QTimer, QDir, pyqtSlot, QSize, QRect, QProcess, QPoint
from PyQt6.Qsci import QsciScintilla, QsciLexerPython, QsciLexerHTML, QsciLexerJavaScript, QsciLexerCSS

from terminal_widget import TerminalWidget
from mobile_view import MobileView
from project_view import ProjectView
from new_project import NewProjectWizard
from theme import DarkTheme
from PyQt6.Qsci import QsciAbstractAPIs, QsciScintilla, QsciDocument,QsciLexerJSON
from autocompleter import AutoCompleter
from Rule_Engine import RuleEngine


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
        
class CodeEditor(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Code Editor")
            self.showMaximized()
            self.setWindowFlags(Qt.WindowType.Window)
            self.setGeometry(100, 100, 800, 600)

            self.project_view = ProjectView(self)
            self.project_view.file_double_clicked.connect(self.open_file_from_project_view)

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
            self.open_project_action.triggered.connect(self.new_project_workspace)
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

            view_menu.addAction(self.dark_mode_action)
            view_menu.addAction(self.project_view_action)

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

            validation_menu.addAction(self.validate_project_action)
            validation_menu.addAction(self.validate_action)

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

            self.mobile_view = MobileView()
            self.terminal = TerminalWidget()
            self.wizard = NewProjectWizard()

            self.splitter = QSplitter(Qt.Orientation.Horizontal)
            self.splitter.addWidget(self.project_view)
            self.splitter.addWidget(self.tab_widget)
            self.splitter.setSizes([500, 900])  # Set initial sizes for the project view and tab widget

            self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
            self.main_splitter.addWidget(self.splitter)
            self.main_splitter.addWidget(self.mobile_view)
            self.main_splitter.setSizes([1200, 300])  # Set initial sizes for the main splitter

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
                self.project_view.select_workspace()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating new project workspace: {e}")
            logging.error(f"Error creating new project workspace: {e}")

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

        except ValueError as e:
            QWidget.QMessageBox.critical(None, "Error", str(e))

    def validate_project(self):
        try:
            project_path, rules_mapping, rules_dict = self.project_view.initialize_validator()
            files_with_errors = self.project_view.validate_files(project_path, rules_mapping, rules_dict)
            self.project_view.show_results(files_with_errors)

        except ValueError as e:
            QWidget.QMessageBox.critical(None, "Error", str(e))

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

            search_bar = QLineEdit()
            search_bar.setVisible(False)
            search_bar.setPlaceholderText("Search...")
            search_bar.textChanged.connect(lambda text: self.search_text(text))

            publish_button = QPushButton("Publish")
            publish_button.setStyleSheet("background-color:red;color:white;font-weight:bold")
            publish_button.clicked.connect(self.publish_code)

            search_tab_layout = QHBoxLayout()
            search_tab_layout.addStretch()
            search_tab_layout.addWidget(search_bar)
            search_tab_layout.addWidget(publish_button)  # Add the publish button to the search tab layout
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

                    # Set up syntax highlighter and auto-completer
                    extension = os.path.splitext(file_path)[1][1:]
                    language = self.get_language_from_extension(extension)
                    lexer = self.get_lexer_for_language(language)
                    editor.setLexer(lexer)

                    # Set up autocompleter
                    autocompleter = AutoCompleter(lexer)
                    autocompleter.add_custom_apis([
                        "<table class=\"section\">", "<tr>", "<td>", "</td>", "</tr>", "</table>",
                        "<td style=\"width: 90%;\">", "getYYY()", "yyyBVO.php",
                        "RDF_ACTION", "RDF_BW", "RDF_BVO", "RDF_DATA",
                        "inline", "width", "height", "background-color", "color"
                    ])
                    autocompleter.prepare()

                # Set up the editor's auto-completion settings
                editor.setAutoCompletionThreshold(1)  # Show auto-completions after 1 character
                editor.setAutoCompletionCaseSensitivity(False)  # Make auto-completion case insensitive
                editor.setAutoCompletionReplaceWord(False)

            except Exception as e:
                print(f"Failed to open file: {e}")

        except Exception as e:
            print(f"Failed to open new tab: {e}")


    def publish_code(self):
        try:
            # Create a new window
            self.publish_window = QWidget()
            self.publish_window.setWindowTitle("Publish Code")
            
            layout = QVBoxLayout()
            
            # Construct the dynamic path to the image
            current_dir = os.path.dirname(os.path.abspath(__file__))
            image_path = os.path.join(current_dir, 'images', 'publish_image.jpg')  # Replace 'publish_image.jpg' with the actual image name
            
            # Add an image
            label = QLabel()
            pixmap = QPixmap(image_path)
            label.setPixmap(pixmap)
            layout.addWidget(label)
            
            self.publish_window.setLayout(layout)
            
            # Set initial small size
            self.publish_window.resize(100, 100)  # Initial small size
            
            # Adjust the size to fit the image after loading it
            # self.publish_window.adjustSize()
            self.publish_window.show()
        except Exception as e:
            print(f"{e}")


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


    def eventFilter(self, source, event):
        if event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_F and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
                # Toggle search bar visibility for the current tab
                current_widget = self.tab_widget.currentWidget()
                search_bar = current_widget.findChild(QLineEdit)
                if search_bar:
                    search_bar.setVisible(not search_bar.isVisible())
                    if search_bar.isVisible():
                        search_bar.setFocus()
                return True
        return super().eventFilter(source, event)
    
    def highlight_text(self, text_edit, text):
        try:
            if not text:
                print("No text to highlight")
                return

            # Clear previous indicators
            text_edit.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, text_edit.length())

            # Set up the indicator for highlighting
            INDICATOR_NUM = 0
            text_edit.SendScintilla(QsciScintilla.SCI_INDICSETSTYLE, INDICATOR_NUM, QsciScintilla.INDIC_BOX)

            # Convert the color to a signed 32-bit integer
            color = QColor("yellow").rgb()
            if color > 0x7FFFFFFF:
                color -= 0x100000000

            text_edit.SendScintilla(QsciScintilla.SCI_INDICSETFORE, INDICATOR_NUM, color)

            # Highlight occurrences of the text
            pos = 0
            found_any = False
            while True:
                found = text_edit.findFirst(text, False, False, False, False, True, pos)
                if not found:
                    break
                found_any = True
                start_pos = found.start()
                end_pos = found.end()
                print(f"Highlighting text from {start_pos} to {end_pos}")
                text_edit.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start_pos, end_pos - start_pos)
                pos = end_pos

            if not found_any:
                print(f"Text '{text}' not found.")

        except Exception as e:
            error_message = f"Error highlighting text: {e}"
            print(error_message)
            


    def search_text(self, text):
        print(f"Searching text: {text}")
        try:
            current_widget = self.tab_widget.currentWidget()
            print(f"Current widget type: {type(current_widget)}")
            if isinstance(current_widget, QsciScintilla):
                print(f"Found QsciScintilla: {current_widget}")
                current_widget.print_editor_content()  # Print editor content for debugging
                self.highlight_text(current_widget, text)
            else:
                # Check if there's a layout or nested widgets to access QsciScintilla
                editor = current_widget.findChild(QsciScintilla)
                if editor:
                    print(f"Found QsciScintilla via findChild: {editor}")  
                    self.highlight_text(editor, text)
                else:
                    print("No QsciScintilla found in current editor widget.")
        except Exception as e:
            error_message = f"Error searching text: {e}"
            print(error_message)
            self.show_error_message(error_message)
                

   
    def toggle_search_bar(self, search_bar):
        try:
            search_bar.setVisible(not search_bar.isVisible())
            if search_bar.isVisible():
                search_bar.setFocus()
        except Exception as e:
            print(f"Error toggling search bar visibility: {e}")
            self.show_error_message(f"Error toggling search bar visibility: {e}")

    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()

