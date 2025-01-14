#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from enum import Enum
import typing as T

from .utils import run_in_thread, get_localhost, gstreamer_pipeline
from .command import Command
from .translate import Translate


class Constant:
    SYSTEM_IDENTIFICATION_FILE = "/proc/device-tree/model"


class System(Enum):
    JETSON_NANO = 'NVIDIA Jetson Nano Developer Kit'
    RASPBERRYPI = "Raspberry Pi 4"

    def equal(self, model: str) -> bool:
        return model.startswith(self.value)


CURRENT_SYSTEM_MODEL = Command.cat(Constant.SYSTEM_IDENTIFICATION_FILE)

print(f" * ================================================")
print(f" * Current platform is {CURRENT_SYSTEM_MODEL}")
print(f" * ================================================")

if System.RASPBERRYPI.equal(CURRENT_SYSTEM_MODEL):
    import RPi.GPIO as GPIO

    class GlobalVar:
        comport = "/dev/ttyAMA2"
        baudrate = 115200
        suction_pump_pins = (2, 3)
        radar_control_pin = 20
        debug = False
        camera2D_pipline = 0
        camera3D_pipline = 0


elif System.JETSON_NANO.equal(CURRENT_SYSTEM_MODEL):
    import Jetson.GPIO as GPIO

    class GlobalVar:
        comport = "/dev/ttyS0"
        baudrate = 115200
        suction_pump_pins = (19, 26)    # 电磁阀引脚/电机引脚
        radar_control_pin = 20
        debug = False
        camera2D_pipline = gstreamer_pipeline(0)
        camera3D_pipline = 0

else:
    raise Exception(" * Current platform is not supported")


class GpioHandler:
    IN = GPIO.IN
    OUT = GPIO.OUT
    HIGH = GPIO.HIGH
    LOW = GPIO.LOW
    PWM = GPIO.PWM

    BCM = GPIO.BCM
    PUD_UP = GPIO.PUD_UP
    PUD_DOWN = GPIO.PUD_DOWN

    @classmethod
    def islow(cls, pin_number: int) -> bool:
        return cls.input(pin_number) == GPIO.LOW

    @classmethod
    def ishigh(cls, pin_number: int) -> bool:
        return cls.input(pin_number) == GPIO.HIGH

    @classmethod
    def setup(cls, channel: int, mode: int):
        GPIO.setup(channel, mode)

    @classmethod
    def setmode(cls, mode: int):
        GPIO.setmode(mode)

    @classmethod
    def input(cls, channel: int):
        return GPIO.input(channel)

    @classmethod
    def output(cls, channel: int, value: int):
        return GPIO.output(channel, value)

    @classmethod
    def event_detect(cls, channel: int, callback: T.Callable, bouncetime: int):
        GPIO.add_event_detect(channel, GPIO.BOTH, callback=callback, bouncetime=bouncetime)

    @classmethod
    def remove_event_detect(cls, channel: int):
        GPIO.remove_event_detect(channel)
        GPIO.cleanup(channel)

    @classmethod
    def gpio_function(cls, channel: int):
        return GPIO.gpio_function(channel)

    @classmethod
    def listening(cls, channel: int, callback: T.Callable, timeout: int, valid_signal: int = 0):
        def on_detect_callback(ori_channel):
            if cls.input(ori_channel) == valid_signal:
                callback()

        if System.JETSON_NANO.equal(CURRENT_SYSTEM_MODEL):
            GPIO.setup(channel, GPIO.IN)

        elif System.RASPBERRYPI.equal(CURRENT_SYSTEM_MODEL):
            GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_UP)

        GPIO.add_event_detect(channel, GPIO.BOTH, callback=on_detect_callback, bouncetime=timeout)

    @classmethod
    def cleanup(cls):
        GPIO.cleanup()


__all__ = [
    "run_in_thread",
    "get_localhost",
    "Constant",
    "GlobalVar",
    "Command",
    "GpioHandler",
    "System",
    "Translate"
]











































