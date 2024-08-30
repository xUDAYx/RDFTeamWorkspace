# import openai

# # Replace with your actual OpenAI API key
# openai.api_key = "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"

# response = openai.ChatCompletion.create(
#     model="gpt-3.5-turbo",
#     messages=[
#         {"role": "user", "content": "write a haiku about ai"}
#     ]
# )

# # Extract the generated text
# completion = response.choices[0].message["content"]
# print(completion)

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

