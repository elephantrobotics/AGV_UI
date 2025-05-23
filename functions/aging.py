#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import time
import enum
from core.handler import AgvHandler
from PyQt5.QtCore import QThread, pyqtSignal


@enum.unique
class AgingStateFlag(enum.Flag):  # 老化状态
    STARTUP = enum.auto()  # 启动
    RUNNING = enum.auto()  # 运行
    STOPPED = enum.auto()  # 停止
    FINISHED = enum.auto()  # 完成


@enum.unique
class AgingDirectionFlag(enum.Flag):  # 运动方向
    FORWARD = enum.auto()  # 前进
    BACKWARD = enum.auto()  # 后退
    PAN_LEFT = enum.auto()  # 左转
    PAN_RIGHT = enum.auto()  # 右转
    STOP = enum.auto()  # 停止
    CLOCKWISE_ROTATION = enum.auto()  # 顺时针旋转
    COUNTERCLOCKWISE_ROTATION = enum.auto()  # 逆时针旋转


@dataclasses.dataclass
class AgingState:
    speed: int  # 老化速度
    duration: int  # 单次老化时长
    timeout: int  # 总老化时长
    progress: float
    direction_flag: AgingDirectionFlag  # 老化运动方向
    state_flag: AgingStateFlag  # 老化状态 完成、停止


class AgvMotorPersistentAging(QThread):
    noticed = pyqtSignal(AgingState)
    finished = pyqtSignal(bool)
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
        self.continued = False

    def stopped(self):
        self.agv_handler.stop()
        self.continued = False

    def motor_movement_testing(self):
        cumulative_duration = 0
        total_duration = sum(self.speed_timeout_mapping.values()) * len(self.agv_direction_function_table)
        for direction, aging_handle in self.agv_direction_function_table.items():

            self.notify(direction=direction, state=AgingStateFlag.STARTUP)
            for speed, duration in self.speed_timeout_mapping.items():
                self.notify(
                    direction=direction,
                    state=AgingStateFlag.RUNNING,
                    speed=speed,
                    duration=duration,
                    progress=round(cumulative_duration / total_duration * 100, 2)
                )
                aging_handle(self.agv_handler, speed=speed, timeout=duration)
                if self.continued is False:
                    self.notify(direction=direction, state=AgingStateFlag.STOPPED)
                    return False
                cumulative_duration += duration
            else:
                self.notify(direction=direction, state=AgingStateFlag.FINISHED)
            time.sleep(2)
        return True

    def notify(
            self,
            direction: AgingDirectionFlag,
            state: AgingStateFlag,
            speed: int = 0,
            duration: int = 0,
            progress: float = 0.0
    ):
        aging_state = AgingState(
            direction_flag=direction,
            state_flag=state,
            speed=speed,
            timeout=self.timeout,
            duration=duration,
            progress=progress
        )
        self.noticed.emit(aging_state)

    def run(self):
        self.continued = True
        self.agv_handler.stop()
        aging_state = self.motor_movement_testing()
        self.agv_handler.stop()
        self.finished.emit(aging_state)
