#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import subprocess
import traceback


class Command:

    @classmethod
    def check_output(cls, command) -> str:

        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Command execution failed: {e}")
            traceback.print_exc()
            output = b''
        return output.decode("utf-8").strip()

    @classmethod
    def run(cls, command, shell=True, in_terminal: bool = False):
        if in_terminal is True:
            command = f'gnome-terminal -- bash -c "{command} || exec bash"'
        return subprocess.Popen(command, shell=shell)

    @classmethod
    def cat(cls, filepath):
        return cls.check_output(f"cat {filepath}")

    @classmethod
    def kill(cls, command):
        cls.run("ps -ef | grep -E %s | grep -v 'grep' | awk '{print $2}' | xargs kill -2" % command, shell=True)

    @classmethod
    def alive(cls, command):
        return int(cls.check_output("ps -ef | grep -E %s | grep -v 'grep' | wc -l" % command)) > 0

