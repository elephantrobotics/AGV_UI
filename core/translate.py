#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import dataclasses

from PyQt5.QtCore import QCoreApplication

_translate = QCoreApplication.translate


def ui_params():
    """
    set selection choices and style
    """
    language_params = [
        _translate("Communal", "English"),
        _translate("Communal", "Chinese")
    ]

    basic_control_params = [
        _translate("Communal", "Keyboard Control"),
        _translate("Communal", "Joystick-Alphabet"),
        _translate("Communal", "Joystick-Number")
    ]

    test_params = [
        _translate("Communal", "Motor"),
        _translate("Communal", "LED"),
        _translate("Communal", "3D Camera"),
        _translate("Communal", "Pump")
    ]


class _Language:
    def __init__(self):
        self.English = _translate("Communal", "English")
        self.Chinese = _translate("Communal", "Chinese")


class _Functional:
    def __init__(self):
        self.Motor = _translate("Communal", "Motor")
        self.Led = _translate("Communal", "LED")
        self.Pump = _translate("Communal", "Pump")
        self.Camera2D = _translate("Communal", "2D Camera")
        self.Camera3D = _translate("Communal", "3D Camera")
        self.Radar = _translate("Communal", "Radar")


class _Color:
    def __init__(self):
        self.Red = _translate("Communal", "Red")
        self.Green = _translate("Communal", "Green")
        self.Blue = _translate("Communal", "Blue")
        self.Yellow = _translate("Communal", "Yellow")
        self.White = _translate("Communal", "White")
        self.Black = _translate("Communal", "Black")
        self.Gray = _translate("Communal", "Gray")
        self.Orange = _translate("Communal", "Orange")
        self.Cyan = _translate("Communal", "Cyan")
        self.Purple = _translate("Communal", "Purple")


class _Direction:
    def __init__(self):
        self.GoAhead = _translate("Communal", "Go ahead")
        self.Retreat = _translate("Communal", "Retreat")
        self.PanLeft = _translate("Communal", "Pan left")
        self.PanRight = _translate("Communal", "Pan Right")
        self.CRotation = _translate("Communal", "Clockwise rotation")
        self.CCRotation = _translate("Communal", "Counterclockwise rotation")


class _State:
    def __init__(self):
        self.On = _translate("Communal", "On")
        self.Off = _translate("Communal", "Off")
        self.Open = _translate("Communal", "Open")
        self.Close = _translate("Communal", "Close")
        self.Connect = _translate("Communal", "Connect")
        self.Disconnect = _translate("Communal", "Disconnect")
        self.Start = _translate("Communal", "Start")
        self.Stop = _translate("Communal", "Stop")
        self.Pause = _translate("Communal", "Pause")
        self.Resume = _translate("Communal", "Resume")
        self.Finish = _translate("Communal", "Finish")
        self.Success = _translate("Communal", "Success")
        self.Fail = _translate("Communal", "Fail")


class _Other:
    def __init__(self):
        self.Testing = _translate("Communal", "testing")
        self.CameraOpenFailed = _translate("Communal", "camera open failed")
        self.CameraOpenSuccess = _translate("Communal", "camera open success")


class Translate:
    Language = _Language()
    Functional = _Functional()
    Color = _Color()
    Direction = _Direction()
    State = _State()
    Other = _Other()

    @classmethod
    def reload(cls):
        cls.Language = _Language()
        cls.Functional = _Functional()
        cls.Color = _Color()
        cls.Direction = _Direction()
        cls.State = _State()
        cls.Other = _Other()
        return cls






