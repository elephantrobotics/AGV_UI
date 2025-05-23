#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pymycobot
from pymycobot import MyAgv
from .singleton import Singleton

if pymycobot.__version__ >= "3.9.8":
    print(f" # setup AGV Handler with version 3.9.8")


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

elif pymycobot.__version__ >= "3.8.0":
    print(f" # setup AGV Handler with version 3.8.0")


    class AgvHandler(MyAgv, metaclass=Singleton):

        def __init__(self, port: str, baudrate: int, debug=False):
            super().__init__(comport=port, baudrate=baudrate, debug=debug)

        @property
        def is_opened(self):
            return self._serial_port.is_open

else:
    print(f" # setup AGV Handler with version x.x.x")


    class AgvHandler(MyAgv, metaclass=Singleton):

        def __init__(self, port: str, baudrate: int, debug=False):
            super().__init__(port, baudrate, debug)

        def open(self):
            if self._serial_port.is_open is False:
                self._serial_port.open()

        @property
        def is_opened(self):
            return self._serial_port.is_open

        def close(self):
            if self._serial_port.is_open is True:
                self._serial_port.close()
