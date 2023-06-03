from functools import partial
from typing import *
import numpy as np
import cv2


def mouseRGB(img: np.ndarray, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        colorsR = img[y, x, 0]
        colorsG = img[y, x, 1]
        colorsB = img[y, x, 2]
        colors = img[y, x]
        print("Red: ", colorsR)
        print("Green: ", colorsG)
        print("Blue: ", colorsB)
        print("RGB Format: ", colors)
        print("Coordinates of pixel: X: ", x, "Y: ", y)


# Not work
def mouseHSV(img, event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        colorsH = img[y, x, 0]
        colorsS = img[y, x, 1]
        colorsV = img[y, x, 2]
        colors = img[y, x]
        print("H: ", colorsH)
        print("S: ", colorsS)
        print("V: ", colorsV)
        print("HSV Format: ", colors)
        print(f"HSV ratio Format: {colorsH/179},{colorsS/255},{colorsV/255}")
        print(
            f"HSV standard Format:{colorsH/179*360},{colorsS/255},{colorsV/255}")
        print("Coordinates of pixel: X: ", x, "Y: ", y)


SUPPORTED_FUNC = [mouseRGB, mouseHSV]


def bind_mouse_event(img, window_name, func):
    if func not in SUPPORTED_FUNC:
        print("Function not supported.")
        return

    partial_click = partial(func, img)
    cv2.setMouseCallback(window_name, partial_click)
