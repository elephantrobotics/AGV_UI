from R1Control.MechArmController import MechArmController
from R1Control.TcpClient import TcpClient
from R1Control.Common import *
import numpy as np
import time
import logging


class RobotR1(MechArmController):

    def status_check(self):
        # 检查270是否已上电，未上电则上电
        if not self.ma.is_power_on():
            self.ma.power_on()
            time.sleep(1)

        # 设置插补模式
        self.imputation_mode()
        time.sleep(1)

        # 夹爪合上
        self.gripper_close()
        time.sleep(1)

        # 根据夹爪实际直径比例设置当前工具坐标系范围
        #self.ma.set_tool_reference([0, 0, flexible_jaw_diameter, 0, 0, 0])
        time.sleep(1)

        # 设置末端工具类型
        self.ma.set_end_type(1)
        time.sleep(1)

    def move_start(self, speed, delay):
        # 移动到初始姿态
        self.ma.send_angles(self.robot_restore_point1, speed)
        time.sleep(delay)

    def  move_end(self,speed,delay):
        self.ma.send_angles(self.robot_restore_point1,speed)
        time.sleep(delay)

    def robot_gripper_open(self):
        # 夹爪合上
        self.set_gripper_range(40, 70)
        time.sleep(1)

    def robot_check(self):
        
        self.status_check()
        self.move_start(default_speed, 3)

    def __init__(
        self
    ):
        super().__init__()
        self.recheck_times = 0  # 重新检测摘取的次数
        self.old_camera_coord_list = []  # 上一次相机实时坐标列表

        self.robot_initial_pose    = [27.59, -15.38, -6.59, 0.0, 75.14, 0]  # 机械臂初始姿态角
        self.robot_restore_point1  = [0, -15.29, 15.9, 0, 75.05, 0]  # 机械臂初始恢复角1
        self.robot_restore_point2  = [-90, -15.29, 15.9, 0, 75.05, 0]   # 机械臂初始恢复角2
        # self.robot_precatch_pose =[-87.27, -22.06, 31.11, 88.85, 92.98, -91.49] # 机械臂抓取前初始预姿态角
        self.robot_precatch_pose =[-87.53, 27.24, 7.99, 89.2, 92.9, -133] # 机械臂抓取前初始预姿态角
        self.robot_end_point = [-87.53, -14.41, 16.61, 0.17, 74.7, 0.26] #机械臂结束点位
        self.AGV_waiting_point = [89.82, -14.41, 16.61, 0.17, 74.7, 0.26]       # 机械臂预放置角
        # 机械臂不同放置区域角
        self.AGV_entry_areas = [
            [87.71, 36.12, -26.27, 0.26, 79.54, 0.17],
            [109.07, 38.32, -26.27, 0.26, 75.23, 1.05],
            [101.42, 52.38, -53.26, 0.26, 65.83,-0.17],
            [89.45, 54.84, -52.47,0.17, 66.02, 0.17],
        ]
        self.camera_coord = np.array([0.0, 0.0, 0.0])  # 相机到目标的实时坐标点
        # self.camera_pos = np.array([-100.8, -110.7, 165.5]) # 相机到目标的固定坐标点
        self.camera_pos = np.array([-98.6, -110.9, 185.3])
        # self.camera_pos = np.array([-99.6, -134.5, 185.6])
        self.end_coords   = np.array([0.0, 0.0, 0.0])          # 根据相机坐标转换后的实际世界坐标点
        self.i = -1                  # 控制果子放置区域
        
        if self.ma:
            self.robot_check()
        else:
            print("in r r1 no ")
            pass

    # 获取真实相机世界坐标x, y, z
    def get_camera_coord(self):
        return self.camera_coord
    
    # 设置真实相机世界坐标x, y, z
    def set_camera_coord(self, x: float, y: float, z: float):
        self.camera_coord = np.array([x, y, z])


    # 获取转换后机械臂可以运动的世界坐标
    def get_end_coords(self):
        return self.end_coords

    
    # 辅助计算机械臂可移动坐标
    def model_track(self):
        target_pos = []
        if(self.camera_coord[2] > 400):
            self.camera_coord[2] = 340
        model_pos = np.array(
            [self.camera_coord[2], self.camera_coord[0], -self.camera_coord[1]]
        )
        target_pos = model_pos + self.camera_pos

        if DEBUG == True:
            #print("model_pos: ", model_pos)
            print("target_pos: ", target_pos)
        return target_pos

    #根据相机真实坐标计算机械臂实际可移动世界坐标
    def target_coords(self):
        coord = self.ma.get_coords()
        while len(coord) == 0:
            coord = self.ma.get_coords()

        target = self.model_track()
        coord[:3] = target.copy()
        self.end_coords = coord[:3]

        if DEBUG == True:
            pass
            #print("coord: ", coord)
            #print("self.end_coords: ", self.end_coords)

        # 更新实际转换的世界坐标系
        self.end_coords = coord

        return coord

    # 摘取前位置调整，避免档到3D摄像头
    def restore_postion_action(self, speed, delay):
        self.ma.send_angles(self.robot_restore_point1, speed)
        time.sleep(delay)
        self.ma.send_angles(self.robot_restore_point2, speed)
        time.sleep(delay)

    # 摘取前姿态预调整
    def pickup_attitude_adjustment_action(self, speed, delay):
        self.ma.send_angles(self.robot_precatch_pose, speed)
        time.sleep(delay)

    # 摘取等待点坐标
    def waiting_point_action(self, waiting_coords, x_pattern, x, y_pattern, y, z_pattern, z, speed):
        new_coords = self.spatial_adjustment(waiting_coords, x_pattern, x, y_pattern, y, z_pattern, z)

        self.ma.clear_error_information()
        time.sleep(0.5)
        self.ma.send_coords(new_coords, speed)
        time.sleep(2)
        err = self.ma.get_error_information()
        while (err != 0):
            self.ma.send_coords(new_coords, speed)
            time.sleep(2)
            err = self.ma.get_error_information()


        a_waiting_point = self.reacquire_get_angles()
        time.sleep(2)
        a_waiting_point[self.Joints.J6.value] += 90

        self.ma.send_angle(6, a_waiting_point[self.Joints.J6.value], 100)
        time.sleep(2.0)

        self.set_gripper_range(35,70)
        time.sleep(0.2)

        # gripper_value = self.ma.get_gripper_value()
        # time.sleep(2)
        # while gripper_value <= 30 or 40 <= gripper_value:
        #     self.set_gripper_vlue(40,70)
        #     time.sleep(5)
        #     gripper_value = self.ma.get_gripper_value()
        return new_coords
        #return self.reacquire_get_coords()

    # 摘取实际点动作
    def pickup_point_action(self, entry_coords, x_pattern, x, y_pattern, y, z_pattern, z, speed):
        self.ma.send_coords(self.spatial_adjustment(entry_coords, x_pattern, x, y_pattern, y, z_pattern, z), speed, 1)
        time.sleep(4)

        # 关闭夹爪摘取果子
        self.set_gripper_range(0, 70)
        time.sleep(1)
        # gripper_value = self.ma.get_gripper_value()
        # time.sleep(5)
        # while gripper_value <= 0 or 10 <= gripper_value:
        #     self.set_gripper_vlue(0, 70)
        #     time.sleep(2)
        #     gripper_value = self.ma.get_gripper_value()
        # 摘取完果子临时插补点，防止撞到没摘的果子
        self.ma.send_coords(self.spatial_adjustment(self.reacquire_get_coords(), '-', 30.0, '-', 0, '-', 0), 70)
        time.sleep(1)

        self.ma.send_angles(self.robot_restore_point2,50)
        time.sleep(1)

    # 将果子运输至AGV上方
    def transport_to_AGV_point_action(self, speed, delay, i):
        self.ma.send_angles(self.robot_restore_point2,speed)
        time.sleep(delay)

        self.ma.send_angles(self.robot_restore_point1,speed)
        time.sleep(delay)

        # 移动到AGV上方轨迹前等待点（防止撞到3D摄像头）
        self.ma.send_angles(self.AGV_waiting_point, speed)
        time.sleep(delay)
        
        # 移动到AGV不同区域
        self.ma.send_angles(self.AGV_entry_areas[i], speed)
        time.sleep(delay)

    # 放置果子动作
    def placement_action(self, speed, delay):
        # 张开夹爪放置果子
        self.set_gripper_range(40,70)
        time.sleep(1)
        # gripper_value = self.ma.get_gripper_value()
        # time.sleep(2)
        # while gripper_value <= 35 or 45 <= gripper_value:
        #     self.set_gripper_vlue(40, 70)
        #     time.sleep(5)
        #     gripper_value = self.ma.get_gripper_value()
        # 上调至传送带轨迹
        self.ma.send_angles(self.AGV_waiting_point, speed)
        time.sleep(delay)

        self.gripper_close()
        time.sleep(delay)

    # 摘取果子轨迹规划
    def trajectory_plan(self, speed, delay):
        flag = False
        for camera_coord in self.old_camera_coord_list:
            if camera_coord is not None:
                logging.info(f"Performing motion for camera coord: {camera_coord}")

                if len(camera_coord) == 3:
                    self.set_camera_coord(camera_coord[0], camera_coord[1], camera_coord[2])

                    # 摘取姿态调整，绕过摄像头
                    self.restore_postion_action(speed, delay)

                    # 摘取前姿态预调整
                    self.pickup_attitude_adjustment_action(speed, delay)
                    
                    # 计算世界坐标
                    self.target_coords()
                    c_waiting_point = self.get_end_coords()
                    logging.info(f"Waiting coords: {c_waiting_point}")
                    print("waiting")
                    # self.ma.send_coords(c_waiting_point, 20)
                    # time.sleep(1)
                    #
                    # 摘取等待点动作
                    # c_entry_point = self.waiting_point_action(c_waiting_point, '-', 30.0, '-',10, '-', 5, 70)
                    c_entry_point = self.waiting_point_action(c_waiting_point, '-', 66.0+90, '-', 11, '+', 20, 90)
                    logging.info(f"Entry coords: {c_entry_point}")
                    print("picking")

                    # self.ma.send_coords(c_waiting_point,30)
                    time.sleep(2)
                    # # 摘取实际点动作
                    # self.pickup_point_action(c_entry_point, '+', 61.0, '+',0, '+', 0, 40)
                    self.ma.send_coord(1, c_entry_point[0] + 61, 90)
                    time.sleep(3)
                    self.set_gripper_range(0, 70)
                    time.sleep(2)
                    self.ma.send_coord(1, c_entry_point[0] - 61, 90)
                    time.sleep(2)
                    # if self.i == 4:
                    #     self.i = 0
                    # else:
                    self.i += 1
                    with open("log.txt","a") as f:
                        f.write("motion:"+str(self.i))
                    # 传送带轨迹规划动作
                    self.transport_to_AGV_point_action(speed, delay,self.i)

                    #
                    # # 放置果子动作
                    self.placement_action(speed, delay)
                    c_waiting_point = []
                    c_entry_point = []
                    flag = True
        return flag


    def motion(self, cap_thread, speed=default_speed, delay=default_delay):
        # 超过100次没检测到好果则设置摘取坏果范围
        #if self.recheck_times > 4:
        #    if cap_thread.is_apple() == True:
        #        cap_thread.set_detect_orange()
        #    else:
        #        cap_thread.set_detect_apple()
        #    self.recheck_times = 0

        # 没果子机械臂则回原点
        camera_coord_list = cap_thread.get_camera_coord_list()
        self.old_camera_coord_list = camera_coord_list
        camera_coord_list_len = len(self.old_camera_coord_list)

        finish = False
        if camera_coord_list_len <= 0:
            #self.move_start(speed, delay)
            self.move_end(speed, delay)
            self.recheck_times += 1
            return finish
        try:
            finish = self.trajectory_plan(speed, delay)
        except Exception as e:
            logging.error(f"Failed to execute motion: {e}")

        return finish

