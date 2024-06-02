import asyncio
from asyncio import Future
from functools import wraps
from imp import reload
import sys

from loguru import logger
from twisted.internet.defer import Deferred,ensureDeferred

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
        if modules:
            if isinstance(modules, (list, tuple)):
                for module in modules:
                    logger.debug("导入模块 : <{module}>".format(module=module))
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


def asDeferred(f):
    '''
    
    :param f:
    :return:
    '''
    @wraps(f)
    def as_deferred_wraps(*args, **kwargs) -> Deferred:
        return Deferred.fromFuture(asyncio.ensure_future(f(*args,**kwargs)))

    return as_deferred_wraps


def future_to_deferred(f):
    '''

    :param f:
    :return:
    '''

    @wraps(f)
    def as_deferred_wraps(*args, **kwargs) -> Deferred:
        return Deferred.fromFuture(asyncio.ensure_future(f(*args, **kwargs)))

    return as_deferred_wraps


def deferred_to_future(f):
    '''

    :param f:
    :return:
    '''

    @wraps(f)
    def as_future_wraps(*args, **kwargs) -> Future:
        return ensureDeferred(f(*args, **kwargs)).asFuture(loop=asyncio.get_event_loop())

    return as_future_wraps

# def deferred_to_future(deferred):
#     '''
#         deferred -> future
#     :param deferred:
#     :return:
#     '''
#     future = asyncio.Future()
#
#     def callback(result):
#         if not future.cancelled():
#             future.set_result(result)
#         return result
#
#     def errback(failure):
#         if not future.cancelled():
#             future.set_exception(failure.value)
#         return failure
#
#     deferred.addCallbacks(callback, errback)
#     return future
#
#
# def future_to_deferred(future):
#     '''
#         future -> deferred
#     :param future:
#     :return:
#     '''
#     d = Deferred()
#     # Callbacks to set the result or exception of the deferred
#     def callback(result):
#         d.callback(result)
#         return result
#
#     def errback(exception):
#         d.errback(exception)
#         return exception
#
#     future.add_done_callback(lambda f: f.add_done_callback(callback) if f.exception() is None else f.add_done_callback(errback))
#     return d