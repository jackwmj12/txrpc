import asyncio

from typing import Any

from twisted.internet import defer
import sys

from twisted.internet.defer import Deferred
from twisted.python import log

from utils import logger


def delay_import(modules, delay=0.1):
    '''
    :param module str 模块地址
    :param delay float 延时时间（s）
    '''
    
    def import_(modules):
        ''':param
        '''
        logger.debug("即将导入模块:{modules}".format(modules=modules))
        if modules:
            if isinstance(modules, (list, tuple)):
                for module in modules:
                    __import__(module)
            elif isinstance(modules, str):
                __import__(modules)

    from twisted.internet import reactor
    
    reactor.callLater(delay, import_, modules)

class asDeferred(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs) -> Deferred:
        return Deferred.fromFuture(asyncio.ensure_future(self.func(*args,**kwargs)))
