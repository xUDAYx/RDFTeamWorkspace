from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

class DarkTheme:
    @staticmethod
    def apply():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))  # Dark background
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)  # White text
        palette.setColor(QPalette.ColorRole.Base, QColor(40, 44, 52))  # Editor background
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))  # Alternate background
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.black)  # Tooltip base
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)  # Tooltip text
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)  # Text color
        palette.setColor(QPalette.ColorRole.Button, QColor(104, 109, 118))  # Button background
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)  # Button text
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)  # Bright text (e.g., errors)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 204))  # Link color
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))  # Highlight color
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)  # Highlighted text
        QApplication.instance().setPalette(palette)



