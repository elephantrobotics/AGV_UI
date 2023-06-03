#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy
from geometry_msgs.msg import Twist
import time
def move_forward():
    twist = Twist()
    twist.linear.x = 0.2
    twist.angular.z = 0
    return twist

def move_backward():
    twist = Twist()
    twist.linear.x = -0.2
    twist.angular.z = 0
    return twist

def turn_left():
    twist = Twist()
    twist.linear.x = 0
    twist.angular.z = 0.5
    return twist

def turn_right():
    twist = Twist()
    twist.linear.x = 0
    twist.angular.z = -0.5
    return twist

def left():
    twist = Twist()
    twist.linear.y = 0.3
    twist.angular.z =0
    return twist

def right():
    twist = Twist()
    twist.linear.y = -0.3
    twist.angular.z =0
    return twist

def stop():
    twist = Twist()
    twist.linear.y = 0
    twist.angular.z = 0
    return twist

if __name__=="__main__":
    rospy.init_node('myagv_auto')
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    pub.publish(stop()) 
    print("start")
    rospy.sleep(1)

    pub.publish(move_forward()) 
    print("forward")
    rospy.sleep(3)

    
    pub.publish(move_backward()) 
    print("backward")
    rospy.sleep(3)

    pub.publish(turn_right()) 
    print("turn_right")
    rospy.sleep(3)

    
    pub.publish(turn_left()) 
    print("turn_left")
    rospy.sleep(5)    

    pub.publish(left()) 
    print("left")
    rospy.sleep(2)

    
    pub.publish(right()) 
    print("right")
    rospy.sleep(2)

    pub.publish(stop())  
    rospy.sleep(2)
    print("stop")
