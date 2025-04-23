#!/usr/bin/env python
# -*- coding: UTF-8 -*-


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def get_instance(cls):
        assert cls in cls._instances, "Singleton instance not created yet"
        return cls._instances[cls]
