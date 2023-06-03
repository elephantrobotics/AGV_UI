import cv2
import numpy as np
from enum import Enum
from typing import *
from CvDetection.config import *
from CvDetection.TargetBucket import TargetBucket

def rgb_to_hsv(self, r_, g_, b_):
    import colorsys
    import numpy as np

    rgb = (r_, g_, b_)
    r, g, b = [x / 255.0 for x in rgb]  # 将RGB值转换为0到1之间的值
    h, s, v = colorsys.rgb_to_hsv(r, g, b)  # 将RGB值转换为HSV值

    hsv = np.array([h, s, v])
    print(hsv)
    return hsv

class Detector:
    class FetchType(Enum):
        FETCH = False
        FETCH_ALL = True

    """
    检测识别类
    """

    HSV_DIST = {
        "redA": (np.array([0, 120, 50]), np.array([3, 255, 255])),
        "redB": (np.array([176, 120, 50]), np.array([179, 255, 255])),
        # "orange": (np.array([10, 120, 120]), np.array([15, 255, 255])),
        "orange": (np.array([8, 150, 150]), np.array([20, 255, 255])),
        "yellow": (np.array([28, 100, 150]), np.array([35, 255, 255])), # old
        # "yellow": (np.array([31, 246, 227]), np.array([35, 255, 255])),   # new
    }

    default_hough_params = {
        "method": cv2.HOUGH_GRADIENT_ALT,
        "dp": 1.5,
        "minDist": 20,
        "param2": 0.6,
        "minRadius": 15,
        "maxRadius": 40,
    }

    def __init__(self, target):
        self.bucket = TargetBucket()
        self.detect_target = target

    def set_target(self, target):
        if self.detect_target == target:
            return
        self.detect_target = target
        if target == "apple":
            self.bucket = TargetBucket(adj_tolerance=25, expire_time=0.2)
        elif target == "orange":
            self.bucket = TargetBucket()
        elif target == "pear":
            self.bucket = TargetBucket(adj_tolerance=35)

    def detect(self, rgb_data):
        if self.detect_target == "apple":
            self.__detect_apple(rgb_data)
        elif self.detect_target == "orange":
            self.__detect_orange(rgb_data)
        elif self.detect_target == "pear":
            self.__detect_pear(rgb_data)

    def __detect_apple(self, rgb_data):
        maskA = color_detect(rgb_data, *self.HSV_DIST["redA"])
        maskB = color_detect(rgb_data, *self.HSV_DIST["redB"])
        mask = maskA + maskB

        kernelA = cv2.getStructuringElement(cv2.MORPH_RECT, (8, 8))
        kernelB = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        mask = cv2.erode(mask, kernelA)
        mask = cv2.dilate(mask, kernelA)

        targets = circle_detect(
            mask, {"minDist": 15, "param2": 0.5,
                   "minRadius": 10, "maxRadius": 50}
        )
        self.bucket.add_all(targets)
        self.bucket.update()

    def __detect_orange(self, rgb_data):
        mask = color_detect(rgb_data, *self.HSV_DIST["orange"])
        targets = circle_detect(
            mask, {"minDist": 15, "param2": 0.1,
                   "minRadius": 7, "maxRadius": 30}
        )
        self.bucket.add_all(targets)
        self.bucket.update()

    def __detect_pear(self, rgb_data):
        mask = color_detect(rgb_data, *self.HSV_DIST["yellow"])

        kernelA = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        kernelB = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.erode(mask, kernelA)
        mask = cv2.dilate(mask, kernelA)
        mask = cv2.erode(mask, kernelB)

        targets = circle_detect(
            mask, {"minDist": 15, "param2": 0.1,
                   "minRadius": 15, "maxRadius": 70}
        )
        self.bucket.add_all(targets)
        self.bucket.update()

    def fetch(self):
        return self.bucket.fetch()

    def fetch_all(self):
        return self.bucket.fetch_all()

    def debug_view(self, bgr_data, view_all=True):
        if view_all:
            targets = self.bucket.fetch_all()
        else:
            targets = self.bucket.fetch()
            if targets is not None:
                targets = [targets]
        if targets is not None:
            for target in targets:
                x, y, radius = target["x"], target["y"], target["radius"]
                # draw outline
                cv2.circle(bgr_data, (x, y), radius, BGR_GREEN, 2)

                # draw circle center
                cv2.circle(bgr_data, (x, y), 1, BGR_RED, -1)


def circle_detect(rgb_data, hough_params=None):
    mask = rgb_data.astype(np.uint8)
    gray_mask = cv2.cvtColor(mask, cv2.COLOR_RGB2GRAY)

    # reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    gray_mask = cv2.medianBlur(gray_mask, 5)
    gray_mask = cv2.dilate(gray_mask, kernel)
    gray_mask = cv2.morphologyEx(gray_mask, cv2.MORPH_OPEN, kernel)

    default_params = {
        "method": cv2.HOUGH_GRADIENT_ALT,
        "dp": 1,
        "minDist": 20,
        "param2": 0.6,
        "minRadius": 15,
        "maxRadius": 40,
    }

    if hough_params is None:
        hough_params = default_params
    else:
        default_params.update(hough_params)
        hough_params = default_params

    circles = cv2.HoughCircles(image=gray_mask, **hough_params)

    res_centers = []
    if circles is not None and len(circles) > 0:
        for co, i in enumerate(circles[0, :], start=1):
            center_x, center_y = int(i[0]), int(i[1])
            radius = int(i[2])

            # fill roi
            ROI = np.zeros(gray_mask.shape).astype(np.uint8)
            cv2.circle(ROI, (center_x, center_y), radius, (255, 255, 255), -1)
            ROI = cv2.bitwise_and(gray_mask, ROI)

            # calculate the ratio between filled area and circle area
            area = radius * radius * 3.14
            non_zeros = np.count_nonzero(ROI)
            factor = non_zeros / area

            if factor > 0.5:
                if DEBUG:
                    # draw the outer circle in green
                    cv2.circle(mask, (center_x, center_y),
                               radius, (0, 0, 255), 1)
                    # draw the center of the circle in red
                    cv2.circle(mask, (center_x, center_y), 2, (0, 0, 255), 1)
                res_centers.append((center_x, center_y, radius))

    if DEBUG:
        cv2.imshow("Detect mask", mask)
        cv2.imshow("Detect gray mask", gray_mask)
    return res_centers


def color_detect(rgb_data, color_lower_bound, color_upper_bound):
    hsv = cv2.cvtColor(rgb_data, cv2.COLOR_RGB2HSV)
    res_mask = np.zeros(rgb_data.shape)

    color_mask = cv2.inRange(hsv, color_lower_bound, color_upper_bound)

    cnts, hierarchy = cv2.findContours(
        color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    if len(cnts) > 0:
        for cnt in cnts:
            cv2.drawContours(res_mask, [cnt], -1, (0, 255, 0), cv2.FILLED)

    # 这一步是为了填充因为高光部分无法被识别造成的孔洞
    kernel = np.ones((3, 3))
    res_mask = cv2.dilate(res_mask, kernel)

    if DEBUG:
        cv2.imshow("Color mask", res_mask)
    return res_mask
