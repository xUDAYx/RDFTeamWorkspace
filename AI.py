
import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Create a QWebEngineView widget
        self.web_view = QWebEngineView(self)

        # Load the URL
        url = r"https://takeitideas.in/RDFSTUDIO/UserTimeTracking/timemanagement.php?email=pratapshukla007%40gmailcom&startTime=1234&endTime=2345"
        self.web_view.setUrl(QUrl(url))

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.web_view)
        self.setLayout(layout)

        # Window settings
        self.setWindowTitle('Display URL in QWebEngineView')
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())

