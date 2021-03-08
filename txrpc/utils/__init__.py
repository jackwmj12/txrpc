import asyncio
from functools import wraps
from imp import reload
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
        logger.debug("即将导入模块 : <{modules}>".format(modules=modules))
        if modules:
            if isinstance(modules, (list, tuple)):
                for module in modules:
                    # logger.debug(32*"1")
                    if module not in sys.modules:
                        # logger.debug(32 * "2")
                        __import__(module)
                    else:
                        # logger.debug(32 * "3")
                        reload(sys.modules[module])
                    # logger.debug(32 * "4")
            elif isinstance(modules, str):
                if modules not in sys.modules:
                    __import__(modules)
                else:
                    reload(sys.modules[modules])
        # logger.debug(f"导入服务 <{modules}> 成功")
    
    if delay != 0:
        from twisted.internet import reactor
        reactor.callLater(delay, __import, modules)
    else:
        __import(modules)

def as_deferred(f):
    return Deferred.fromFuture(asyncio.ensure_future(f))

def asDeferred(f):
    
    @wraps(f)
    def as_deferred(*args, **kwargs):
        return Deferred.fromFuture(asyncio.ensure_future(f(*args,**kwargs)))
    
    return as_deferred

# def as_future(f):
#     return Deferred.asFuture(f)