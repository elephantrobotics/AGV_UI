#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
from core.handler import AgvHandler
from PyQt5.QtCore import QThread, pyqtSignal


class AgingStateFlag:  # 老化状态
    STARTUP = 0  # 启动
    RUNNING = 1  # 运行
    FINISHED = 2  # 完成


class AgingDirectionFlag:  # 运动方向
    FORWARD = 0  # 前进
    BACKWARD = 1  # 后退
    PAN_LEFT = 2  # 左转
    PAN_RIGHT = 3  # 右转
    STOP = 4  # 停止
    CLOCKWISE_ROTATION = 5  # 顺时针旋转
    COUNTERCLOCKWISE_ROTATION = 6  # 逆时针旋转


class AgvMotorPersistentAging(QThread):
    noticed = pyqtSignal(int, int, int)

    speed_timeout_mapping = {
        10: 240,
        50: 180,
        127: 180
    }

    agv_direction_function_table = {
        AgingDirectionFlag.FORWARD: AgvHandler.go_ahead,
        AgingDirectionFlag.BACKWARD: AgvHandler.retreat,
        AgingDirectionFlag.PAN_LEFT: AgvHandler.pan_left,
        AgingDirectionFlag.PAN_RIGHT: AgvHandler.pan_right,
        AgingDirectionFlag.CLOCKWISE_ROTATION: AgvHandler.clockwise_rotation,
        AgingDirectionFlag.COUNTERCLOCKWISE_ROTATION: AgvHandler.counterclockwise_rotation
    }

    def __init__(self, speed: int = 10, timeout=600, parent=None):
        super().__init__(parent=parent)
        self.agv_handler = AgvHandler.get_instance()
        self.speed = speed
        self.timeout = timeout

    def motor_movement_testing(self):
        for direction, function in self.agv_direction_function_table.items():
            for speed, timeout in self.speed_timeout_mapping.items():
                self.aging(function, direction, timeout, speed)
            time.sleep(2)

    def aging(self, move_handle, direction, timeout, speed):
        self.noticed.emit(direction, AgingStateFlag.STARTUP, timeout)
        move_handle(self.agv_handler, speed=speed, timeout=timeout)
        self.noticed.emit(direction, AgingStateFlag.FINISHED, timeout)

    def run(self):
        self.agv_handler.stop()
        self.motor_movement_testing()
        self.agv_handler.stop()
