#!/usr/bin/env python

import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point
#from sound_play.libsoundplay import SoundClient

class map_navigation():



  def __init__(self):

    #sc = SoundClient()
    #path_to_sounds = "/home/ros/catkin_ws/src/gaitech_edu/src/sounds/"

    # declare the coordinates of interest
    self.xCafe = -0.122906163335
    self.yCafe = 0.0972566530108

    self.goalReached = False
    # initiliaze
    rospy.init_node('map_navigation', anonymous=False)
    self.goalReached = self.moveToGoal(self.xCafe, self.yCafe)

   


  def shutdown(self):
        # stop turtlebot
        rospy.loginfo("Quit program")
        rospy.sleep()

  def moveToGoal(self,xGoal,yGoal):

      #define a client for to send goal requests to the move_base server through a SimpleActionClient
      ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)

      #wait for the action server to come up
      while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
              rospy.loginfo("Waiting for the move_base action server to come up")


      goal = MoveBaseGoal()

      #set up the frame parameters
      goal.target_pose.header.frame_id = "map"
      goal.target_pose.header.stamp = rospy.Time.now()

      # moving towards the goal*/

      goal.target_pose.pose.position =  Point(xGoal,yGoal,0)
      goal.target_pose.pose.orientation.x = 0.0
      goal.target_pose.pose.orientation.y = 0.0
      goal.target_pose.pose.orientation.z =  -0.0932167360737
      goal.target_pose.pose.orientation.w =  0.996503720099

      rospy.loginfo("Sending goal location ...")
      ac.send_goal(goal)

      ac.wait_for_result(rospy.Duration(60))

      if(ac.get_state() ==  GoalStatus.SUCCEEDED):
              rospy.loginfo("You have reached the destination 4")
              return True
      else:
              rospy.loginfo("The robot failed to reach the destination")
              return False

if __name__ == '__main__':
    try:

        rospy.loginfo("You have reached the destination")
        map_navigation()
        

    except rospy.ROSInterruptException:
        rospy.loginfo("map_navigation node terminated.")