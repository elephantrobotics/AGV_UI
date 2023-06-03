#!/usr/bin/env python
import test_auto_charing                                                                                                                        
import rospy
import time
import agv_aruco
import agv_aruco_1
import actionlib
import numpy as np
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf.transformations import quaternion_from_euler
from std_srvs.srv import Empty
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point


class SetRobotPose:
    def __init__(self):

        self.pub = rospy.Publisher('initialpose', PoseWithCovarianceStamped, queue_size=10)
        rospy.init_node('map_navigation', anonymous=False)
        self.goalReached = False

    def set_pose(self):
        pose = PoseWithCovarianceStamped()
        pose.header.seq = 0
        pose.header.stamp.secs = 0
        pose.header.stamp.nsecs = 0
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x =0.318938016891
        pose.pose.pose.position.y =-0.041979894042
        pose.pose.pose.position.z = 0.0
        q = quaternion_from_euler(0, 0, 1.57)  
        pose.pose.pose.orientation.x = 0.0
        pose.pose.pose.orientation.y = 0.0
        pose.pose.pose.orientation.z = -0.206234243203
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

class MapNavigation1():
    def __init__(self):
        self.xCafe = 0.659595251083 
        self.yCafe = 0.0182209927589
        self.goalReached = False
        rospy.init_node('map_navigation', anonymous=False)

    def moveToGoal(self, xGoal, yGoal):
        ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
            rospy.loginfo("Waiting for the move_base action server to come up")

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position =  Point(xGoal, yGoal, 0)
        goal.target_pose.pose.orientation.x = 0.0
        goal.target_pose.pose.orientation.y = 0.0
        goal.target_pose.pose.orientation.z =  0.130239713964
        goal.target_pose.pose.orientation.w = 0.991482534847

        rospy.loginfo("Sending goal location ...")
        ac.send_goal(goal)

        ac.wait_for_result(rospy.Duration(60))

        if(ac.get_state() ==  GoalStatus.SUCCEEDED):
            rospy.loginfo("You have reached the destination 1")
            return True
        else:
            rospy.loginfo("The robot failed to reach the destination")
            return False

    def shutdown(self):
        rospy.loginfo("Quit program")
        rospy.sleep()

    def navigate(self):
        self.goalReached = self.moveToGoal(self.xCafe, self.yCafe)
        
class MapNavigation2():

    def __init__(self):
        self.xCafe = -0.0304405391216
        self.yCafe = 0.166388019919
        self.goalReached = False

    def moveToGoal(self, xGoal, yGoal):
        ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
            rospy.loginfo("Waiting for the move_base action server to come up")

        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = "map"
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose.position =  Point(xGoal, yGoal, 0)
        goal.target_pose.pose.orientation.x = 0.0
        goal.target_pose.pose.orientation.y = 0.0
        goal.target_pose.pose.orientation.z =  0.879178855259
        goal.target_pose.pose.orientation.w = 0.476491910178

        rospy.loginfo("Sending goal location ...")
        ac.send_goal(goal)

        ac.wait_for_result(rospy.Duration(60))

        if(ac.get_state() ==  GoalStatus.SUCCEEDED):
            rospy.loginfo("You have reached the destination 2")
            return True
        else:
            rospy.loginfo("The robot failed to reach the destination")
            return False

    def shutdown(self):
        rospy.loginfo("Quit program")
        rospy.sleep()

    def navigate(self):
        self.goalReached = self.moveToGoal(self.xCafe, self.yCafe)
        

if __name__ == '__main__':
    
    for i in range(10):   
   

        map_navigation = MapNavigation1()
        map_navigation.navigate()
        time.sleep(2)

        agv_aruco.main()
        time.sleep(2)

        set_robot_pose = SetRobotPose()
        set_robot_pose.set_pose()
        time.sleep(2)

        map_navigation = MapNavigation2()
        map_navigation.navigate()
        time.sleep(2)

        agv_aruco_1.main()
        time.sleep(2)

        set_robot_pose = SetRobotPose()
        set_robot_pose.set_pose_1()
        time.sleep(2)
      
    