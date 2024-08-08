import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QScrollArea
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

class ReferenceView(QWidget):
  def __init__(self, parent=None):
      super().__init__(parent)
      self.setWindowTitle("Reference View")
      self.setFixedSize(400, 600)
      # Create a layout
      layout = QVBoxLayout()
      layout.setContentsMargins(20, 20, 20, 20)  # Add some padding

      # Create a scroll area
      scroll_area = QScrollArea()
      scroll_area.setWidgetResizable(True)
      scroll_area.setStyleSheet("""
          QScrollArea {
              border: 1px solid #ccc;
              border-radius: 5px;
          }
      """)

      # Create a label to display the image
      self.image_label = QLabel()
      self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
      scroll_area.setWidget(self.image_label)

      layout.addWidget(scroll_area)

      
      browse_button = QPushButton("Browse Image")
      browse_button.setStyleSheet("""
          QPushButton {
              background-color: #1E90FF;
              color: white;
              padding: 5px 10px;
              border-radius: 3px;
              font-size: 12px;
          }
          QPushButton:hover {
              background-color: #4169E1;
          }
      """)
      browse_button.clicked.connect(self.browse_image)
      layout.addWidget(browse_button, alignment=Qt.AlignmentFlag.AlignCenter)

      self.setLayout(layout)
      self.setStyleSheet("background-color: #f0f0f0;")  # Set a light background color

  def browse_image(self):
      file_dialog = QFileDialog()
      file_dialog.setNameFilter("Image Files (*.png *.jpg *.bmp)")
      if file_dialog.exec():
          selected_files = file_dialog.selectedFiles()
          if selected_files:
              image_path = selected_files[0]
              self.load_image(image_path)

  def load_image(self, image_path):
      self.original_pixmap = QPixmap(image_path)
      if not self.original_pixmap.isNull():
          self.display_image()
      else:
          self.image_label.setText("Failed to load image")

  def display_image(self):
      # Get the available space in the widget
      available_width = self.width() - 40  # Subtract margins
      available_height = self.height() - 100  # Subtract margins and button height

      # Scale the image to fit the available space while maintaining aspect ratio
      scaled_pixmap = self.original_pixmap.scaled(available_width, available_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
      self.image_label.setPixmap(scaled_pixmap)

  def resizeEvent(self, event):
      super().resizeEvent(event)
      if hasattr(self, 'original_pixmap'):
          self.display_image()

  def toggle_stay_on_top(self, stay_on_top):
      window_flags = self.windowFlags()
      if stay_on_top:
          self.setWindowFlags(window_flags | Qt.WindowType.WindowStaysOnTopHint)
      else:
          self.setWindowFlags(window_flags & ~Qt.WindowType.WindowStaysOnTopHint)
      self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ref_view = ReferenceView()
   
    ref_view.show()
    sys.exit(app.exec())
