#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import traceback
import typing as T

from PyQt5.QtWidgets import QTextBrowser


class Console(object):
    timestamp_format = "%Y-%m-%d %H:%M:%S"

    def __init__(self, output: T.Optional[QTextBrowser] = None):
        self.output: T.Optional[QTextBrowser] = output

    def set_output(self, output: QTextBrowser):
        self.output = output

    def _echo(self, msg: str):
        if self.output is None:
            raise RuntimeError("No output widget set")
        self.output.append(msg)

    def get_current_timestamp(self):
        return time.strftime(self.timestamp_format, time.localtime(time.time()))

    def echo(self, *args):
        timestamp = self.get_current_timestamp()
        self._echo(f"[{timestamp}] {' '.join(args)}")

    def exception(self, exception: Exception):
        message = traceback.format_exc()
        timestamp = self.get_current_timestamp()

        with open("error.log", "w") as f:
            f.write(repr(exception))
            f.write(message)

        self._echo(f"[{timestamp}] {message}")
