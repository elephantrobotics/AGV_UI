import sys
import cv2
import time
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

finish_flag=False

class CameraThread(QThread):
    image_ready = Signal(QImage)
    thread_finished = Signal()

    def run(self):
        start_time = time.time()
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()

            print(time.time() - start_time, "time--")
            if time.time() - start_time >= 5:
                # finish_flag=True
                break
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.image_ready.emit(q_image)

        self.thread_finished.emit()


class CameraWindow(QMainWindow, QThread):

    camera_finish=Signal(str)

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

    def close_window(self):
        self.camera_finish.emit("2D Camera")
        self.camera_thread.quit()
        self.close()  # 在窗口关闭槽函数中关闭窗口
        
        # from operations import myAGV_windows
        # myAGV_windows.prrr("sssss")
        # myAGV_windows.testing_finished("2D Camera")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CameraWindow()
    window.show()
    sys.exit(app.exec_())
