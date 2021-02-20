import logging
import os
import sys

from twisted.python import log
from twisted.python.logfile import DailyLogFile


class LevelFileLogObserver(log.FileLogObserver):

    def __init__(self, f, level=logging.INFO):
        log.FileLogObserver.__init__(self, f)
        self.logLevel = level

    def emit(self, eventDict):
        if eventDict['isError']:
            level = logging.ERROR
        elif 'level' in eventDict:
            level = eventDict['level']
        else:
            level = logging.INFO
        if level >= self.logLevel:
            eventDict["system"] = logging._levelToName[level]
            log.FileLogObserver.emit(self,eventDict)

def init(debug=True,file_path = None,file_name = None):
    
    log.msg(f"初始化日志路径为：{file_path}")

    if file_path and os.path.isdir(file_path) == False:  # 设置生产日志路径
        os.mkdir(file_path)
    
    log.FileLogObserver.timeFormat = '%Y-%m-%d %H:%M:%S'
    # log.FileLogObserver.
 
    if file_name and not debug:
        f = DailyLogFile(file_name + ".log", file_path)
        log.msg("当前为常规模式，设置日志路径，且将日志运行于每日分割模式")
        log_level = logging.INFO
    else:
        f = sys.stdout
        log.msg("当前为DEBUG模式，设置日志为屏幕输出")
        log_level = logging.DEBUG

    logger = LevelFileLogObserver(f, log_level)
    
    log.startLoggingWithObserver(logger.emit, setStdout=False)

def debug(msg):
    log.msg(msg, level=logging.DEBUG)

def msg(msg):
    log.msg(msg,level=logging.INFO)

def info(msg):
    log.msg(msg,level=logging.INFO)
    
def warning(msg):
    log.msg(msg, level=logging.WARNING)

def error(msg):
    log.msg(msg, level=logging.ERROR)

def err(msg):
    log.msg(msg, level=logging.ERROR)
    