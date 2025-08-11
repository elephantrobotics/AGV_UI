import cv2
import time
from PyQt5.QtCore import QThread, pyqtSignal, QSize, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget
from .camera_ui import Ui_Camera as CameraUI
from core import GlobalVar


class RealtimeCameraThread(QThread):
    dispatched = pyqtSignal(QPixmap)
    finished = pyqtSignal(bool)

    def __init__(self, size: QSize, timeout: int = 10):
        super().__init__()
        self.__size = size
        self.__running = True
        self.__timeout = timeout
        self.__capture = cv2.VideoCapture(GlobalVar.camera2D_pipline)
        self.__capture.set(cv2.CAP_PROP_FPS, 30)

    def set_size(self, size: QSize):
        self.__size = size

    def stop_running(self):
        self.__running = False

    @property
    def is_opened(self):
        return self.__capture.isOpened()

    def run(self):
        start_time = time.time()
        is_opened = self.is_opened
        while time.time() - start_time < 10 and is_opened:
            ret, frame = self.__capture.read()
            if self.__running is False:
                break

            if ret is False:
                continue

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image).scaled(self.__size, Qt.KeepAspectRatio)
            self.dispatched.emit(pixmap)

        self.__capture.release()
        self.finished.emit(not self.__running)


class AGVCameraWidget(QWidget, CameraUI):
    finished = pyqtSignal(str, bool)

    def __init__(self, test_name: str):
        super().__init__()
        self.setup_ui()
        self.test_name = test_name
        self.camera_thread = RealtimeCameraThread(size=self.VideoLabel.size(), timeout=10)

    def setup_ui(self):
        self.setupUi(self)
        self.setWindowTitle('AGV Camera')

    def startup(self):
        self.camera_thread.dispatched.connect(self.display)
        self.camera_thread.finished.connect(self.__on_finished)
        self.camera_thread.start()
        self.show()
        self.camera_thread.set_size(self.VideoLabel.size())

    def __on_finished(self, is_stop: bool):
        self.finished.emit(self.test_name, is_stop)
        self.camera_thread.quit()
        if self.isVisible():
            self.close()

    def shutdown(self):
        self.camera_thread.stop_running()

    def closeEvent(self, a0):
        self.shutdown()

    def display(self, pixmap: QPixmap):
        self.VideoLabel.setPixmap(pixmap)

    def opened(self):
        return self.camera_thread.is_opened
