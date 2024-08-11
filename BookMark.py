import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLineEdit, QPushButton, QTreeView,
    QVBoxLayout, QWidget, QAbstractItemView, QLabel
)
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QModelIndex
import webbrowser
import sys

class BookmarkApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bookmark Manager")
        self.setGeometry(100, 100, 600, 400)

        self.bookmarks = []  # Initialize as a list of tuples: (serial_number, tag, url)

        # Create widgets
        self.heading_label = QLabel("Website Bookmarks", self)
        self.heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.heading_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")

        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter website URL")
        self.tag_input = QLineEdit(self)
        self.tag_input.setPlaceholderText("Enter tags (comma-separated)")
        self.add_button = QPushButton("Add Bookmark", self)
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search bookmarks by tag")
        self.bookmark_tree = QTreeView(self)

        # Set layout
        layout = QVBoxLayout()
        layout.addWidget(self.heading_label)
        layout.addWidget(self.url_input)
        layout.addWidget(self.tag_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.search_input)
        layout.addWidget(self.bookmark_tree)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Setup tree view
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Bookmarks"])
        self.bookmark_tree.setModel(self.model)
        self.bookmark_tree.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Disable editing
        self.bookmark_tree.clicked.connect(self.open_bookmark)

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
            item.setData(url, Qt.ItemDataRole.UserRole)  # Store URL in item data
            self.model.appendRow(item)

    def filter_bookmarks(self):
        search_text = self.search_input.text().lower()
        for row in range(self.model.rowCount()):
            item = self.model.item(row)
            item_text = item.text().lower()
            should_hide = search_text not in item_text
            self.bookmark_tree.setRowHidden(row, QModelIndex(), should_hide)

    def open_bookmark(self, index: QModelIndex):
        item = self.model.itemFromIndex(index)
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
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
                    # Ensure the loaded data is a list of tuples
                    if isinstance(data, list) and all(isinstance(entry, list) and len(entry) == 3 for entry in data):
                        self.bookmarks = [(int(entry[0]), entry[1], entry[2]) for entry in data]
                    else:
                        print("Error: Bookmarks file is not in the expected format. Resetting bookmarks.")
                        self.bookmarks = []
                    self.update_bookmark_tree()
            except Exception as e:
                print(f"Error loading bookmarks: {e}")
                self.bookmarks = []  # Reset to empty list in case of error
                self.update_bookmark_tree()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookmarkApp()
    window.show()
    sys.exit(app.exec())
