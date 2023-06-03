# coding=utf8
import math
import time
import threading
import numpy as np
import aruco_detector
import rospy
from std_msgs.msg import Int8
from geometry_msgs.msg import Twist

DETECT = False

aruco_detector_res = None
ids = None
pub = None
rate = None
_id_get = 0


def main():
    global pub
    global rate
    try:
        rospy.init_node('qcode_detect', anonymous=True)
    except rospy.exceptions.ROSException as e:
        print("Node has already been initialized, do nothing")
    rate = rospy.Rate(30)
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    time.sleep(1)
    goPosition(1)
    time.sleep(2)


States = ['first point', 'first point back', 'second point back', 'second point']


def movelittle():
    print "once"


def pub_vel(x, y, theta):
    twist = Twist()
    twist.linear.x = x
    twist.linear.y = y
    twist.linear.z = 0
    twist.angular.x = 0
    twist.angular.y = 0
    twist.angular.z = theta
    pub.publish(twist)


def stop():
    pub_vel(0, 0, 0)


def processY_small(_state, _detect_res):
    print("process y small")
    default_y_vel = 0.1

    if _detect_res is not None:
        print(_detect_res)
        cam_y = _detect_res[0][0]
        print("current y dis" + str(cam_y))

        if abs(cam_y) < 1:
            print("stop")
            stop()
            time.sleep(1)
            return _state + 1
            print('state 1+1')
        else:
            pub_vel(0, -np.sign(cam_y) * default_y_vel, 0)
            print("_detect_res", _detect_res)
            return _state
    else:
        pub_vel(0, 0, -0.1)
        print("can't find qr code in short dis")
        return _state


def faceToQr(_state, _detect_res):
    l = _detect_res[0][2]
    theta = _detect_res[0][4]
    theta_rad = theta * math.pi / 180.0
    y_distance = math.sin(theta_rad) * l

    kp_y = 1.5
    kp_theta = 0.7

    y_vel = y_distance / 100.0 * kp_y
    theta_vel = theta / 100.0 * kp_theta
    print("l=", l)
    print("_detect_res", _detect_res)
    if _detect_res is not None:
        if abs(theta) <= 5 and abs(y_distance) <= 2:
            print("stop face to qr")
            stop()
            time.sleep(1)
            return _state + 1
        else:
            print(y_distance, theta), (y_vel, theta_vel)
            pub_vel(0, -y_vel, theta_vel)
            return _state
    else:
        print("can't find erweima")

        pub_vel(0, 0, -0.1)
        return _state


def goPosition(cmd=0):
    state = 0
    protect_sec = 60
    time_count_start = time.time()

    while True:
        data_rec = aruco_detector.getArucoCode(display_mode=True)
        if data_rec is not None:
            aruco_detector_res, ids = data_rec[0], data_rec[1]
            _id_get = ids[0][0]
            time_count_start = time.time()
            target = 1
        else:
            aruco_detector_res = None
            ids = None
            _id_get = 0

            time_gap = time.time() - time_count_start

        if aruco_detector_res is not None:
            if len(aruco_detector_res) == 1:
                pass
                # processMovements(aruco_detector_res)
        else:
            pass
            # continue

        if cmd == 0:
            pass
            if aruco_detector_res is not None:
                if len(aruco_detector_res) == 1:
                    faceToQr(state, aruco_detector_res)
        elif cmd == 1:
            y_dir = 31  # 1 for left, -1 for right
            id_find = 31  # 1 and 4
            # combination (-1,1) ; (1,4)
            back_dis = 20

            if state == 0:  # backward
                print('state 0')
                pub_vel(0, 0, -0.2)
                if aruco_detector_res is not None:
                    if len(aruco_detector_res) == 1:
                        state += 1
                        print('state 0+1')

            elif state == 1:
                print('state 1')
                state = processY_small(state, aruco_detector_res)  # 1 to 4 to left

            elif state == 2:
                print('state 2')
                if aruco_detector_res is not None:
                    state = faceToQr(state, aruco_detector_res)

            elif state == 3:
                print('state 3')
                pub_vel(0.1, 0, 0)
                time.sleep(4)
                state += 1

            elif state == 4:
                print('state 4')
                pub_vel(0, 0, 0)
                time.sleep(3)
                pub_vel(-0.1, 0, 0)
                time.sleep(3)
                pub_vel(0, 0.1, 0)
                time.sleep(2)
                state += 1

            else:
                stop()
                break

        else:
            pub_vel(0, 0, 0)

        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.exceptions.ROSException as e:
        print("Node has already been initialized, do nothing")
