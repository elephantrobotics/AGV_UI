#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import typing as T
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox, QWidget


class QPrompt(QObject):
    def __init__(self, parent: T.Optional[QWidget] = None):
        super(QPrompt, self).__init__(parent)
        self._parent = parent

    def set_parent(self, parent: QWidget):
        self._parent = parent

    def warning(self, title: str, message: str):
        return QMessageBox.warning(self._parent, title, message, QMessageBox.Ok)

    def question(self, title: str, message: str):
        return QMessageBox.question(self._parent, title, message, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes
