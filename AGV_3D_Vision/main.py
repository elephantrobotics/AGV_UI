from R1Control.Common import *
from CvDetection.detection import Detector
from R1Control.RobotR1 import RobotR1
from R1Control.VideoCapture3d import VideoCaptureThread
import serial.tools.list_ports
import time

def main():
    r1 = RobotR1(sorted([str(x).split(" - ")[0].strip() for x in serial.tools.list_ports.comports()])[0])

    capture_thread = VideoCaptureThread(Detector("apple"), Detector.FetchType.FETCH.value)
    capture_thread.daemon = True
    capture_thread.start()

    while True:
        r1.motion(capture_thread)
        time.sleep(1)

    capture_thread.join()
