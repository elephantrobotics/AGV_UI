#!/usr/bin/env python
# import test_auto_charing
import rospy
import time
import actionlib
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf.transformations import quaternion_from_euler
from std_srvs.srv import Empty
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point

#test_auto_charing.some_function()
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
        pose.pose.pose.position.x = 0.090062927628
        pose.pose.pose.position.y = 0.143029577136
        pose.pose.pose.position.z = 0.0
        q = quaternion_from_euler(0, 0, 1.57)  
        pose.pose.pose.orientation.x = 0.0
        pose.pose.pose.orientation.y = 0.0
        pose.pose.pose.orientation.z = -0.1805217571503
        pose.pose.pose.orientation.w = 0.978716377888
        pose.pose.covariance = [0.25, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
         0.0, 0.0, 0.0, 0.0, 0.0, 0.068533892326654787]
        rospy.sleep(1)
        self.pub.publish(pose)
        rospy.loginfo('Published robot pose: %s' % pose)

class MapNavigation1:
    def __init__(self):
        self.xCafe = -0.419124215841
        self.yCafe = 0.090332865715
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
        goal.target_pose.pose.orientation.z = -0.80196930331
        goal.target_pose.pose.orientation.w = 0.597365245514

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
        

class MapNavigation2:
    def __init__(self):
        self.xCafe = -0.536592960358
        self.yCafe = -0.565056025982
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
        goal.target_pose.pose.orientation.z =  -0.0835484041125
        goal.target_pose.pose.orientation.w =  0.996503720099

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
        
class MapNavigation3:

   def __init__(self):
        
        self.xCafe = -0.803486943245
        self.yCafe = -0.643324017525
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
        goal.target_pose.pose.orientation.z = 0.589739012406
        goal.target_pose.pose.orientation.w = 0.807593893765

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
        
class MapNavigation4:
    def __init__(self):
        self.xCafe = -0.122906163335
        self.yCafe = 0.0972566530108
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
        goal.target_pose.pose.orientation.z =  -0.0932167360737
        goal.target_pose.pose.orientation.w =  0.996503720099

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
        

# if __name__ == '__main__':
#     try:
#         set_robot_pose = SetRobotPose()
#         set_robot_pose.set_pose()
#         map_navigation = MapNavigation1()
#         map_navigation.navigate()
#         map_navigation = MapNavigation2()
#         map_navigation.navigate()
#         test_auto_charing.init()
#         test_auto_charing.main()
#         map_navigation = MapNavigation3()
#         map_navigation.navigate()
#         map_navigation = MapNavigation4()
#         map_navigation.navigate()
#         test_auto_charing.init()
#         test_auto_charing.main()
#         set_robot_pose = SetRobotPose()
#         set_robot_pose.set_pose()
#         # map_navigation = MapNavigation3
#     except rospy.ROSInterruptException:
#             rospy.loginfo("map_navigation node terminated.")