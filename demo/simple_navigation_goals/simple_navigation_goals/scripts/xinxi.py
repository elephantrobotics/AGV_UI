#!/usr/bin/env python
import rospy
import tf
from geometry_msgs.msg import PointStamped

if __name__ == '__main__':
    rospy.init_node('agv_position_listener')
    listener = tf.TransformListener()
    rate = rospy.Rate(10.0)
    while not rospy.is_shutdown():
        try:

            (trans, rot) = listener.lookupTransform('/map', '/base_up', rospy.Time(0))

            print("AGV position: x={}, y={}, z={}".format(trans[0], trans[1], trans[2]))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            continue
        rate.sleep()
