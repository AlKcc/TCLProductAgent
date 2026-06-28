"""
日志工具模块
"""
import logging
import sys
from pathlib import Path
from .config import LOG_LEVEL, LOG_FILE


def setup_logger(name: str = "TCLAgent", log_file: Path = LOG_FILE, level: str = LOG_LEVEL):
    """配置日志系统"""

    # 创建logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # 避免重复添加handler
    if logger.handlers:
        return logger

    # 控制台handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))

    # 文件handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 格式化
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 添加handler
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# 创建全局logger
logger = setup_logger()