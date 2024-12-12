#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time

from pymycobot import MyAgv
from .command import ShellAPI
from . import GlobalVar, roslaunch


class AgvHandler(object):

    def __init__(self, agv: MyAgv, radar_pin: int, suction_pump_pins: tuple, debug: bool = False):
        self.agv = agv
        self.radar_pin = radar_pin
        self.suction_pump_pins = suction_pump_pins
        self.debug = debug

    def get_system_version(self):
        firmware_version = self.agv.get_firmware_version()
        # modified_version = self.agv.get_modified_version()
        return f"{firmware_version}"

    def close(self):
        serial_port = getattr(self.agv, "_serial_port", None)
        if serial_port is not None:
            serial_port.close()
            
    def radar_high(self):
        GlobalVar.GPIO.setmode(GlobalVar.GPIO.BCM)
        time.sleep(0.1)
        GlobalVar.GPIO.setup(self.radar_pin, GlobalVar.GPIO.OUT)
        GlobalVar.GPIO.output(self.radar_pin, GlobalVar.GPIO.HIGH)

    def radar_low(self):
        GlobalVar.GPIO.setmode(GlobalVar.GPIO.BCM)
        time.sleep(0.1)
        GlobalVar.GPIO.setup(self.radar_pin, GlobalVar.GPIO.OUT)
        GlobalVar.GPIO.output(self.radar_pin, GlobalVar.GPIO.LOW)
        
    def init_pump(self):
        # init
        GlobalVar.GPIO.setmode(GlobalVar.GPIO.BCM)
        GlobalVar.GPIO.setup(self.suction_pump_pins[0], GlobalVar.GPIO.OUT)
        GlobalVar.GPIO.setup(self.suction_pump_pins[1], GlobalVar.GPIO.OUT)
    
    def turn_on_pump(self):
        # open
        GlobalVar.GPIO.output(self.suction_pump_pins[1], GlobalVar.GPIO.LOW)
        time.sleep(0.5)
        GlobalVar.GPIO.output(self.suction_pump_pins[0], GlobalVar.GPIO.HIGH)

    def turn_off_pump(self):
        # close
        GlobalVar.GPIO.output(self.suction_pump_pins[1], GlobalVar.GPIO.HIGH)
        GlobalVar.GPIO.output(self.suction_pump_pins[0], GlobalVar.GPIO.LOW)
        time.sleep(0.05)
        GlobalVar.GPIO.output(self.suction_pump_pins[0], GlobalVar.GPIO.HIGH)

    def radar_open(self):
        self.radar_high()
        roslaunch.roslaunch('myagv_odometry myagv_active.launch')

    def radar_close(self):
        self.radar_low()
        ShellAPI.kill("myagv_active.launch")

    @classmethod
    def check_radar_running(cls):
        return ShellAPI.alive("myagv_active.launch")

