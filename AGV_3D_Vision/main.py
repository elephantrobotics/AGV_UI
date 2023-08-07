    #from R1Control.Common import *
from CvDetection.detection import Detector
from R1Control.RobotR1 import RobotR1
from R1Control.VideoCapture3d import VideoCaptureThread
from CvDetection.VideoStreamPipe import VideoStreamPipe
import serial.tools.list_ports
import time
import socket
import inspect
import ctypes
import select

def CycleSendText():
    # AGV IP and port
    host = ""
    port = 9005
    # connect to the server
    tcpclient =socket.socket()
    tcpclient.connect((host,port))
    # connect to the 270
    r1 = RobotR1()
    # connect to the video
    capture_thread = VideoCaptureThread(Detector("apple"), Detector.FetchType.FETCH.value)
    capture_thread.daemon = True
    capture_thread.start()
    # send _data
    send_data = "go_to_feed"
    tcpclient.send(send_data.encode())
    info = tcpclient.recv(1024).decode()
    while True:
        read_to_read,_,_ = select.select([tcpclient],[],[],1)
        if read_to_read:
            info = tcpclient.recv(1024).decode()
        if info == "arrive_feed":
            while r1.i < 3:
                r1.motion(capture_thread)
                time.sleep(1)
            else:
                r1.i = -1
                send_data = "picking_finished"
                tcpclient.send(send_data.encode())
                info = None
            r1.move_end(50,1)

def test():
    r1 = RobotR1()
    # connect to the video
    capture_thread = VideoCaptureThread(Detector("apple"), Detector.FetchType.FETCH.value)
    capture_thread.daemon = True
    capture_thread.start()
    while True:
        while r1.i < 3:
            r1.motion(capture_thread)
            time.sleep(1)
        else:
            r1.i = -1

if __name__ == "__main__":
    #CycleSendText()
    test()





