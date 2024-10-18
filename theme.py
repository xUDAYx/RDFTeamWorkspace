from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QApplication,QTabWidget,QToolBar
from PyQt6.QtCore import Qt

class DarkTheme:
    @staticmethod
    def apply():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(45, 45, 48))  # Dark background
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)  # Text
        palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))  # Editor background
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(50, 50, 50))  # Alternate background
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))  # Tooltip base
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)  # Tooltip text
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)  # General text
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 63, 65))  # Button background
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)  # Button text
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)  # Bright text (errors)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 204))  # Link color
        palette.setColor(QPalette.ColorRole.Highlight, QColor(50, 153, 255))  # Highlight color
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        QApplication.instance().setPalette(palette)



 
class LightTheme:
    @staticmethod
    def apply():
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(240, 240, 240))
        palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.Button, QColor(225, 225, 225))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 122, 204))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        QApplication.instance().setPalette(palette)
        


