import logging
from PyQt5.QtCore import QObject, pyqtSignal
from logging import Handler


class QConsoleHandler(QObject, Handler):
    level_color_mapping = {
        logging.INFO: "black",
        logging.WARNING: "black",
        logging.ERROR: "red",
        logging.CRITICAL: "cyan",
        logging.DEBUG: "green"
    }
    outputted = pyqtSignal(str)

    """A custom logging handler that outputs to a QTextBrowser widget."""

    def __init__(self, formatter: logging.Formatter, level: int = logging.INFO, parent=None):
        super().__init__(parent=parent)
        self.level = level
        self.setFormatter(formatter)

    def format(self, record):
        format_message = super().format(record)
        color = self.level_color_mapping.get(record.levelno, "white")
        return f"<p style='color:{color};padding:0px;margin:0px;'>{format_message}</p>"

    def emit(self, record):
        message = self.format(record)
        self.outputted.emit(message)

