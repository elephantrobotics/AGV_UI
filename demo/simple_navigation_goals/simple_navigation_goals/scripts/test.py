#!/usr/bin/env python
import test_auto_charing                                                                                                                                                                                   
import rospy
import time
import agv_aruco
import actionlib
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

    def set_pose(self):
        pose = PoseWithCovarianceStamped()
        pose.header.seq = 0
        pose.header.stamp.secs = 0
        pose.header.stamp.nsecs = 0
        pose.header.frame_id = 'map'
        pose.pose.pose.position.x = 0.0201717317104
        pose.pose.pose.position.y = 0.0658675357699
        pose.pose.pose.position.z = 0.0
        q = quaternion_from_euler(0, 0, 1.57)  
        pose.pose.pose.orientation.x = 0.0
        pose.pose.pose.orientation.y = 0.0
        pose.pose.pose.orientation.z = -1.02788762886e-05
        pose.pose.pose.orientation.w =0.999995620035
        pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.068533892326654787]
        rospy.sleep(1)
        self.pub.publish(pose)
        rospy.loginfo('Published robot pose: %s' % pose)

class MapNavigation:
    def __init__(self):
        self.goalReached = False
        rospy.init_node('map_navigation', anonymous=False)
    def moveToGoal(self, xGoal, yGoal, orientation_z, orientation_w):
        ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
            ##stop_client = actionlib.SimpleActionClient('move_base', MoveBaseAction)
          #  stop_client.wait_for_server()
           # goal = MoveBaseGoal()
           # stop_client.send_goal(goal)
           # stop_client.wait_for_result()
            sys.exit(0)
            #return False
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


if __name__ == '__main__':
   
       # set_robot_pose = SetRobotPose()
       # set_robot_pose.set_pose()

    




    map_navigation = MapNavigation()

    goals = [
        (0.229920655489 ,-0.468442887068 , -0.566741287911 ,0.823895814152),
        (0.663715600967 ,  0.363270163536 , 0.294119799193,0.955768561799)
    ]

    for i in range(1):
        for goal in goals:
            x_goal, y_goal, orientation_z, orientation_w = goal
            map_navigation.navigate(x_goal, y_goal, orientation_z, orientation_w)
            time.sleep(2)

            agv_aruco.main()



