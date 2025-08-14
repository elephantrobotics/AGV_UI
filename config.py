#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

__version__ = "1.0.0-b1"
logging.basicConfig(
    level=logging.INFO,
    filename="logs/assets.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class LoggingConfiger:
    class Console:
        message_format = '[%(asctime)s] %(message)s'    # docs
        timestamp_format = '%Y-%m-%d %H:%M:%S'
        level = logging.INFO

