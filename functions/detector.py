#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time

from PyQt5.QtCore import pyqtSignal, QThread
from pymycobot import MyAgv


class MyAGVStatusDetector(QThread):
    voltages = pyqtSignal(float, float)
    battery = pyqtSignal(bool, bool)
    powers = pyqtSignal(float, float)
    motors = pyqtSignal(bool, list)

    def __init__(self, my_agv: MyAgv):
        super().__init__()
        self.agv_handler = my_agv
        self.detector = True

    def stop_detector(self):
        self.detector = False
        self.battery.emit(0, 0)
        self.voltages.emit(0, 0)
        self.powers.emit(0, 0)
        self.motors.emit(False, [0, 0, 0, 0])
        self.quit()

    @classmethod
    def calculate_amount_of_power(cls, voltage):
        """计算电池电量"""
        return round((voltage - 9) / (12 - 9) * 100, 2)

    def get_status_info(self):
        data = self.agv_handler.get_mcu_info()
        if not data:
            return

        # 电池状态 【电池2接入、电池1接入、适配器接入、充电桩接入、电池2充电灯， 电池1充电灯】
        battery_status = list(map(lambda n: int(n) == 1, data[9]))
        battery1 = battery_status[1]
        battery2 = battery_status[0]
        self.battery.emit(battery1, battery2)

        # 电机电流
        motors = data[12:16]
        # status = all(motor for motor in motors)
        self.motors.emit(bool(data), motors)

        battery_voltage_1 = data[10]  # 电池1电压
        battery_voltage_2 = data[11]  # 电池2电压

        battery_level_1 = 0.00  # 电池1电量
        battery_level_2 = 0.00  # 电池2电量
        if int(battery1) and battery_voltage_1:
            battery_level_1 = self.calculate_amount_of_power(battery_voltage_1)

        if int(battery2) and battery_voltage_2:
            battery_level_2 = self.calculate_amount_of_power(battery_voltage_1)

        self.voltages.emit(battery_voltage_1, battery_voltage_2)
        self.powers.emit(battery_level_1, battery_level_2)

    def run(self):
        while self.detector is True:
            try:
                self.get_status_info()
                time.sleep(1)
            except Exception as e:
                print(e)
