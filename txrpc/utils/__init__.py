import asyncio
from imp import reload

from typing import Any

from twisted.internet import defer
import sys

from twisted.internet.defer import Deferred

from txrpc.utils import logger


def delay_import(modules, delay=0.1):
    '''
    :param module str 模块地址
    :param delay float 延时时间（s）
    '''
    
    def __import(modules):
        ''':param
        '''
        logger.debug("即将导入模块:{modules}".format(modules=modules))
        if modules:
            if isinstance(modules, (list, tuple)):
                for module in modules:
                    if module not in sys.modules:
                        __import__(module)
                    else:
                        reload(sys.modules[module])
            elif isinstance(modules, str):
                if modules not in sys.modules:
                    __import__(modules)
                else:
                    reload(sys.modules[modules])
    
    if delay != 0:
        from twisted.internet import reactor
        reactor.callLater(delay, __import, modules)
    else:
        __import(modules)

class asDeferred(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs) -> Deferred:
        return Deferred.fromFuture(asyncio.ensure_future(self.func(*args,**kwargs)))
