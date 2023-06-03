#!/usr/bin/env python

import rospy
from actionlib_msgs.msg import GoalID

rospy.init_node('move_base_cancel_publisher')

pub = rospy.Publisher('/move_base/cancel', GoalID, queue_size=10)

goal_id = GoalID()

while not rospy.is_shutdown():
    pub.publish(goal_id)
    rospy.sleep(0.1)
