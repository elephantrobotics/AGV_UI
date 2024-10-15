import sys
import cv2
import time
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

finish_flag = False


class CameraThread(QThread):
    image_ready = Signal(QImage)
    thread_finished = Signal()

    def __init__(self):
        super().__init__()
        self.__running = True

    def stop_running(self):
        self.__running = False

    def run(self):
        start_time = time.time()
        cap = cv2.VideoCapture(0)
        while time.time() - start_time < 10:
            ret, frame = cap.read()

            print(time.time() - start_time, "time--")
            if self.__running is False:
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_ready.emit(q_image)
        else:
            self.thread_finished.emit()


class CameraWindow(QMainWindow, QThread):
    camera_finish = Signal(str, bool)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        self.label = QLabel()
        layout.addWidget(self.label)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.camera_thread = CameraThread()
        self.camera_thread.image_ready.connect(self.display_image)
        self.camera_thread.thread_finished.connect(self.close_window)  # 连接线程结束信号和关闭窗口槽函数
        self.camera_thread.start()

    def display_image(self, image):
        pixmap = QPixmap.fromImage(image)
        self.label.setPixmap(pixmap)

    def close_window(self, is_stop=False):
        if is_stop:
            self.camera_thread.thread_finished.disconnect(self.close_window)
            self.camera_thread.stop_running()
            # self.camera_thread.terminate()
        self.camera_finish.emit("2D Camera", is_stop)
        self.camera_thread.quit()
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())
