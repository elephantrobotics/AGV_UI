#!/usr/bin/env python
import rospy
from actionlib_msgs.msg import GoalID

def cancel_goal():
    pub = rospy.Publisher('/move_base/cancel', GoalID, queue_size=10)
    goal_id = GoalID()
    pub.publish(goal_id)

if __name__ == '__main__':
    rospy.init_node('cancel_goal_node', anonymous=True)
    cancel_goal()
    print ('state 1')
