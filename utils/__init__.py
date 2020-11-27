import asyncio
import logging
from twisted.internet import reactor
import sys

from twisted.internet.defer import Deferred
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

class Log:

    @staticmethod
    def debug(data):
        log.msg(data,level=logging.DEBUG)

    @staticmethod
    def msg(data):
        log.msg(data,level=logging.INFO)

    @staticmethod
    def info(data):
        log.msg(data,level=logging.INFO)

    @staticmethod
    def warning(data):
        log.msg(data,level=logging.WARNING)

    @staticmethod
    def err(data):
        log.err(data,level=logging.ERROR)

    @staticmethod
    def D(data):
        log.msg(data, level=logging.DEBUG)

    @staticmethod
    def M(data):
        log.msg(data, level=logging.INFO)

    @staticmethod
    def W(data):
        log.msg(data, level=logging.WARNING)

    @staticmethod
    def E(data):
        log.err(data, level=logging.ERROR)

    @staticmethod
    def init_(debug=True):

        log.FileLogObserver.timeFormat = '%Y-%m-%d %H:%M:%S'

        if debug:
            f = sys.stdout
            Log.msg("当前为DEBUG模式，设置日志为屏幕输出")
            logger = LevelFileLogObserver(f, logging.DEBUG)
            log.startLoggingWithObserver(logger.emit, setStdout=False)
        else:
            pass

def delay_import(modules, delay=0.1):
    '''
    :param module str 模块地址
    :param delay float 延时时间（s）
    '''

    def import_(modules):
        ''':param
        '''
        Log.debug("即将导入模块:{modules}".format(modules=modules))
        if modules:
            if isinstance(modules, (list, tuple)):
                for module in modules:
                    __import__(module)
            elif isinstance(modules, str):
                __import__(modules)

    reactor.callLater(delay, import_, modules)

class asDeferred(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs) -> Deferred:
        return Deferred.fromFuture(asyncio.ensure_future(self.func(*args,**kwargs)))
    