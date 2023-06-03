from enum import Enum
from pymycobot.mycobot import MyCobot
from R1Control.Common import *
import time


# MechArm270控制器
class MechArmController:
    class Joints(Enum):
        J1 = 0
        J2 = 1
        J3 = 2
        J4 = 3
        J5 = 4
        J6 = 5

    class Axis(Enum):
        X = 0
        Y = 1
        Z = 2
        RX = 3
        RY = 4
        RZ = 5

    def __init__(self, port: str, baud: int):
        self.ma = MyCobot(port, baud)

        # M5 吸泵引脚参数
        self.pump_pin2_m5 = 2
        self.pump_pin5_m5 = 5

    # 刷新模式
    def refresh_mode(self):
        self.ma.set_fresh_mode(1)

    # 插补模式
    def imputation_mode(self):
        self.ma.set_fresh_mode(0)
        
    # 检查关节是否合法
    def check_joints(self, joint):
        return joint in [j.value for j in self.Joints]

    # 获取当前角度
    def reacquire_get_angles(self):
        curr_angles = []
        while True:
            if not curr_angles:
                curr_angles = self.ma.get_angles()
            else:
                break
        return curr_angles
    
    # 获取当前坐标
    def reacquire_get_coords(self):
        curr_coords = []
        while True:
            if not curr_coords:
                curr_coords = self.ma.get_coords()
            else:
                break
        return curr_coords

    # 根据行为进行角度偏移（behavior：True -> 递增，False -> 递减）
    def angles_offset(self, joint, offset, b_behavior):
        curr_angles = []
        if self.check_joints(joint):
            curr_angles = self.reacquire_get_angles()
            if b_behavior:
                curr_angles[joint] += offset
            else:
                curr_angles[joint] -= offset
        return curr_angles

    # 递增角度
    def additional_offset(self, joint, offset):
        return self.angles_offset(joint, offset, True)

    # 递减角度
    def reduce_offset(self, joint, offset):
        return self.angles_offset(joint, offset, False)

    # 吸泵控制
    def pump_control(self, pin_signal):
        if pin_signal == 0 or pin_signal == 1:
            self.ma.set_basic_output(self.pump_pin2_m5, pin_signal)
            self.ma.set_basic_output(self.pump_pin5_m5, pin_signal)

    # 吸泵打开（M5）
    def pump_open(self):
        self.pump_control(0)

    # 吸泵关闭（M5）
    def pump_close(self):
        self.pump_control(1)

    # 夹爪控制
    def gripper_control(self, flag, speed):
        if flag == 0 or flag == 1:
            self.ma.set_gripper_state(flag, speed)

    # 夹爪张开
    def gripper_open(self, speed=default_gripper_speed):
        self.gripper_control(0, speed)

    # 夹爪合上
    def gripper_close(self, speed=default_gripper_speed):
        self.gripper_control(1, speed)

    # 夹爪范围设置
    def set_gripper_range(self, value, speed = default_gripper_speed):
        self.ma.set_gripper_value(value, speed)

    # 姿态向上调整
    def up(self, offset):
        curr_angles = self.reacquire_get_angles()
        curr_angles[self.Joints.J2.value] -= offset  # J2减少偏移量
        curr_angles[self.Joints.J3.value] -= offset * 2.0  # J3减少偏移量
        curr_angles[self.Joints.J5.value] += offset * 2.0  # J5增加偏移量
        return curr_angles
    
    # 姿态笛卡尔调整
    def spatial_adjustment(self, base, x_pattern, x_offset, y_pattern, y_offset, z_pattern, z_offset):
        coords = []
        if base is not None and len(base) == 6:
            coords = base
            if x_pattern == '+':
                coords[self.Axis.X.value] += x_offset
            elif x_pattern == '-':
                coords[self.Axis.X.value] -= x_offset

            if y_pattern == '+':
                coords[self.Axis.Y.value] += y_offset
            elif y_pattern == '-':
                coords[self.Axis.Y.value] -= y_offset

            if z_pattern == '+':
                coords[self.Axis.Z.value] += z_offset
            elif z_pattern == '-':
                coords[self.Axis.Z.value] -= z_offset
        new_coords = coords
        return new_coords

    # 放松关节根据行为获取角度、坐标信息（behavior：True -> 角度，False -> 坐标）
    def release_all_servos_and_get_values(self, behavior, num_iterations=1000, sleep_time=0.05):
        self.ma.release_all_servos()
        print_func = self.ma.get_angles if behavior else self.ma.get_coords
        print_type = "angles" if behavior else "coords"
        for i in range(num_iterations):
            print(f"{print_type}: {print_func()}")
            time.sleep(sleep_time)

    # 获取 DEBUG 角度信息
    def debug_get_angles_info(self, name):
        print_func = self.ma.get_angles
        print_type = "angles"
        name += " " + print_type
        print(f"{name}: {print_func()}")

    # 获取 DEBUG 坐标信息
    def debug_get_coords_info(self, name):
        print_func = self.ma.get_coords
        print_type = "coords"
        name += " " + print_type
        print(f"{name}: {print_func()}")
