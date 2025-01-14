#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from core.command import Command

ROS_SETUP_FILEPATH = "/opt/ros/noetic/setup.bash"
ROS_WORKSPACE_FILEPATH = "/home/er/myagv_ros/devel/setup.bash"


def close_rviz():
    Command.kill("rviz")


def roslaunch(*args):
    command = " ".join(args)
    Command.run_in_terminal(
        f"source {ROS_SETUP_FILEPATH} && source {ROS_WORKSPACE_FILEPATH} && roslaunch {command}", keep=True
    )


def navigation_close():
    # os.system("ps -ef | grep -E rviz | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    # os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    close_rviz()
    Command.kill("navigation_active.launch")


def navigation_open():
    roslaunch("myagv_navigation", "navigation_active.launch")


def keyboard_open(cls):
    # ShellAPI.run_in_terminal("cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_teleop/launch/myagv_teleop.launch; exec bash")
    # os.system("gnome-terminal -e 'bash -c \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_teleop/launch/myagv_teleop.launch; exec bash\"'")
    Command.run_in_terminal("myagv_teleop myagv_teleop.launch", keep=True)


def keyboard_close():
    # close_command = "ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2"
    Command.kill("myagv_teleop.launch")


def joystick_open(cls):
    # launch_command = "roslaunch myagv_ps2 myagv_ps2.launch"
    # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
    Command.run_in_terminal("myagv_ps2 myagv_ps2.launch", keep=True)


def joystick_close():
    Command.kill("myagv_ps2.launch")


def joystick_close_number():
    Command.kill("myagv_ps2_number.launch")


def joystick_open_number(cls):
    # launch_command = "roslaunch myagv_ps2 myagv_ps2_number.launch"
    # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
    Command.run_in_terminal("myagv_ps2 myagv_ps2_number.launch", keep=True)


def gmapping_build_open(cls):
    # launch_command = "roslaunch myagv_navigation myagv_slam_laser.launch"
    # os.system("gnome-terminal -e 'bash -c
    # \"cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_navigation/launch/myagv_slam_laser.launch; exec bash\"'")
    command = "cd /home/ubuntu; roslaunch ~/myagv_ros/src/myagv_navigation/launch/myagv_slam_laser.launch"
    Command.run_in_terminal(command, keep=True)


def gampping_build_close():
    # os.system("ps -ef | grep -E rviz | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    # os.system("ps -ef | grep -E " + run_launch + " | grep -v 'grep' | awk '{print $2}' | xargs kill -2")
    close_launch = "myagv_slam_laser.launch"
    close_rviz()
    Command.kill(close_launch)


def save_map_file():
    # launch_command = "rosrun map_server map_saver"
    # subprocess.run(['gnome-terminal', '-e', f"bash -c '{launch_command}; exec $SHELL'"])
    Command.run_in_terminal("rosrun map_server map_saver", keep=True)
