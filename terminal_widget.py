from PyQt6.QtWidgets import QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class TerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.text_edit = QTextEdit(self)
        self.text_edit.setFont(QFont("Monospace", 10))
        self.text_edit.setStyleSheet("background-color: black; color: white;")
        self.text_edit.setReadOnly(True)

        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setFixedSize(60, 30)
        self.clear_button.clicked.connect(self.clear_terminal)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.clear_button)

        layout = QVBoxLayout(self)
        layout.addLayout(button_layout)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return:
            self.write("\n")
        else:
            super().keyPressEvent(event)

    def write(self, text, color="white"):
        colored_text = f'<span style="color:{color};">{text}</span>'
        self.text_edit.append(colored_text)
        self.text_edit.ensureCursorVisible()

    def clear_terminal(self):
        self.text_edit.clear()
