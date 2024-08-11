import json
import os
from PyQt6.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import (
    QApplication, QWizard, QTreeView, QVBoxLayout, QWizardPage, QLineEdit, QPushButton, QAbstractItemView
)
import webbrowser
import sys

class BookmarkWizard(QWizard):
    urlClicked = pyqtSignal(str)  # Custom signal to emit URL when clicked

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bookmark Manager")
        self.setGeometry(100, 100, 600, 400)

        # Create pages
        self.bookmark_page = QWizardPage()
        self.bookmark_page.setTitle("Bookmarks")

        # Initialize bookmark storage
        self.bookmarks = []

        # Create UI components for the first page
        self.url_input = QLineEdit(self.bookmark_page)
        self.url_input.setPlaceholderText("Enter website URL")
        self.tag_input = QLineEdit(self.bookmark_page)
        self.tag_input.setPlaceholderText("Enter tags (comma-separated)")
        self.add_button = QPushButton("Add Bookmark", self.bookmark_page)
        self.search_input = QLineEdit(self.bookmark_page)
        self.search_input.setPlaceholderText("Search bookmarks by tag")
        self.bookmark_tree = QTreeView(self.bookmark_page)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.url_input)
        layout.addWidget(self.tag_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.search_input)
        layout.addWidget(self.bookmark_tree)
        self.bookmark_page.setLayout(layout)

        # Add the page to the wizard
        self.addPage(self.bookmark_page)

        # Set up the tree view model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Bookmarks"])
        self.bookmark_tree.setModel(self.model)
        self.bookmark_tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing
        self.bookmark_tree.clicked.connect(self.on_bookmark_clicked)

        self.setButtonLayout([
            QWizard.WizardButton.Stretch,
            QWizard.WizardButton.BackButton,
            QWizard.WizardButton.NextButton,
            QWizard.WizardButton.CancelButton,
        ])
       
        # Connect signals
        self.add_button.clicked.connect(self.add_bookmark)
        self.search_input.textChanged.connect(self.filter_bookmarks)

        self.load_bookmarks()

    def add_bookmark(self):
        url = self.url_input.text()
        tags = [tag.strip() for tag in self.tag_input.text().split(",") if tag.strip()]
        if url:
            serial_number = len(self.bookmarks) + 1
            for tag in tags:
                self.bookmarks.append((serial_number, tag, url))
            self.update_bookmark_tree()
            self.url_input.clear()
            self.tag_input.clear()
            self.save_bookmarks()

    def update_bookmark_tree(self):
        self.model.clear()
        self.model.setHorizontalHeaderLabels(["Bookmarks"])
        for serial_number, tag, url in sorted(self.bookmarks):
            display_text = f"{serial_number}. {tag} - {url}"
            item = QStandardItem(display_text)
            item.setData(url, Qt.ItemDataRole.UserRole)
            self.model.appendRow(item)

    def filter_bookmarks(self):
        search_text = self.search_input.text().lower()
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            item_text = item.text().lower()
            should_hide = search_text not in item_text
            self.bookmark_tree.setRowHidden(row, QModelIndex(), should_hide)

    def on_bookmark_clicked(self, index: QModelIndex):
        item = self.model.itemFromIndex(index)
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            print(f"Emitting signal with URL: {url}")
            self.urlClicked.emit(url)
            webbrowser.open(url)

    def save_bookmarks(self):
        try:
            with open("bookmarks.json", "w") as file:
                json.dump(self.bookmarks, file, indent=4)
        except Exception as e:
            print(f"Error saving bookmarks: {e}")

    def load_bookmarks(self):
        if os.path.exists("bookmarks.json"):
            try:
                with open("bookmarks.json", "r") as file:
                    data = json.load(file)
                    if isinstance(data, list) and all(isinstance(entry, list) and len(entry) == 3 for entry in data):
                        self.bookmarks = [(int(entry[0]), entry[1], entry[2]) for entry in data]
                    else:
                        print("Error: Bookmarks file is not in the expected format. Resetting bookmarks.")
                        self.bookmarks = []
                    self.update_bookmark_tree()
            except Exception as e:
                print(f"Error loading bookmarks: {e}")
                self.bookmarks = []
                self.update_bookmark_tree()
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    bookmark_wizard = BookmarkWizard()
    bookmark_wizard.show()
    sys.exit(app.exec())
