#!/usr/bin/env python
import rospy
import actionlib
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from math import radians, degrees
from actionlib_msgs.msg import *
from geometry_msgs.msg import Point
class map_navigation():
  def __init__(self):
    self.xCafe = -0.419124215841
    self.yCafe = 0.090332865715
    self.goalReached = False
    rospy.init_node('map_navigation', anonymous=False)
    self.goalReached = self.moveToGoal(self.xCafe, self.yCafe)

  def shutdown(self):
        rospy.loginfo("Quit program")
        rospy.sleep()

  def moveToGoal(self,xGoal,yGoal):
      ac = actionlib.SimpleActionClient("move_base", MoveBaseAction)
      while(not ac.wait_for_server(rospy.Duration.from_sec(5.0))):
              rospy.loginfo("Waiting for the move_base action server to come up")

      goal = MoveBaseGoal()
      goal.target_pose.header.frame_id = "map"
      goal.target_pose.header.stamp = rospy.Time.now()
      goal.target_pose.pose.position =  Point(xGoal,yGoal,0)
      goal.target_pose.pose.orientation.x = 0.0
      goal.target_pose.pose.orientation.y = 0.0
      goal.target_pose.pose.orientation.z =  -0.80196930331
      goal.target_pose.pose.orientation.w =  0.597365245514

      rospy.loginfo("Sending goal location ...")
      ac.send_goal(goal)

      ac.wait_for_result(rospy.Duration(60))

      if(ac.get_state() ==  GoalStatus.SUCCEEDED):
              rospy.loginfo("You have reached the destination 1")
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