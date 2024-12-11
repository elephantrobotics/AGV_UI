#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import threading
import time
import traceback

from PyQt5.QtCore import QThread, pyqtSignal
from pymycobot import MyAgv


class AGVStateEnum:  # 老化状态
    STARTUP = 0  # 启动
    RUNNING = 1  # 运行
    FINISHED = 2  # 完成


class AGVDirectionEnum:  # 运动方向
    FORWARD = 0  # 前进
    BACKWARD = 1  # 后退
    PAN_LEFT = 2  # 左转
    PAN_RIGHT = 3  # 右转
    STOP = 4  # 停止
    CLOCKWISE_ROTATION = 5  # 顺时针旋转
    COUNTERCLOCKWISE_ROTATION = 6  # 逆时针旋转


class AgvMotorAging(QThread):
    """
    电机老化测试线程
    """
    aging_finished = pyqtSignal(str, list)  # 老化完成
    aging_noticed = pyqtSignal(int, int, int)  # 运动方向
    motion_checked = pyqtSignal(bool)  # 运动检测

    speed_timeout_mapping = {10: 240, 50: 180, 127: 180}

    def __init__(self, agv: MyAgv, parent=None, speed: int = 10, timeout=600):
        super().__init__(parent=parent)
        self.agv = agv
        self.speed = speed
        self.timeout = timeout
        self.aging_event = threading.Event()
        self.next_tick_running = False
        self.agv_direction_function_table = {
            AGVDirectionEnum.FORWARD: self.agv.go_ahead,
            AGVDirectionEnum.BACKWARD: self.agv.retreat,
            AGVDirectionEnum.PAN_LEFT: self.agv.pan_left,
            AGVDirectionEnum.PAN_RIGHT: self.agv.pan_right,
            AGVDirectionEnum.CLOCKWISE_ROTATION: self.agv.clockwise_rotation,
            AGVDirectionEnum.COUNTERCLOCKWISE_ROTATION: self.agv.counterclockwise_rotation
        }

    def next(self, running: bool):
        self.aging_event.set()
        self.next_tick_running = running

    def aging_notification(self, direction: int, state: int, timeout: int):
        self.aging_noticed.emit(direction, state, timeout)

    def motor_movement_testing(self, timeout, is_aging: bool = False):
        for direction, function in self.agv_direction_function_table.items():

            if is_aging is True:
                for speed, timeout in self.speed_timeout_mapping.items():
                    self.aging(function, direction, timeout, speed)
            else:
                self.aging(function, direction, timeout, self.speed)
            time.sleep(2)

    def aging(self, func, direction, timeout, speed):
        self.aging_notification(direction, AGVStateEnum.STARTUP, timeout=timeout)
        func(speed=speed, timeout=timeout)
        self.aging_notification(direction, AGVStateEnum.FINISHED, timeout=timeout)

    def get_battery_info(self):
        info = None
        while info is None:
            try:
                info = self.agv.get_battery_info()
            except Exception as e:
                info = None
                print(e)
            time.sleep(0.3)
        return info

    def run(self):
        difference = []
        try:
            self.agv.stop()
            self.motor_movement_testing(timeout=5)
            self.aging_finished.emit("break", difference)

            self.aging_event.wait()

            if self.next_tick_running is True:
                _, *before_aging_vol = self.get_battery_info()
                self.motor_movement_testing(timeout=self.timeout, is_aging=True)
                _, *after_aging_vol = self.get_battery_info()
                difference = [abs(after - before) for after, before in zip(after_aging_vol, before_aging_vol)]
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        finally:
            self.aging_finished.emit("finish", difference)
