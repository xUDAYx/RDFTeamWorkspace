import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QMessageBox
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter
from PyQt6.QtCore import QRegularExpression

class MultiLanguageHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.highlighting_rules = []
        
        # Default text format (plain black)
        self.default_format = QTextCharFormat()
        self.default_format.setForeground(QColor("#000000"))
        
        # Initialize the highlighter with HTML rules by default
        try:
            self.set_language("html")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"Error initializing syntax highlighter: {e}")
            print(f"Error initializing syntax highlighter: {e}")
    
    def set_language(self, language):
        self.highlighting_rules.clear()
        
        if language == "html":
            self.set_html_rules()
        elif language == "javascript":
            self.set_javascript_rules()
        elif language == "php":
            self.set_php_rules()
        elif language == "css":
            self.set_css_rules()
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def set_html_rules(self):
        self.highlighting_rules.extend([
            # Tags
            (r'<[a-zA-Z0-9!\/?]+', self.create_format("#0000FF", bold=True)),   # Blue
            
            # Attributes
            (r'\b[a-zA-Z\-]+(?=\=)', self.create_format("#FF00FF", bold=True)),   # Purple
            
            # Strings (double quoted)
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.create_format("#008000", bold=True)),  # Green
        ])
    
    def set_javascript_rules(self):
        self.highlighting_rules.extend([
            # Keywords
            (r'\bfunction\b', self.create_format("#0000FF", bold=True)),   # Blue
            (r'\bvar\b', self.create_format("#0000FF", bold=True)),
            (r'\bif\b', self.create_format("#0000FF", bold=True)),
            (r'\belse\b', self.create_format("#0000FF", bold=True)),
            (r'\bfor\b', self.create_format("#0000FF", bold=True)),
            (r'\bwhile\b', self.create_format("#0000FF", bold=True)),
            (r'\bdo\b', self.create_format("#0000FF", bold=True)),
            (r'\breturn\b', self.create_format("#0000FF", bold=True)),
            
            # Built-in objects and functions
            (r'\bconsole\b', self.create_format("#FFA500", bold=True)),  # Orange
            
            # Strings (single and double quoted)
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.create_format("#008000", bold=True)),  # Green
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.create_format("#008000", bold=True)),
            
            # Comments
            (r'//.*$', self.create_format("#808080", bold=True)),  # Gray
            (r'/\*(.|\n)*?\*/', self.create_format("#808080", bold=True)),
        ])
    
    def set_php_rules(self):
        self.highlighting_rules.extend([
            # Keywords
            (r'\bfunction\b', self.create_format("#0000FF", bold=True)),   # Blue
            (r'\bif\b', self.create_format("#0000FF", bold=True)),
            (r'\belse\b', self.create_format("#0000FF", bold=True)),
            (r'\bfor\b', self.create_format("#0000FF", bold=True)),
            (r'\bwhile\b', self.create_format("#0000FF", bold=True)),
            (r'\bdo\b', self.create_format("#0000FF", bold=True)),
            (r'\breturn\b', self.create_format("#0000FF", bold=True)),
            
            # Variables and constants
            (r'\$\w+', self.create_format("#FFA500", bold=True)),  # Orange
            
            # Strings (single and double quoted)
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.create_format("#008000", bold=True)),  # Green
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.create_format("#008000", bold=True)),
            
            # Comments
            (r'//.*$', self.create_format("#808080", bold=True)),  # Gray
            (r'/\*(.|\n)*?\*/', self.create_format("#808080", bold=True)),
        ])
    
    def set_css_rules(self):
        self.highlighting_rules.extend([
            # Selectors (class, id, tag)
            (r'[a-zA-Z\-\_][a-zA-Z0-9\-\_]*', self.create_format("#0000FF", bold=True)),   # Blue
            
            # Properties and values
            (r'\b\w+\b(?=\s*:)', self.create_format("#FF00FF", bold=True)),   # Purple
            
            # Strings (single and double quoted)
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.create_format("#008000", bold=True)),  # Green
            (r"'[^'\\]*(\\.[^'\\]*)*'", self.create_format("#008000", bold=True)),
            
            # Comments
            (r'/\*(.|\n)*?\*/', self.create_format("#808080", bold=True)),  # Gray
        ])
    
    def create_format(self, color, bold=False):
        text_format = QTextCharFormat()
        text_format.setForeground(QColor(color))
        if bold:
            text_format.setFontWeight(QFont.Weight.Bold)
        return text_format
    
    def highlightBlock(self, text):
        try:
            for pattern, format in self.highlighting_rules:
                regex = QRegularExpression(pattern)
                match_iterator = regex.globalMatch(text)
                while match_iterator.hasNext():
                    match = match_iterator.next()
                    self.setFormat(match.capturedStart(), match.capturedLength(), format)
        except Exception as e:
            print(f"Error in highlightBlock: {e}")
            QMessageBox.critical(None, "Error", f"Error highlighting syntax: {e}")

