#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import traceback
from PyQt5.QtCore import QThread, pyqtSignal
from core.translate import Translate
from core.handler import AgvHandler
from . import Functional


class FunctionalBaseTesting(QThread):
    finished = pyqtSignal(str, bool)
    processed = pyqtSignal(dict)

    def __init__(self, agv: AgvHandler, test_name: str, parent=None):
        super().__init__(parent=parent)
        self.test_name = test_name
        self.agv = agv

    def emit_process(self, **kwargs):
        self.processed.emit({"test_name": self.test_name, **kwargs})

    def do_testing(self):
        raise NotImplementedError

    def run(self):
        try:
            self.do_testing()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        finally:
            self.finished.emit(self.test_name, False)


class AGVLEDTesting(FunctionalBaseTesting):

    @staticmethod
    def get_colors():
        return {
            Translate.Color.Red: (255, 0, 0),
            Translate.Color.Orange: (255, 128, 0),
            Translate.Color.Yellow: (255, 255, 0),
            Translate.Color.Green: (0, 255, 0),
            # Translate.Color.Cyan: (0, 255, 255),
            Translate.Color.Blue: (0, 0, 255),
            Translate.Color.Purple: (128, 0, 255)
        }

    def do_testing(self):
        # #####################################################
        self.agv.set_led_mode(1)  # 适配1.0版本, 1.1之后可删除
        self.agv.stop()
        # #####################################################
        for name, color in self.get_colors().items():
            self.emit_process(name=name, color=color)
            self.agv.set_led(1, *color)
            time.sleep(1)


class AGVPUMPTesting(FunctionalBaseTesting):

    def do_testing(self):
        # GPIO = GlobalVar.GPIO
        # GPIO.setmode(GPIO.BCM)
        # GPIO.setup(GlobalVar.suction_pump_pins[0], GPIO.OUT)
        # GPIO.setup(GlobalVar.suction_pump_pins[1], GPIO.OUT)
        Functional.init_pump()

        # open
        self.emit_process(behavior=Translate.State.Open)
        # GPIO.output(GlobalVar.suction_pump_pins[1], GPIO.LOW)
        # GPIO.output(GlobalVar.suction_pump_pins[0], GPIO.HIGH)
        Functional.turn_on_pump()
        time.sleep(4)

        # close
        self.emit_process(behavior=Translate.State.Close)
        # GPIO.output(GlobalVar.suction_pump_pins[1], GPIO.HIGH)
        # GPIO.output(GlobalVar.suction_pump_pins[0], GPIO.LOW)
        # time.sleep(0.05)
        # GPIO.output(GlobalVar.suction_pump_pins[0], GPIO.HIGH)
        # GPIO.cleanup()
        Functional.turn_off_pump()


class AGVMotorTesting(FunctionalBaseTesting):

    def __init__(self, agv: AgvHandler, test_name: str, parent=None):
        super().__init__(agv, test_name, parent)
        self.direction_movement_table = {
            Translate.Direction.GoAhead: lambda: self.agv.go_ahead(100, 4),
            Translate.Direction.Retreat: lambda: self.agv.retreat(100, 4),
            Translate.Direction.PanLeft: lambda: self.agv.pan_left(100, 4),
            Translate.Direction.PanRight: lambda: self.agv.pan_right(100, 4),
            Translate.Direction.CRotation: lambda: self.agv.clockwise_rotation(100, 8),
            Translate.Direction.CCRotation: lambda: self.agv.counterclockwise_rotation(100, 8),
        }

    def do_testing(self):
        for direction, movement in self.direction_movement_table.items():
            self.emit_process(direction=direction)
            movement()
            time.sleep(1)
            self.agv.stop()
            time.sleep(1)
        self.agv.stop()
