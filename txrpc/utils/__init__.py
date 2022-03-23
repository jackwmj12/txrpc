import asyncio
from functools import wraps
from imp import reload
import sys

from loguru import logger
from twisted.internet.defer import Deferred

def delay_import(modules, delay=0.1):
    '''
        延时调用
    :param modules: 模块地址
    :param delay: 延时时间(s)
    :return:
    '''
    def __import(modules):
        ''':param
        '''
        # logger.debug("即将导入模块 : <{modules}>".format(modules=modules))
        try:
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
            logger.debug(f"导入服务 <{modules}> 成功")
        except Exception as e:
            logger.error(e)
    if delay != 0:
        from twisted.internet import reactor
        reactor.callLater(delay, __import, modules)
    else:
        __import(modules)

def as_deferred(f):
    '''
    
    :param f:
    :return:
    '''
    return Deferred.fromFuture(asyncio.ensure_future(f))

def asDeferred(f):
    '''
    
    :param f:
    :return:
    '''
    @wraps(f)
    def as_deferred(*args, **kwargs):
        return Deferred.fromFuture(asyncio.ensure_future(f(*args,**kwargs)))
    
    return as_deferred

# def as_future(f):
#     return Deferred.asFuture(f)