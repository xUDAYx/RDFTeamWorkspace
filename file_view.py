import sys
import os
import re
from PyQt6.QtWidgets import QApplication, QGridLayout, QWidget, QVBoxLayout, QScrollArea, QLabel, QMessageBox
from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt,QSize
from project_view import ProjectView

def read_project_info(folder_path):
    linked_files_dict = {}
    ui_folder_path = os.path.join(folder_path, "RDF_UI")

    print(f"Scanning RDF_UI folder at: {ui_folder_path}")

    if os.path.isdir(ui_folder_path):
        for ui_file in os.listdir(ui_folder_path):
            if ui_file.endswith("UI.php"):
                process_ui_file(folder_path, ui_file, linked_files_dict)
    else:
        print(f"RDF_UI folder not found at: {ui_folder_path}")

    return linked_files_dict

def process_ui_file(folder_path, ui_file, linked_files_dict):
    linked_files_dict[ui_file] = set()
    ui_file_path = os.path.join(folder_path, "RDF_UI", ui_file)
    print(f"Processing UI file: {ui_file_path}")

    if os.path.isfile(ui_file_path):
        try:
            with open(ui_file_path, "r", encoding="utf-8") as file:
                file_contents = file.read()
            js_files = [os.path.basename(match) for match in re.findall(r'"(.*?\.js)"', file_contents)]
            linked_files_dict[ui_file].update(js_files)

            for js_file in js_files:
                process_js_file(folder_path, js_file, ui_file, linked_files_dict)
        except UnicodeDecodeError as e:
            print(f"Error reading file {ui_file_path}: {e}")

def process_js_file(folder_path, js_file, ui_file, linked_files_dict):
    js_file_path = os.path.join(folder_path, "RDF_ACTION", js_file)
    print(f"Processing JS file: {js_file_path}")

    if os.path.isfile(js_file_path):
        try:
            with open(js_file_path, "r", encoding="utf-8") as file:
                js_file_contents = file.read()
            bw_files = [os.path.basename(match) for match in re.findall(r'[\w\/]+\/(.*?BW\.php)', js_file_contents)]
            linked_files_dict[ui_file].update(bw_files)

            for bw_file in bw_files:
                process_bw_file(folder_path, bw_file, ui_file, linked_files_dict)
        except UnicodeDecodeError as e:
            print(f"Error reading file {js_file_path}: {e}")

def process_bw_file(folder_path, bw_file, ui_file, linked_files_dict):
    bw_file_path = os.path.join(folder_path, "RDF_BW", bw_file)
    print(f"Processing BW file: {bw_file_path}")

    if os.path.isfile(bw_file_path):
        try:
            with open(bw_file_path, "r", encoding="utf-8") as file:
                bw_file_contents = file.read()
            bvo_files = [os.path.basename(match) for match in re.findall(r'[\w\/]+\/(.*?BVO\.php)', bw_file_contents)]
            linked_files_dict[ui_file].update(bvo_files)

            for bvo_file in bvo_files:
                process_bvo_file(folder_path, bvo_file, ui_file, linked_files_dict)
        except UnicodeDecodeError as e:
            print(f"Error reading file {bw_file_path}: {e}")

def process_bvo_file(folder_path, bvo_file, ui_file, linked_files_dict):
    bvo_file_path = os.path.join(folder_path, "RDF_BVO", bvo_file)
    print(f"Processing BVO file: {bvo_file_path}")

    if os.path.isfile(bvo_file_path):
        try:
            with open(bvo_file_path, "r", encoding="utf-8") as file:
                bvo_file_contents = file.read()
            data_files = re.findall(r'[\w\/]+\/(.*?Data\.json)', bvo_file_contents)
            linked_files_dict[ui_file].update(data_files)
        except UnicodeDecodeError as e:
            print(f"Error reading file {bvo_file_path}: {e}")


class ColorPanel(QWidget):
    def __init__(self, color, title, files, folder_path):
        super().__init__()
        self.node_folder_path = folder_path
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("transparent"))
        self.setPalette(palette)

        max_width = max([self.fontMetrics().boundingRect(file).width() for file in files] + [self.fontMetrics().boundingRect(title).width()])
        max_width = max(max_width, 200)

        self.setFixedSize(max_width + 20, 50 + len(files) * 25)

        layout = QVBoxLayout()
        layout = QVBoxLayout()
        if len(files) <= 2:
            layout.setSpacing(2)
        else:
            layout.setSpacing(5)

        title_label = QLabel(title, alignment=Qt.AlignmentFlag.AlignCenter)
        font = title_label.font()
        font.setBold(True)
        font.setPointSize(10)
        title_label.setFont(font)
        title_label.setFixedSize(max_width, 30)
        title_label.setStyleSheet(f"""
            color: white;
            border: 5px solid {color};
            align-text: centre;
            border-radius: 15px;
            background-color: {color};
        """)

        layout.addWidget(title_label)

        for file in files:
            file_label = QLabel(file)
            font = file_label.font()
            font.setBold(True)
            font.setPointSize(10)
            file_label.setFont(font)
            file_label.setStyleSheet(f"color: {color}; padding: 2px; ")
            file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(file_label)
            file_label.setFixedWidth(max_width)

        self.setLayout(layout)

class FileView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Project Structure Visualization")

        # Create an instance of ProjectView
        self.project_view = ProjectView()
        self.project_view.path_changed.connect(self.set_path)

        # Access the folder path from path_line_edit
        self.folder_path = self.project_view.get_path()
        print(f"Retrieved folder path from ProjectView: {self.folder_path}")

        self.linked_files_dict = None

        main_layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.scroll_layout = QGridLayout(self.scroll_widget)
        self.scroll_layout.setSpacing(10)

        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.scroll_area)
        self.scroll_area.setMinimumWidth(800)
        self.setLayout(main_layout)
        self.resize(800, 600)

    def set_path(self, folder_path):
        self.folder_path = folder_path
        if not self.folder_path:
            QMessageBox.warning(self, "Warning", "No project is opened to show file view")
            self.close()  # Close the FileView window if no path is set
            return

        self.linked_files_dict = read_project_info(self.folder_path)  # Read project info
        self.update_display()

    def clear_layout(self):
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def display_files(self, linked_files_dict, column_count):
        colors = ["#FF6B6B", "#FFA06B", "#9D6BFF", "#6BCEFF", "#6B8CFF", "#0052CC", "#6BFF7C", "#00CCAA"]
        color_index = 0

        for ui_file, linked_files in linked_files_dict.items():
            color = colors[color_index % len(colors)]
            panel = ColorPanel(color, ui_file, sorted(linked_files), self.folder_path)
            row = color_index // column_count
            column = color_index % column_count
            self.scroll_layout.addWidget(panel, row, column)
            color_index += 1
            for i in range(column_count):
                self.scroll_layout.setColumnMinimumWidth(i, 200)

    def update_display(self):
        if self.linked_files_dict:
            self.clear_layout()
            window_width = self.width()
            box_width = 200
            column_count = max(1, window_width // box_width - 1)
            self.display_files(self.linked_files_dict, column_count)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    def calculate_min_width(self, linked_files_dict):
        num_columns = len(linked_files_dict)
        column_width = 200
        spacing = 10
        scroll_area_padding = 20
        min_width = num_columns * (column_width + spacing) + scroll_area_padding
        return min_width



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileView()
    window.show()
    sys.exit(app.exec())
