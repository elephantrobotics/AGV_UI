#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
from core import GpioHandler, GlobalVar, Command


ROS_SETUP_FILEPATH = "/opt/ros/noetic/setup.bash"
ROS_WORKSPACE_FILEPATH = "/home/er/myagv_ros/devel/setup.bash"
COMMAND_SEPARATOR = " "


def roslaunch(*args, workspace: bool = True):
    command = f"roslaunch {COMMAND_SEPARATOR.join(args)}"
    if workspace is True:
        command = f"source {ROS_SETUP_FILEPATH} && source {ROS_WORKSPACE_FILEPATH} && {command}"

    Command.run_in_terminal(command=command, keep=True)


def rosrun(*args):
    command = f"source {ROS_SETUP_FILEPATH} && source {ROS_WORKSPACE_FILEPATH} && rosrun {COMMAND_SEPARATOR.join(args)}"
    Command.run_in_terminal(command=command, keep=True)


class Functional:

    @classmethod
    def init_pump(cls):
        GpioHandler.setup(GlobalVar.suction_pump_pins[0], GpioHandler.OUT)
        GpioHandler.setup(GlobalVar.suction_pump_pins[1], GpioHandler.OUT)

    @classmethod
    def turn_on_pump(cls):
        GpioHandler.output(GlobalVar.suction_pump_pins[1], GpioHandler.LOW)
        time.sleep(0.5)
        GpioHandler.output(GlobalVar.suction_pump_pins[0], GpioHandler.HIGH)

    @classmethod
    def turn_off_pump(cls):
        GpioHandler.output(GlobalVar.suction_pump_pins[1], GpioHandler.HIGH)
        GpioHandler.output(GlobalVar.suction_pump_pins[0], GpioHandler.LOW)
        time.sleep(0.05)
        GpioHandler.output(GlobalVar.suction_pump_pins[0], GpioHandler.HIGH)

    @classmethod
    def radar_open(cls):
        GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.OUT)
        GpioHandler.output(GlobalVar.radar_control_pin, GpioHandler.HIGH)
        roslaunch('myagv_odometry myagv_active.launch')

    @classmethod
    def radar_close(cls):
        GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.OUT)
        GpioHandler.output(GlobalVar.radar_control_pin, GpioHandler.LOW)
        if Command.alive("myagv_active.launch"):
            Command.kill("myagv_active.launch")

    @classmethod
    def check_radar_running(cls):
        return Command.alive("myagv_active.launch") or GpioHandler.ishigh(GlobalVar.radar_control_pin)

    @classmethod
    def open_keyboard_control(cls):
        roslaunch("myagv_teleop", "myagv_teleop.launch", workspace=False)  # keyboard

    @classmethod
    def close_keyboard_control(cls):
        Command.kill("myagv_teleop.launch")

    @classmethod
    def open_joystick_alphabet_control(cls):
        roslaunch("myagv_ps2", "myagv_ps2.launch", workspace=False)  # joystick

    @classmethod
    def close_joystick_alphabet_control(cls):
        Command.kill("myagv_ps2.launch")

    @classmethod
    def open_joystick_number_control(cls):
        roslaunch("myagv_ps2", "myagv_ps2_number.launch", workspace=False)  # joystick

    @classmethod
    def close_joystick_number_control(cls):
        Command.kill("myagv_ps2_number.launch")

    @classmethod
    def open_gmapping_mapping(cls):
        roslaunch("myagv_navigation", "myagv_slam_laser.launch")  # gmapping

    @classmethod
    def close_gmapping_mapping(cls):
        Command.kill("myagv_slam_laser.launch")

    @classmethod
    def open_rtabmap_mapping(cls):
        roslaunch("myagv_navigation", "rtabmap_mapping.launch")  # rtabmap

    @classmethod
    def close_rtabmap_mapping(cls):
        Command.kill("rtabmap_mapping.launch")

    @classmethod
    def save_gmapping_map(cls):
        rosrun("map_server", "map_saver")  # 保存建图

    @classmethod
    def open_singlepoint_navigation(cls):
        roslaunch("myagv_navigation", "navigation_active.launch")  # 单点导航

    @classmethod
    def close_singlepoint_navigation(cls):
        Command.kill("navigation_active.launch")

    @classmethod
    def open_multipoint_navigation(cls):
        # 多点导航
        roslaunch("myagv_navigation", "multipoint_navigation_active.launch")

    @classmethod
    def close_multipoint_navigation(cls):
        Command.kill("multipoint_navigation_active.launch")

    @classmethod
    def open_3d_navigation(cls):
        roslaunch("myagv_navigation", "3d_navigation_active.launch")

    @classmethod
    def close_3d_navigation(cls):
        Command.kill("3d_navigation_active.launch")

    @classmethod
    def open_3d_camera(cls):
        Command.run_in_terminal("roslaunch orbbec_camera astra_pro2.launch", keep=True)

    @classmethod
    def close_3d_camera(cls):
        Command.kill("astra_pro2.launch")

    @classmethod
    def camera_3d_alive(cls):
        return Command.alive("astra_pro2.launch")
