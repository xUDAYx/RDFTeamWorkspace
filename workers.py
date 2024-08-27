from PyQt6.QtCore import QThread, pyqtSignal ,QMetaObject, Q_ARG,Qt
import qrcode
from PIL.ImageQt import ImageQt
from io import BytesIO
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtGui import QGuiApplication


class QRCodeWorker(QThread):
    finished = pyqtSignal(QPixmap, str)
    error = pyqtSignal(str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            # Generate the QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.url)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert the PIL image to a QPixmap
            buffer = BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)  # Ensure the buffer is read from the start

            qimage = QImage()
            if not qimage.loadFromData(buffer.getvalue()):
                raise ValueError("Failed to load image data into QImage")

            pixmap = QPixmap(qimage)
            self.finished.emit(pixmap, self.url)
        except Exception as e:
            self.error.emit(str(e))


