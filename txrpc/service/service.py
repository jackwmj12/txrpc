
'''
Created on 2019-11-22
@author: LCC
            ┏┓　　　┏┓
          ┏┛┻━━━┛┻┓
          ┃　　　━　　　┃
          ┃　┳┛　┗┳　┃
          ┃　　　　　　　┃
          ┃　　　┻　　　┃
          ┗━┓　　　┏━┛
              ┃　　　┃
              ┃　　　┗━━━┓
              ┃　　　　　　　┣┓
              ┃　　　　　　　┏┛
              ┗┓┓┏━┳┓┏┛
                ┃┫┫　┃┫┫
                ┗┻┛　┗┻┛
                 神兽保佑，代码无BUG!
 @desc：
    服务类封装
'''
import asyncio
import inspect
import threading
from twisted.internet import defer,threads
from twisted.internet.defer import Deferred, fail, succeed
from twisted.python import failure
from typing import Callable, Set, Dict, Any
from loguru import logger

class Service(object):
    """
        服务基类(远程,本地)
    """

    def __init__(self, name: str):
        '''

        :param name: 服务名称
        :param runstyle:  运行模式 -单线程模式 -多线程模式
        '''
        self._name = name
        self.unDisplay: Set[str] = set()
        self._lock: threading.RLock = threading.RLock()
        self._functions: Dict[str,Callable] = {} # Keeps track of targets internally

    def __iter__(self):
        return self._functions.__iter__()

    def setName(self,name: str):
        '''
            设置服务名称
        :param name:
        :return:
        '''
        self._name = name

    def addUnDisplayFunction(self,functionName: str):
        '''
            将云函数加入黑名单
        :param command:
        :return:
        '''
        self.unDisplay.add(functionName)

    def mapFunction(self, f: Callable):
        """
            添加云函数到服务中
        :param f:
        :return:
        """
        self._lock.acquire()
        try:
            key = f.__name__
            if key in self._functions.keys():
                exist_target = self._functions.get(key)
                logger.warning("function [%s] Already exists, [%s] will be covered by [%s]" % (key, exist_target.__class__.__name__, f.__class__.__name__))
            logger.debug(f"Service : <{self._name}> {key} 注册成功")
            self._functions[key] = f
        finally:
            self._lock.release()

    def unMapFunction(self, f: Callable):
        """
            从服务中移除云函数
        :param f:
        :return:
        """
        self._lock.acquire()
        try:
            key = f.__name__
            if key in self._functions:
                del self._functions[key]
        finally:
            self._lock.release()

    def unMapFunctionByName(self,functionName):
        """
            通过云函数名称从服务中移除云函数
        :param f:
        :return:
        """
        self._lock.acquire()
        try:
            del self._functions[functionName]
        finally:
            self._lock.release()

    def getFunction(self, functionKey):
        '''
            从服务中获取云函数
        :param functionKey:
        :return:
        '''
        self._lock.acquire()
        try:
            # logger.info("共有服务target：{}".format(self._targets))
            target = self._functions.get(functionKey, None)
        finally:
            self._lock.release()
        return target

    def callFunction(self,functionName,*args,**kwargs) -> Any:
        '''
            调用服务下挂载的方法,且强制转化为deferred对象
        :param functionName:
        :param args:
        :param kwargs:
        :return:
        '''
        f = self.getFunction(functionName)
        if not f or functionName in self.unDisplay:
            err_msg = f'the command <{functionName}> not Found on service<{self._name}>'
            logger.error(err_msg)
            d = fail(err_msg)
        else:
            try:
                self._lock.acquire()
                # if functionName not in self.unDisplay:
                #     logger.debug(f"RPC : <remote> call method <{functionName}> : <{f.__name__}> on service[single]")
                defer_result = f(*args, **kwargs)
                if isinstance(defer_result, defer.Deferred):
                    # logger.debug(f"callFunction <{functionName}> deferred")
                    d = defer_result
                elif inspect.isawaitable(defer_result): #
                    # logger.debug(f"callFunction <{functionName}> awaitable")
                    d = Deferred.fromFuture(asyncio.ensure_future(defer_result))
                elif asyncio.coroutines.iscoroutine(defer_result):
                    # logger.debug(f"callFunction <{functionName}> coroutine")
                    d = defer.ensureDeferred(defer_result)
                else:
                    # logger.debug(f"callFunction <{functionName}> else")
                    d = succeed(defer_result)
            except Exception as e:
                logger.error(e)
                d = fail(e)
            finally:
                self._lock.release()
        return d

    def callFunctionEnsureDeferred(self,functionName,*args,**kwargs) -> Deferred:
        '''
            调用服务下挂载的方法,且强制转化为deferred对象(一般用于deferredList)
        :param functionName:
        :param args:
        :param kwargs:
        :return:
        '''
        f = self.getFunction(functionName)
        if not f or functionName in self.unDisplay:
            err_msg = f'the command <{functionName}> not Found on service<{self._name}>'
            logger.error(err_msg)
            d = fail(err_msg)
        else:
            try:
                self._lock.acquire()
                # if functionName not in self.unDisplay:
                #     logger.debug(f"RPC : <remote> call method <{functionName}> : <{f.__name__}> on service[single]")
                defer_result = f(*args, **kwargs)
                if isinstance(defer_result, defer.Deferred):
                    # logger.debug(f"callFunctionEnsureDeferred <{functionName}> deferred")
                    d = defer_result
                elif inspect.isawaitable(defer_result):
                    # logger.debug(f"callFunctionEnsureDeferred <{functionName}> awaitable")
                    d = Deferred.fromFuture(asyncio.ensure_future(defer_result))
                elif asyncio.coroutines.iscoroutine(defer_result):
                    # logger.debug(f"callFunctionEnsureDeferred <{functionName}> coroutine")
                    d = defer.ensureDeferred(defer_result)
                else:
                    d = succeed(defer_result)
            except Exception as e:
                logger.error(e)
                d = fail(None)
            finally:
                self._lock.release()
        return d

    # def callFunctionSingle(self,functionName,*args,**kw):
    #     '''
    #         通过函数名称,进行云函数单线程调用
    #     :param targetKey:
    #     :param args:
    #     :param kw:
    #     :return:
    #     '''
    #     f = self.getFunction(functionName)
    #     self._lock.acquire()
    #     try:
    #         if not f or functionName in self.unDisplay:
    #             # logger.error(f'the command <{functionName}> not Found on service<{self._name}>')
    #             d = None
    #         # if functionName not in self.unDisplay:
    #         #     logger.debug(f"RPC : <remote> call method <{functionName}> : <{f.__name__}> on service[single]")
    #         # logger.debug("RPC : <remote> call method <%s> on service[single]" % f.__name__)
    #         else:
    #             defer_data = f(*args, **kw)
    #             if isinstance(defer_data, defer.Deferred):
    #                 # logger.debug(f"callFunctionSingle <{functionName}> deferred")
    #                 d = defer_data
    #             elif inspect.isawaitable(defer_data):
    #                 # logger.debug(f"callFunctionSingle <{functionName}> awaitable")
    #                 d = Deferred.fromFuture(asyncio.ensure_future(defer_data))
    #             elif asyncio.coroutines.iscoroutine(defer_data):
    #                 # logger.debug(f"callFunctionSingle <{functionName}> coroutine")
    #                 d = defer.Deferred.fromCoroutine(defer_data)
    #             # elif isinstance(defer_data, failure.Failure):
    #             #     logger.debug(f"callFunction <{functionName}> failure")
    #             #     d = fail(defer_data)
    #             # else:
    #             #     logger.debug(f"callFunction <{functionName}> succeed")
    #             #     d = succeed(defer_data)
    #             else:
    #                 # logger.debug(f"callFunctionSingle <{functionName}> else")
    #                 d = defer_data
    #     finally:
    #         self._lock.release()
    #     return d
    #
    # def callFunctionParallel(self,functionName,*args,**kw):
    #     '''
    #         通过函数名称,进行云函数多线程调用
    #     :param functionName:
    #     :param args:
    #     :param kw:
    #     :return:
    #     '''
    #     self._lock.acquire()
    #     try:
    #         f = self.getFunction(functionName)
    #         if not f:
    #             # logger.error(f'the command {functionName} not Found on service<{self._name}>')
    #             return None
    #         logger.debug("RPC : <remote> call method <%s> on service[parallel]" % f.__name__)
    #         d = threads.deferToThread(f,*args,**kw)
    #     finally:
    #         self._lock.release()
    #     return d

class CommandService(Service):

    def mapFunction(self, f: Callable):
        """
            添加云函数到服务中
                云函数名称格式为 {command}__{function_name}
        :param f:
        :return:
        """
        self._lock.acquire()
        try:
            key = (f.__name__).split('__')[-1]
            if key in self._functions.keys():
                exist_target = self._functions.get(key)
                logger.warning("function [%s] Already exists, [%s] will be covered by [%s]" % (key, exist_target.__class__.__name__, f.__class__.__name__))
            logger.debug(f"Command Service:<{self._name}> {key} 注册成功")
            self._functions[key] = f
        finally:
            self._lock.release()

    def unmapFunction(self, f: Callable):
        """
            从服务中移除云函数
        :param f:
        :return:
        """
        self._lock.acquire()
        try:
            key = (f.__name__).split('__')[-1]
            if key in self._functions:
                del self._functions[key]
        finally:
            self._lock.release()

