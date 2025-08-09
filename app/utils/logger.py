from loguru import logger
import sys

# 基础日志配置
logger.remove()
logger.add(sys.stderr, level="INFO", enqueue=True, backtrace=False, diagnose=False,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

__all__ = ["logger"]

