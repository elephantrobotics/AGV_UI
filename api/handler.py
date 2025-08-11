#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses
import typing

import pymycobot
from pymycobot import MyAgv
from core.singleton import Singleton


@dataclasses.dataclass
class Velocity:
    x: float  # m/s
    y: float  # m/s
    z: float  # m/s


@dataclasses.dataclass
class EulerAngle:
    roll: float  # rad
    pitch: float  # rad
    yaw: float  # rad


@dataclasses.dataclass
class Battery:
    id: int
    voltage: float  # V
    plugged: bool  # True if plugged in
    LED: bool  # True if LED is on

    @property
    def percentage(self):
        if self.voltage <= 9:
            return 0.0

        return round((self.voltage - 9) / (12 - 9) * 100, 2)


@dataclasses.dataclass
class BatteryGroup:
    state: bool  # 电池状态
    adapter_access: bool  # 电源适配器
    charging_pile_access: bool  # 充电桩
    batteries: typing.List[Battery]

    @classmethod
    def create(cls, state: bool, adapter_access: bool, charging_pile_access: bool, batteries: typing.List[Battery]):
        return cls(
            state=state,
            adapter_access=adapter_access,
            charging_pile_access=charging_pile_access,
            batteries=batteries
        )


@dataclasses.dataclass
class Motor:
    id: int
    current: float  # A
    stall_state: bool  # True if blocked
    encoder_state: bool  # True if encoder is working


@dataclasses.dataclass
class MCUInfo:
    linear_velocity: Velocity  # 线速度
    acceleration: Velocity  # 加速度
    angular_velocity: Velocity  # 角速度

    # version 1.1
    mpu_state: bool  # 陀螺仪
    euler_angle: EulerAngle  # 欧拉角
    battery_groups: BatteryGroup  # 电池组
    motors: typing.List[Motor]  # 电机

    @classmethod
    def create(cls, data: typing.List):
        liner_velocity = Velocity(*data[0:3])
        acceleration = Velocity(*data[3:6])
        angular_velocity = Velocity(*data[6:9])

        battery_info = list(map(int, data[9]))
        battery_groups = BatteryGroup.create(
            state=battery_info[0] == 1,
            adapter_access=battery_info[2] == 1,
            charging_pile_access=battery_info[3] == 1,
            batteries=[
                Battery(
                    id=1,
                    voltage=data[10],
                    plugged=battery_info[1] == 1,
                    LED=battery_info[2] == 1
                ),
                Battery(
                    id=2,
                    voltage=data[11],
                    plugged=battery_info[0] == 1,
                    LED=battery_info[4] == 1
                )
            ]
        )

        motors = []
        motor_infos = (data[12:16], data[21:25], data[25:30])
        for motor_id, (current, stall, encoder) in enumerate(zip(*motor_infos), start=1):
            motor = Motor(
                id=motor_id,
                current=current,
                stall_state=stall == 1,
                encoder_state=encoder == 1
            )
            motors.append(motor)

        return cls(
            linear_velocity=liner_velocity,
            acceleration=acceleration,
            angular_velocity=angular_velocity,
            battery_groups=battery_groups,
            motors=motors,
            mpu_state=data[12],
            euler_angle=EulerAngle(*data[13:16])
        )


class AgvHandler(MyAgv, metaclass=Singleton):

    def __init__(self, port: str, baudrate: int, debug=False):
        super().__init__(comport=port, baudrate=baudrate, debug=debug)

    @property
    def is_opened(self):
        return self._serial_port.is_open

    def close(self):
        if self._serial_port.is_open is True:
            self._serial_port.close()

    def open(self):
        if self._serial_port.is_open is False:
            self._serial_port.open()

    def get_auto_report_message(self):
        mcu_info = self.get_mcu_info()
        if not mcu_info:
            return None

        print(f" # MCU INFO【{len(mcu_info)}】 {mcu_info}")
        return MCUInfo.create(mcu_info)


print(f" # setup AGV Handler with version {pymycobot.__version__}")
if __name__ == '__main__':
    agv_handler = AgvHandler('/dev/ttyAMA2', baudrate=115200, debug=True)
    a = agv_handler.get_auto_report_message()
    print(a)
