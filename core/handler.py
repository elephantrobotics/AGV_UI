#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from pymycobot import MyAgv


class AgvHandler(MyAgv):

    def __init__(self, port: str, baudrate: int, debug=False):
        super().__init__(port, baudrate, debug)

    def open(self):
        if self._serial_port.is_open is False:
            self._serial_port.open()

    def is_opened(self):
        return self._serial_port.is_open

    def close(self):
        if self._serial_port.is_open is True:
            self._serial_port.close()

    def get_system_version(self):
        firmware_version = self.get_firmware_version()
        # modified_version = self.agv.get_modified_version()
        return f"{firmware_version}"
