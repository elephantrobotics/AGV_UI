#!/usr/bin/env python
import test_auto_charing                                                                                                                        
import rospy
import time
import agv_aruco
import agv_aruco_1
import actionlib
import socket
import threading
from pick import pick


import numpy as np
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf.transformations import quaternion_from_euler
from std_srvs.srv import Empty
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point


global socket_res
socket_res = None

class MapNavigation:

    def set_pose(self):
        pose = PoseWithCovarianceStamped()
        pose.header.seq = 0
        pose.header.stamp.secs = 0
        pose.header.stamp.nsecs = 0
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x =0.535247802734
        pose.pose.pose.position.y =-0.0171256065369
        pose.pose.pose.position.z = 0.0
        q = quaternion_from_euler(0, 0, 1.57)  
        pose.pose.pose.orientation.x = 0.0
        pose.pose.pose.orientation.y = 0.0
        pose.pose.pose.orientation.z = 0.00373901184227
        pose.pose.pose.orientation.w = 0.978502650446
        pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.068533892326654787]
        rospy.sleep(1)
        self.pub.publish(pose)
        rospy.loginfo('Published robot pose: %s' % pose)

    def set_pose_1(self):
        pose = PoseWithCovarianceStamped()
        pose.header.seq = 0
        pose.header.stamp.secs = 0
        pose.header.stamp.nsecs = 0
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x =-0.0369547009468
        pose.pose.pose.position.y =0.0794232487679
        pose.pose.pose.position.z = 0.0
        q = quaternion_from_euler(0, 0, 1.57)  
        pose.pose.pose.orientation.x = 0.0
        pose.pose.pose.orientation.y = 0.0
        pose.pose.pose.orientation.z = 0.738174798162
        pose.pose.pose.orientation.w = 0.674609492491
        pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.068533892326654787]
        rospy.sleep(1)
        self.pub.publish(pose)
        rospy.loginfo('Published robot pose: %s' % pose)

    def __init__(self):

        self.pub = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10)
        rospy.init_node('map_navigation', anonymous=False)
        self.goalReached = False

    def moveToGoal(self, xGoal, yGoal, orientation_z, orientation_w):
        ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
      
            sys.exit(0)

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position =  Point(xGoal, yGoal, 0)
        goal.target_pose.pose.orientation.x = 0.0
        goal.target_pose.pose.orientation.y = 0.0
        goal.target_pose.pose.orientation.z = orientation_z 
        goal.target_pose.pose.orientation.w = orientation_w

        rospy.loginfo("Sending goal location ...")
        ac.send_goal(goal)

        ac.wait_for_result(rospy.Duration(60))

        if(ac.get_state() ==  GoalStatus.SUCCEEDED):
            rospy.loginfo("You have reached the destination")
            return True
        else:
            rospy.loginfo("The robot failed to reach the destination")
            return False

    def shutdown(self):
        rospy.loginfo("Quit program")
        rospy.sleep()

    def navigate(self, xGoal, yGoal, orientation_z, orientation_w):
        self.goalReached = self.moveToGoal(xGoal, yGoal, orientation_z, orientation_w)

def socket_connect(data):

    conn.send(data.encode("UTF-8"))


def get_res():
    while 1:
        global socket_res
        print('get_res')
        data = conn.recv(1024).decode("UTF-8")

        print("from user:%s" % data)
        socket_res = data
        print(socket_res)




if __name__ == '__main__':
   
    goal_2 = [(-0.0291289053857,-0.138362124562, 0 ,1)]
    goal_1 = [(0.677817523479 , 0.302406698465 ,  0 ,1)]
    socket_res = ''
    map_navigation = MapNavigation()

    server_ip = '192.168.12.31'
    server_port = 9000

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((server_ip, server_port))

    server_socket.listen(3)
    server_socket.settimeout(None)
    result = server_socket.accept()
    conn = result[0] 
    address = result[1]  

    # while 1:
    #     if socket_res == 'robot_move':
    #         sorting()
   # y=0

    t = threading.Thread(target=get_res)
    t.start()

    while 1:
        if socket_res == 'go_to_feed':
            for goal in goal_1:
                x_goal, y_goal, orientation_z, orientation_w = goal
                map_navigation.navigate(x_goal, y_goal, orientation_z, orientation_w)
                time.sleep(2)
                agv_aruco.main()
                time.sleep(2)
                socket_connect('arrive_feed')
                socket_res = None
        if socket_res == 'picking_finished':
            pub_vel(0,0,0)
            time.sleep(3)
            pub_vel(-0.1,0,0)
            time.sleep(3)
            pub_vel(0,0.1,0)
            time.sleep(2)

            # map_navigation.set_pose()
            # time.sleep(3)
            socket_res = 'go_to_unload'

        if socket_res == 'go_to_unload':
            for goal in goal_2:
                x_goal, y_goal, orientation_z, orientation_w = goal
                map_navigation.navigate(x_goal, y_goal, orientation_z, orientation_w)
                time.sleep(2)
                # agv_aruco_1.main()
                time.sleep(2)
                map_navigation.set_pose_1()
                time.sleep(3)
                #socket_connect('pi_down')
                pick()
                socket_res = 'placed_finished'


        if socket_res == 'placed_finished':
            # pub_vel(0,0,0)
            # time.sleep(3)
            # pub_vel(-0.1,0,0)
            # time.sleep(3)
            # pub_vel(0,0.1,0)
            # time.sleep(2)
            socket_res = 'agv_feed'
       # ptint("y=" y+1)