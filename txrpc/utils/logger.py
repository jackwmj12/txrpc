import logging
import sys

from twisted.python import log

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

def init(debug=True):

    log.FileLogObserver.timeFormat = '%Y-%m-%d %H:%M:%S'

    if debug:
        f = sys.stdout
        log.msg("当前为DEBUG模式，设置日志为屏幕输出")
        log_observer = LevelFileLogObserver(f, logging.DEBUG)
        log.startLoggingWithObserver(log_observer.emit, setStdout=False)
    else:
        pass

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
    