
import sys

import time
import numpy as np
import cv2
import Pipeline
import Frame
from AGV_3D_Vision.CvDetection.detection import Detector
from .utli import *
from AGV_3D_Vision.libs import *
from Error import ObException
from Property import *
from ObTypes import *


class VideoStreamPipe:
    """
    视频流封装类
    """

    def __init__(self):
        try:
            # 创建一个Pipeline，Pipeline是整个高级API的入口，通过Pipeline可以很容易的打开和关闭
            # 多种类型的流并获取一组帧数据
            pipe = Pipeline.Pipeline(None, None)
            self.pipe = pipe
            # 通过创建Config来配置Pipeline要启用或者禁用哪些流
            config = Pipeline.Config()
            self.config = config

            self.frame_time = 100

            try:
                # 获取彩色相机的所有流配置，包括流的分辨率，帧率，以及帧的格式
                profiles = pipe.getStreamProfileList(OB_PY_SENSOR_COLOR)
                videoProfile = None
                try:
                    # 根据指定的格式查找对应的Profile,优先选择RGB888格式
                    videoProfile = profiles.getVideoStreamProfile(
                        640, 0, OB_PY_FORMAT_RGB888, 30
                    )
                except ObException as e:
                    print(
                        "function: %s\nargs: %s\nmessage: %s\ntype: %d\nstatus: %d"
                        % (
                            e.getName(),
                            e.getArgs(),
                            e.getMessage(),
                            e.getExceptionType(),
                            e.getStatus(),
                        )
                    )
                    # 没找到RGB888格式后不匹配格式查找对应的Profile进行开流
                    videoProfile = profiles.getVideoStreamProfile(
                        640, 0, OB_PY_FORMAT_UNKNOWN, 30
                    )
                colorProfile = videoProfile.toConcreteStreamProfile(
                    OB_PY_STREAM_VIDEO)
                self.windowWidth = colorProfile.width()
                self.windowHeight = colorProfile.height()
                config.enableStream(colorProfile)
            except ObException as e:
                print(
                    "function: %s\nargs: %s\nmessage: %s\ntype: %d\nstatus: %d"
                    % (
                        e.getName(),
                        e.getArgs(),
                        e.getMessage(),
                        e.getExceptionType(),
                        e.getStatus(),
                    )
                )
                print("Current device is not support color sensor!")

            try:
                # 获取深度相机的所有流配置，包括流的分辨率，帧率，以及帧的格式
                profiles = pipe.getStreamProfileList(OB_PY_SENSOR_DEPTH)

                videoProfile = None
                try:
                    # 根据指定的格式查找对应的Profile,优先选择Y16格式
                    videoProfile = profiles.getVideoStreamProfile(
                        320, 0, OB_PY_FORMAT_Y16, 30
                    )
                except ObException as e:
                    print(
                        "function: %s\nargs: %s\nmessage: %s\ntype: %d\nstatus: %d"
                        % (
                            e.getName(),
                            e.getArgs(),
                            e.getMessage(),
                            e.getExceptionType(),
                            e.getStatus(),
                        )
                    )
                    # 没找到Y16格式后不匹配格式查找对应的Profile进行开流
                    videoProfile = profiles.getVideoStreamProfile(
                        320, 0, OB_PY_FORMAT_UNKNOWN, 30
                    )
                depthProfile = videoProfile.toConcreteStreamProfile(
                    OB_PY_STREAM_VIDEO)
                config.enableStream(depthProfile)
            except ObException as e:
                print(
                    "function: %s\nargs: %s\nmessage: %s\ntype: %d\nstatus: %d"
                    % (
                        e.getName(),
                        e.getArgs(),
                        e.getMessage(),
                        e.getExceptionType(),
                        e.getStatus(),
                    )
                )
                print("Current device is not support depth sensor!")
                sys.exit()

            # 启动在Config中配置的流，如果不传参数，将启动默认配置启动流
            pipe.start(config, None)

            # 获取镜像属性是否有可写的权限
            if pipe.getDevice().isPropertySupported(
                OB_PY_PROP_COLOR_MIRROR_BOOL, OB_PY_PERMISSION_WRITE
            ):
                # 设置镜像
                pipe.getDevice().setBoolProperty(OB_PY_PROP_COLOR_MIRROR_BOOL, False)
                # pipe.getDevice().setBoolProperty(OB_PY_PROP_DEPTH_MIRROR_BOOL, False)

        except ObException as e:
            print(
                "function: %s\nargs: %s\nmessage: %s\ntype: %d\nstatus: %d"
                % (
                    e.getName(),
                    e.getArgs(),
                    e.getMessage(),
                    e.getExceptionType(),
                    e.getStatus(),
                )
            )

    def __enter__(self):
        print("Pipe started.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Pipe stopped.")
        self.pipe.stop()

    def get_pipe(self):
        return self.pipe

    def stop_pipe(self):
        self.pipe.stop()

    def start_pipe(self):
        self.pipe.start(self.config, None)

    def get_color_frame(self):
        Frames = self.pipe.waitForFrames(self.frame_time)
        if Frames is not None:
            return Frames

    def get_color_frame_2(self):
        while 1:
            _Frame = self.pipe.waitForFrames(self.frame_time)
            if _Frame == None:
                print("111111111111111111111111111111111111111111")
                continue
            else:
                if _Frame is not None:
                    colorFrame = _Frame.colorFrame()
                    depthFrame = _Frame.depthFrame()
                    if colorFrame != None and depthFrame != None:
                        # 获取帧的大小和数据
                        colorSize = colorFrame.dataSize()
                        colorData = colorFrame.data()
                        depthSize = depthFrame.dataSize()
                        depthData = depthFrame.data()
                        colorWidth = colorFrame.width()
                        colorHeight = colorFrame.height()
                        depthWidth = depthFrame.width()
                        depthHeight = depthFrame.height()
                        if colorSize != 0 and depthSize != 0:
                            newColorData = colorData
                            # 将彩色帧数据大小调整为(height,width,3)
                            newColorData.resize(
                                (colorHeight, colorWidth, 3)
                            )
                            # newColorData = cv2.flip(newColorData,1)
                            # 将彩色帧数据BGR转RGB
                            newColorData = cv2.cvtColor(
                                newColorData, cv2.COLOR_BGR2RGB)

                            # 将深度帧数据大小调整为(height,width,2)
                            depthData = np.resize(
                                depthData, (depthHeight, depthWidth, 2))
                            # # 分辨率不一致，多余的部分填0
                            # if colorHeight != depthHeight:
                            #     depthData[depthHeight:colorHeight-1,:]=0

                            # 将深度帧数据8bit转16bit
                            newDepthData = depthData[:, :,
                                                     0] + depthData[:, :, 1] * 256
                            # # 将深度帧数据16bit转8bit，用于渲染
                            # newDepthData = newDepthData.astype(np.uint8)
                            # # 将深度帧数据GRAY转RGB
                            # newDepthData = cv2.cvtColor(newDepthData, cv2.COLOR_GRAY2RGB)

                            # # 列表存储彩色帧及深度帧，用于渲染
                            # colorDatas = newColorData
                            # depthDatas = newDepthData

                            # windowName = "MultiDevice dev" + str(1)
                            # # 按垂直顺序堆叠彩色帧及深度帧
                            # newDatas = np.vstack([colorDatas, depthDatas])

                            # # 创建窗口
                            # cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

                            # cv2.resizeWindow(windowName, int(colorWidth/2), colorHeight)

                            # # 显示图像
                            # cv2.imshow(windowName, newDatas)

                            # key = cv2.waitKey(1)
                            # # 按 ESC 或 'q' 关闭窗口
                            # if key == 27 or key == 113:
                            #     isExit = True
                            #     exit()
                            # rgb_Frame = _Frame.colorFrame()
                            # depth_Frame = _Frame.depthFrame()
                            # if rgb_Frame.dataSize() != None and depth_Frame.dataSize() != None:
                            #     newColorData = rgb_Frame.data()
                            #     print("c+d")
                            #     newColorData.resize((self.windowHeight, self.windowWidth, 3))
                            #     _newColorData = cv2.flip(newColorData, 1)

                            #     newDephtData = depth_Frame.data()
                            #     # 将深度帧数据大小调整为(height,width,2)
                            #     newDephtData = np.resize(newDephtData, (400, 640, 2))

                            #     # 将深度帧数据8bit转16bit
                            #     _newDephtData = newDephtData[:, :, 0] + newDephtData[:, :, 1] * 256
                            return newColorData, newDepthData


def test():
    _t = time.time()
    newColorData, newDepthData = vp.get_color_frame_2()

    print(time.time() - _t)
    if newColorData == [] and newDepthData == []:
        pass
    else:
        newColorData = cv2.flip(newColorData, 1)
        vs.detect(newColorData)
        # if DEBUG == True:
        #     centers = circle_detect(rgb_data)
        #     print(centers)

        objs = vs.fetch_all()
        print("objs: ", objs)
        if objs != None:
            for obj in objs:
                x = obj["x"]
                y = obj["y"]
                z = newDepthData[int(y-40)/2, int(x-40)/2]
                print(y - 40, x - 40, z)
        # 将深度帧数据16bit转8bit，用于渲染
        newDepthData = newDepthData.astype(np.uint8)
        # 将深度帧数据GRAY转RGB
        newDepthData = cv2.cvtColor(newDepthData, cv2.COLOR_GRAY2RGB)

        # 列表存储彩色帧及深度帧，用于渲染
        colorDatas = newColorData
        depthDatas = newDepthData

        windowName = "MultiDevice dev" + str(1)
        # 按垂直顺序堆叠彩色帧及深度帧
        newDatas = np.vstack([colorDatas, depthDatas])

        # 创建窗口
        cv2.namedWindow(windowName, cv2.WINDOW_NORMAL)

        cv2.resizeWindow(windowName, int(vp.windowWidth / 2), vp.windowHeight)

        # 显示图像
        cv2.imshow(windowName, newDatas)

        key = cv2.waitKey(1)
        # 按 ESC 或 'q' 关闭窗口
        if key == 27 or key == 113:
            isExit = True
            exit()


if __name__ == "__main__":
    vp = VideoStreamPipe()
    vs = Detector("apple")
    while True:
        frame = vp.get_color_frame()
        if frame is None:
            continue
        else:
            # 在窗口中渲染一组帧数据，这里只渲染彩色帧
            rgb_data = frame
            cv2.namedWindow("ColorViewer", cv2.WINDOW_AUTOSIZE)
            bind_mouse_event(rgb_data, "ColorViewer", mouseHSV)
            vs.detect(rgb_data)

            # 将帧数据BGR转RGB
            bgr_data = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2BGR)
            # 创建窗口
            vs.debug_view(bgr_data, view_all=True)

            # 显示图像
            cv2.imshow("ColorViewer", bgr_data)
            key = cv2.waitKey(1)
            # 按 ESC 或 'q' 关闭窗口
            if key == 113 or key == 27:
                cv2.destroyAllWindows()
                break
    vp.stop_pipe()
