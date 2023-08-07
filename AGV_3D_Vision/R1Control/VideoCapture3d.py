from ObTypes import *
from Property import *
from Error import ObException
from collections import namedtuple
from CvDetection.VideoStreamPipe import VideoStreamPipe
from CvDetection.detection import color_detect, circle_detect, Detector
from CvDetection.utli import *
from R1Control.Common import *
from openni import _openni2 as c_api
import numpy as np
import Pipeline
import cv2
import threading
import sys
import time
import Pipeline

class VideoCaptureThread(threading.Thread):
    def __init__(self, detector, detect_type = Detector.FetchType.FETCH_ALL.value):
        threading.Thread.__init__(self)
        self.vp = VideoStreamPipe()               # 3D摄像头视觉流管道
        self.detector = detector                  # 果子检测机
        self.finished = True                      # 中断标记
        self.camera_coord_list = []               # 相机坐标（转换后世界坐标，非像素坐标）
        self.old_real_coord_list = []             # 像素坐标 -> 相机世界坐标（拷贝）
        self.real_coord_list = []                 # 像素坐标 -> 相机世界坐标
        self.new_color_frame = None               # RGB帧
        self.fruit_type = detector.detect_target  # 水果类型
        self.detect_type = detect_type            # 摘取类型
        self.depth_show = None
        self.rgb_show = None

    # 设置中断标记
    def get_finished_flag(self):
        return self.finished
    
    # 获取中断标记
    def set_finished_flag(self, flag):
        self.finished = flag
    
    # 已中断
    def is_finished(self):
        return self.get_finished_flag() == True

    # 未中断
    def not_finished(self):
        return self.get_finished_flag() == False
    

    # 获取以相机为中心的世界坐标
    def get_camera_coord_list(self):
        return self.camera_coord_list
    

    # 获取水果类型
    def get_fruit_type(self):
        return self.fruit_type


    # 获取摘取类型
    def get_detect_type(self):
        return self.detect_type
    
    # 设置摘取类型
    def set_detect_type(self, type):
        self.detect_type = type

    
    # 设置摘取一个模式
    def set_fetch_one_mode(self):
        self.set_detect_type(Detector.FetchType.FETCH.value)

    # 设置摘取全部模式
    def set_fetch_all_mode(self):
        self.set_detect_type(Detector.FetchType.FETCH_ALL.value)


    # 设置检测目标为苹果
    def set_detect_apple(self):
        self.detector.set_target("apple")

    # 设置检测目标为橙子
    def set_detect_orange(self):
        self.detector.set_target("orange")

    # 设置检测目标为雪梨
    def set_detect_pear(self):
        self.detector.set_target("pear")


    # 检测水果类型
    def detect_fruit_type(self, fruit_name):
        if self.get_fruit_type() == fruit_name:
            return True
        return False
    
    # 检测水果类型是否为苹果
    def is_apple(self):
        return self.detect_fruit_type("apple")
    
    # 检测水果类型是否为橙子
    def is_orange(self):
        return self.detect_fruit_type("orange")
    
    # 检测水果类型是否为雪梨
    def is_pear(self):
        return self.detect_fruit_type("pear")


    # 创建一对namedtuple匿名对象
    def make_pair(self, lhs_name, lhs_value, rhs_name, rhs_value):
        pair = namedtuple('pair', [lhs_name, rhs_name])
        new_pair = pair(lhs_value, rhs_value)
        return new_pair


    # 像素坐标x、y解包成列表
    def unpack_xy_to_list(self, infos):
        data_list = []

        # 只要存在二维相机坐标
        if infos is not None:
            if DEBUG == True:
                print("infos: ", infos)

            # 遍历所有检测到的二维相机坐标
            for fruit_info in infos:
                # 每次都需要清空一次
                coord_pair = None

                # 非空则取出一条二维相机坐标信息打印
                if fruit_info is not None:
                    if DEBUG == True:
                        print("fruit_info: ", fruit_info)

                    # 截取前两位x、y
                    coord = [list(fruit_info.values())[:2]][0]
                    if DEBUG == True:
                        print("coord: ", coord)

                    # 截取到位，则创建一个匿名pair
                    if len(coord) == 2:
                        coord_pair = self.make_pair("x", coord[0], "y", coord[1])
                    if DEBUG == True:
                        print("X: ", coord_pair.x)
                        print("Y: ", coord_pair.y)

                # 匿名对象非空则将数据加入到列表
                if coord_pair is not None:
                    data_list.append(coord_pair.x)
                    data_list.append(coord_pair.y)

        # 返回解包后的x、y列表
        return data_list


    # 获取新彩色、新深度帧（[0]->新彩色帧，[1]->新深度帧）
    def get_depth_frame(self, frame):
        # new_color_data = None  # src: Mat
        # new_depth_data = []
        data_list = []

        color_frame = frame.colorFrame()  # 获取彩色帧
        depth_frame = frame.depthFrame()  # 获取深度帧

        # 彩色、深度帧非空满足
        if color_frame != None and depth_frame != None:
            color_size = color_frame.dataSize()  # 彩色帧大小
            color_data = color_frame.data()      # 彩色帧数据

            depth_size = depth_frame.dataSize()  # 深度帧大小
            depth_data = depth_frame.data()      # 深度帧数据

            color_width = color_frame.width()    # 彩色帧宽度
            color_height = color_frame.height()  # 彩色帧高度

            depth_width = depth_frame.width()    # 深度帧宽度
            depth_height = depth_frame.height()  # 深度帧高度

            # 彩色帧、深度帧非空满足
            if color_size != 0 and depth_size != 0:
                # 色彩识别
                new_color_data = color_data
                new_color_data.resize((color_height, color_width, 3))
                data_list.append(new_color_data)

                # 帧数据BGR转RGB
                self.new_color_frame = cv2.cvtColor(new_color_data, cv2.COLOR_BGR2RGB)

                # 深度识别帧数据大小调整(height, width, 2)
                depth_data = np.resize(depth_data, (depth_height, depth_width, 2))
                # if color_height != depth_height:
                #     filled_height = np.zeros((40, color_width, 2))
                #     filled_width = np.zeros((color_height, 30, 2))
                #     depth_data = np.vstack([filled_height, depth_data, filled_height])
                #     depth_data = np.hstack([filled_width, depth_data])

                # 深度帧数据8bit转16bit
                new_depth_data = depth_data[:, :, 0] + depth_data[:, :, 1] * 256
                new_depth_data = cv2.flip(new_depth_data, 1)
                data_list.append(new_depth_data)

        # 返回新彩色、新深度帧
        return data_list


    # 深度信息转世界坐标信息（适用于摘取 FetchAll 类型）
    def convert_depth_to_world(self, x, y, z):
        fx = 454.367
        fy = 454.367
        cx = 313.847
        cy = 239.89

        ratio = float(z / 1000)

        world_x = float((x - cx) * ratio) / fx
        world_x = world_x * 1000

        world_y = float((y - cy) * ratio) / fy
        world_y = world_y * 1000

        world_z = float(z)
        
        return world_x, world_y, world_z
    

    # x、y信息转世界坐标信息（适用于摘取 Fetch 类型）
    def xy_to_world(self, cx, cy, frame):
        x, y = cx, cy
        z = frame[int((y-40)/2),int((x-40)/2)]
        if DEBUG == True:
            print("pixel coord X, Y, Z: ", (x, y, z))

        x, y, z = self.convert_depth_to_world(x, y, z)
        real_data = (x, y, z)
        
        # 无效数据去重
        # if any(val == 0 or val == -0.0 for val in real_data):
        if 0 in [x, y, z] or -0 in [x, y, z]:
            real_data = None

        if DEBUG == True:
            print("real coord X, Y, Z: ", real_data)

        # 返回真实的世界x、y、z信息
        return real_data
    

    # 获取摘取信息列表
    def get_fruit_info(self):
        fruit_info_list = []

        # 根据摘取全部类型摘取全部果子
        if self.get_detect_type() == Detector.FetchType.FETCH_ALL.value:
            # 从检测机当中进行全部摘取
            fetch_all = self.detector.fetch_all()
            # 非空满足
            if fetch_all is not None:
                # 直接将列表覆盖
                fruit_info_list = fetch_all

        # 根据摘取一个类型摘取一个果子
        elif self.get_detect_type() == Detector.FetchType.FETCH.value:
            # 从检测机当中进行单个摘取
            fetch = self.detector.fetch()
            # 非空满足
            if fetch is not None:
                # 依个附加到列表
                fruit_info_list.append(fetch)

        if DEBUG == True:
            print("get_fruit_info()...............")
            print("fruit_info_list: ", fruit_info_list)
            print("fruit_info_list len: ", len(fruit_info_list))

        # 返回摘取信息列表
        return fruit_info_list


    def pack_camera_coord(self, fruit_info_list, depth_frame):
        coord_index = 0

        infos_len = len(fruit_info_list)
        if infos_len < 1:
            infos_len = 0
            coord_index = 0
            self.old_real_coord_list = []
            self.real_coord_list = []
            self.camera_coord_list = []

        if DEBUG == True:
            print("infos: ", fruit_info_list)
            print("infos len: ", infos_len)

        if infos_len >= 1:
            if self.get_detect_type() == Detector.FetchType.FETCH.value and infos_len == 1:
                if DEBUG == True:
                    print("------------------------------------------------------------------FETCH ! ------------------------------------------------------------------")
                data_list = self.unpack_xy_to_list(fruit_info_list)
                if len(data_list) == 2:
                    if DEBUG == True:
                        print("fruit_coord: ", data_list)
                    x, y = data_list[0], data_list[1]
                    world_coord = self.xy_to_world(x, y, depth_frame)
                    if world_coord is not None:
                        self.real_coord_list.append(world_coord)
            else:
                if self.get_detect_type() == Detector.FetchType.FETCH_ALL.value:
                    if DEBUG == True:
                        print("------------------------------------------------------------------FETCH_ALL ! ------------------------------------------------------------------")
                    for fruit in fruit_info_list:
                        if fruit is not None:
                            if DEBUG == True:
                                print("fruit info: ", fruit)
                            x, y = fruit["x"], fruit["y"]
                            z = depth_frame[y, x]
                            if DEBUG == True:
                                print("pixel coord X, Y, Z: ", (x, y, z))
                                
                            x, y, z = self.convert_depth_to_world(x, y, z)
                            if 0 in [x, y, z] or -0 in [x, y, z]:
                                continue
                            if DEBUG == True:
                                print("real coord X, Y, Z: ", (x, y, z))

                            old_len = len(self.old_real_coord_list)
                            self.old_real_coord_list.append((x, y, z))
                            new_len = len(self.old_real_coord_list)
                            if new_len == old_len + 1:
                                coord_index += 1
                if len(self.old_real_coord_list) == coord_index:
                    self.real_coord_list = self.old_real_coord_list

                    # 根据x, y的顺序从左到右排序真实的世界坐标值列表
                    self.real_coord_list = sorted(self.real_coord_list, key=lambda x: (x[0], x[1]))  # 0 -> x, 1 -> y, 2 -> z
                    
                    # 根据x顺序从左到右排序真实的世界坐标值列表
                    # self.real_coord_list = sorted(self.real_coord_list, key=lambda x: x[0])
                    
                    self.old_real_coord_list = []
        if DEBUG == True:
            print("self.real_coord_list: ", self.real_coord_list)
            print("self.real_coord_list len: ", len(self.real_coord_list))

        self.camera_coord_list = self.real_coord_list
        self.real_coord_list = []

    def render_screen(self, depth_frame):
        # 将深度帧数据16bit转8bit，用于渲染
        depth_frame = depth_frame.astype(np.uint8)

        # 将深度帧数据GRAY转RGB
        new_depth_frame = cv2.cvtColor(depth_frame, cv2.COLOR_GRAY2RGB)

        self.rgb_show = cv2.cvtColor(self.new_color_frame,cv2.COLOR_BGR2RGB)
        self.depth_show = new_depth_frame
        # 创建窗口
        #newDatas = np.vstack([self.new_color_frame, new_depth_frame])

        #cv2.namedWindow("ColorViewer", cv2.WINDOW_AUTOSIZE)
        #cv2.namedWindow("DepthViewer", cv2.WINDOW_AUTOSIZE)

        # 显示图像
        #cv2.imshow("ColorViewer", self.new_color_frame)
        #cv2.imshow("DepthViewer", new_depth_frame)

        # 将彩色帧数据大小调整为(height,width,3)
        #bind_mouse_event(cv2.cvtColor(self.new_color_frame, cv2.COLOR_RGB2BGR), "ColorViewer", mouseHSV)

    def close_window(self):
        # 按 ESC 或 'q' 关闭窗口
        is_close = False
        key = cv2.waitKey(1)
        if key == ord('q') or key == 27:
            cv2.destroyAllWindows()
            is_close = True
        return is_close

    def frame_processing(self, frame_list):
        finished = False
        if len(frame_list) == 2:
            color_frame = frame_list[0]
            depth_frame = frame_list[1]
            self.detector.detect(color_frame)

            if DEBUG == True:
                self.detector.debug_view(color_frame)

            infos = self.get_fruit_info()
            
            self.pack_camera_coord(infos, depth_frame)
            self.render_screen(depth_frame)

            finished = self.close_window()
        return finished

    def run(self):
        while True:
            frame = self.vp.get_color_frame()
            if frame is None:
                continue
            else:
                if DEBUG == True:
                    print("curr fruit_type: ", self.get_fruit_type())

                frame_list = self.get_depth_frame(frame)

                if self.frame_processing(frame_list) == True:
                    break

        self.vp.stop_pipe()
