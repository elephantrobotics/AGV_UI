# coding=utf8
import struct
import numpy as np
import math
import time
import threading
import cv2
import sys
import cv2.aruco as aruco
import rospy
from std_msgs.msg import Int8
from geometry_msgs.msg import Twist
import RPi.GPIO as GPIO


twist = None
pub = None
font = None
marker_length = None
camera_matrix =None
dist_coeffs  =None
frame =None
R_flip =None
pose_data =None
pose_data_dict =None

def init():
    global twist
    global pub
    global font
    global marker_length
    global camera_matrix
    global dist_coeffs
    global frame
    global R_flip
    global pose_data
    global pose_data_dict

    x = 0
    y = 0
    theta = 0
    rospy.init_node('qcode_detect', anonymous=True)
    # rospy.init_node('get_oltage', anonymous=True)
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    twist = Twist()


# the threshold of the angle
def v_cllback(msg):
    if msg.data >= 11:
        print('bac1')
        go(-0.1, 0, 0)
        time.sleep(3)
        print('00010001')
        go(0, 0, 0)
        sys.exit(0)


# ����С���˶�������cmd_vel����
def go(x, y, theta):
    twist.linear.x = x;
    twist.linear.y = y;
    twist.linear.z = 0
    twist.angular.x = 0;
    twist.angular.y = 0;
    twist.angular.z = theta
    pub.publish(twist)


def main():

    print('000')
    go(0, 0, 0)
    time.sleep(3)
    print('101010')
    go(10, 10, 10)
    rospy.Subscriber("Voltage", Int8, v_cllback)
    rospy.spin()


if __name__ == '__main__':
    init()
    print("TWIST " , twist)
    try:
        main()
    # go(10,10,10)
    # for i in range(1,850000):
    #     i=i+1
    #     go(0.1,0,0)
    # for i in range(1,400):
    #     i=i+1
    # go(0.2,0,0)
    except rospy.ROSInterruptException:
        go(0, 0, 0)
    finally:
        go(0, 0, 0)
