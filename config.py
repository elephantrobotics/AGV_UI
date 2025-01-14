#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="logs/assets.log",
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


class LoggingConfiger:
    class Console:
        message_format = '[%(asctime)s] %(message)s'
        timestamp_format = '%Y-%m-%d %H:%M:%S'
        level = logging.INFO

