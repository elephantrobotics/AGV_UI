#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import time
import traceback
import typing as T
import serial.serialutil
from PyQt5.QtCore import pyqtSignal, QThread, QObject
from core.handler import AgvHandler


@dataclasses.dataclass
class AGVBattery:
    status: T.Tuple[bool, bool] = (False, False)
    powers: T.Tuple[float, float] = (0.0, 0.0)
    voltages: T.Tuple[float, float] = (0.0, 0.0)


@dataclasses.dataclass
class AGVMotor:
    state: bool = False
    currents: T.List[float] = dataclasses.field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])
    stall_states: T.List[int] = dataclasses.field(default_factory=lambda: [0, 0, 0, 0])
    encoder_states: T.List[int] = dataclasses.field(default_factory=lambda: [0, 0, 0, 0])


class MyAGVStatusDetector(QThread):
    battery_stated = pyqtSignal(AGVBattery)
    motor_stated = pyqtSignal(AGVMotor)
    versioned = pyqtSignal(str)

    def __init__(self, agv_handler: AgvHandler, interval: float = 10, parent: QObject = None):
        super().__init__(parent=parent)
        self.__agv_handler = agv_handler
        self.__detector = True
        self.__interval = interval

    def stop_detector(self):
        self.__detector = False
        self.motor_stated.emit(AGVMotor())
        self.battery_stated.emit(AGVBattery())
        self.quit()

    @classmethod
    def calculate_amount_of_power(cls, voltage):
        """计算电池电量"""
        return round((voltage - 9) / (12 - 9) * 100, 2)

    def _get_status_info(self):
        data = self.__agv_handler.get_mcu_info()
        if not data:
            return

        # 电机电流
        currents = data[12:16]
        self.motor_stated.emit(
            AGVMotor(
                state=any(map(lambda c: c != 0, currents)),
                currents=currents,
                stall_states=data[20:24],
                encoder_states=data[24:28]
            ),
        )

        # 电池状态 【电池2接入、电池1接入、适配器接入、充电桩接入、电池2充电灯， 电池1充电灯】
        # main_battery_state, backup_battery_state, *_ = tuple(map(lambda n: int(n) == 1, data[9]))
        main_battery_state = data[9][1] == '1'
        backup_battery_state = data[9][0] == '1'
        main_battery_voltage = data[10]  # 主电池电压
        sub_battery_voltage = data[11]  # 副电池电压

        main_battery_coulomb = 0.00  # 主电池电量
        sub_battery_coulomb = 0.00  # 副电池电量
        if main_battery_state and main_battery_voltage:
            main_battery_coulomb = self.calculate_amount_of_power(main_battery_voltage)

        if backup_battery_state and sub_battery_voltage:
            sub_battery_coulomb = self.calculate_amount_of_power(sub_battery_voltage)

        self.battery_stated.emit(
            AGVBattery(
                status=(main_battery_state, backup_battery_state),
                voltages=(main_battery_voltage, sub_battery_voltage),
                powers=(main_battery_coulomb, sub_battery_coulomb)
            )
        )

    def run(self):
        while self.__detector is True:
            try:
                self._get_status_info()
                version = self.__agv_handler.get_firmware_version()
                if version:
                    self.versioned.emit(str(version))
            except serial.serialutil.SerialException:
                pass
            except Exception as e:
                print(f"@MyAGVStatusDetector::run exception: {e}")
            finally:
                time.sleep(self.__interval)
