import os
import sys

from loguru import logger

def init(log_path=None,rotation="00:00",retention="1 days",enqueue=True,compression=None):
	if log_path:
		if not os.path.exists(os.path.dirname(log_path)):
			os.mkdir(os.path.dirname(log_path))
		logger.add(log_path, rotation=rotation, retention=retention, enqueue=enqueue, compression=compression)
	return logger

# 日志简单配置

__all__ = ["logger"]