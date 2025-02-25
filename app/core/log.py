import logging
import colorlog
import os
from logging.handlers import RotatingFileHandler


def init_logger():
    # 检查并创建 logs 文件夹
    if not os.path.exists("./logs"):
        os.makedirs("./logs")

    # 创建自定义的日志格式器
    color_formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(levelname)s%(reset)s:     %(asctime)s     %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        secondary_log_colors={},
        style="%",
    )

    file_formatter = logging.Formatter(
        "%(levelname)s:     %(asctime)s     %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 创建流处理器（控制台输出）
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(color_formatter)

    # 创建轮转文件处理器（文件输出）
    file_handler = RotatingFileHandler(
        "./logs/log.log",
        maxBytes=5 * 1024 * 1024,  # 文件大小限制（5MB）
        backupCount=5,  # 保留的旧日志文件数
        encoding="utf-8",
    )
    file_handler.setFormatter(file_formatter)

    # 配置全局日志记录器
    logging.basicConfig(level=logging.INFO, handlers=[stream_handler, file_handler])
