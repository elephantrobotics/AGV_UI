#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import sys
import os


class FileResource:
    """
    FileResource is a class to read and write file.
    """

    def __init__(self, relative_path: str):
        if getattr(sys, 'frozen', False):
            base_path = getattr(sys, "_MEIPASS")
        else:
            base_path = os.getcwd()
        self.path = os.path.join(base_path, relative_path)

    def exits(self, filepath: str):
        return os.path.exists(os.path.join(self.path, filepath))

    def read(self, *args):
        with open(os.path.join(self.path, *args), 'r', encoding='utf-8') as f:
            return f.read()

    def write(self, filepath: str, content: str):
        with open(os.path.join(self.path, filepath), 'w', encoding='utf-8') as f:
            f.write(content)

    def get(self, *args):
        return os.path.join(self.path, *args)
