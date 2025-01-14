#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
from core import GpioHandler, GlobalVar, Command
from functions import roslaunch


class Functional:

    @classmethod
    def init_pump(cls):
        # init
        # GpioHandler.setmode(GpioHandler.BCM)
        GpioHandler.setup(GlobalVar.suction_pump_pins[0], GpioHandler.OUT)
        GpioHandler.setup(GlobalVar.suction_pump_pins[1], GpioHandler.OUT)

    @classmethod
    def turn_on_pump(cls):
        # open
        GpioHandler.output(GlobalVar.suction_pump_pins[1], GpioHandler.LOW)
        time.sleep(0.5)
        GpioHandler.output(GlobalVar.suction_pump_pins[0], GpioHandler.HIGH)

    @classmethod
    def turn_off_pump(cls):
        # close
        GpioHandler.output(GlobalVar.suction_pump_pins[1], GpioHandler.HIGH)
        GpioHandler.output(GlobalVar.suction_pump_pins[0], GpioHandler.LOW)
        time.sleep(0.05)
        GpioHandler.output(GlobalVar.suction_pump_pins[0], GpioHandler.HIGH)

    @classmethod
    def radar_open(cls):
        GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.OUT)
        GpioHandler.output(GlobalVar.radar_control_pin, GpioHandler.HIGH)
        roslaunch.roslaunch('myagv_odometry myagv_active.launch')

    @classmethod
    def radar_close(cls):
        GpioHandler.setup(GlobalVar.radar_control_pin, GpioHandler.OUT)
        GpioHandler.output(GlobalVar.radar_control_pin, GpioHandler.LOW)
        if Command.alive("myagv_active.launch"):
            Command.kill("myagv_active.launch")

    @classmethod
    def check_radar_running(cls):
        return Command.alive("myagv_active.launch") or GpioHandler.ishigh(GlobalVar.radar_control_pin)


