#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from .command import Terminal

ROS_SETUP_FILEPATH = "/opt/ros/noetic/setup.bash"
ROS_WORKSPACE_FILEPATH = "/home/er/myagv_ros/devel/setup.bash"

# 导航文件
NAVIGATION_LAUNCH_FILENAME = "navigation_active.launch"


def close_rviz():
    Terminal.kill("rviz")


def roslaunch(*args):
    command = " ".join(args)
    Terminal.run_in_terminal(
        f"source {ROS_SETUP_FILEPATH} && source {ROS_WORKSPACE_FILEPATH} && roslaunch {command}", keep=True
    )


def navigation_close():
    # os.system("ps -ef | grep -E rviz | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    # os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    close_rviz()
    Terminal.kill(NAVIGATION_LAUNCH_FILENAME)


def navigation_open():
    roslaunch("myagv_navigation", NAVIGATION_LAUNCH_FILENAME)

