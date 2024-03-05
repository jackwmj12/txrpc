
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
from typing import Callable, Set, Dict

from txrpc.utils import as_deferred
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

    def callFunction(self,functionName,*args,**kwargs):
        '''
            通过云函数名称,调用云函数
        :param functionName:
        :param args:
        :param kwargs:
        :return:
        '''
        f = self.getFunction(functionName)
        self._lock.acquire()
        try:
            if not f:
                logger.error('the command ' + str(functionName) + ' not Found on service in ' + self._name)
                return None
            if functionName not in self.unDisplay:
                logger.debug(f"RPC : <remote> call method <{functionName}> : <{f.__name__}> on service[single]")

            defer_data = f(*args, **kwargs)
            if isinstance(defer_data, defer.Deferred):
                # logger.debug(f"{target.__name__} deferred")
                d = defer_data
            elif inspect.isawaitable(defer_data):
                # logger.debug(f"{target.__name__} awaitable")
                d = as_deferred(defer_data)
            elif asyncio.coroutines.iscoroutine(defer_data):
                # logger.debug(f"{target.__name__} coroutine")
                d = defer.Deferred.fromCoroutine(defer_data)
            elif isinstance(defer_data, failure.Failure):
                # logger.debug(f"{target.__name__} failure")
                d = fail(defer_data)
            else:
                # logger.debug(f"{target.__name__} succeed")
                d = succeed(defer_data)
        finally:
            self._lock.release()
        return d

    def callFunctionSingle(self,functionName,*args,**kw):
        '''
            通过函数名称,进行云函数单线程调用
        :param targetKey:
        :param args:
        :param kw:
        :return:
        '''
        target = self.getFunction(functionName)
        self._lock.acquire()
        try:
            if not target:
                logger.error('the command ' + str(functionName) + ' not Found on service in ' + self._name)
                return None
            if functionName not in self.unDisplay:
                logger.debug(f"RPC : <remote> call method <{functionName}> : <{target.__name__}> on service[single]")

            defer_data = target(*args,**kw)
            if isinstance(defer_data, defer.Deferred):
                # logger.debug(f"{target.__name__} deferred")
                d = defer_data
            elif inspect.isawaitable(defer_data):
                # logger.debug(f"{target.__name__} awaitable")
                d = as_deferred(defer_data)
            elif asyncio.coroutines.iscoroutine(defer_data):
                # logger.debug(f"{target.__name__} coroutine")
                d = defer.Deferred.fromCoroutine(defer_data)
            elif isinstance(defer_data, failure.Failure):
                # logger.debug(f"{target.__name__} failure")
                d = fail(defer_data)
            else:
                # logger.debug(f"{target.__name__} succeed")
                d = succeed(defer_data)
            # d = defer.Deferred()
            # d.callback(defer_data)
        finally:
            self._lock.release()
        return d

    def callFunctionParallel(self,functionName,*args,**kw):
        '''
            通过函数名称,进行云函数多线程调用
        :param functionName:
        :param args:
        :param kw:
        :return:
        '''
        self._lock.acquire()
        try:
            f = self.getFunction(functionName)
            if not f:
                logger.error('the command ' + str(functionName) + ' not Found on service in ' + self._name)
                return None
            logger.debug("RPC : <remote> call method <%s> on service[parallel]" % f.__name__)
            d = threads.deferToThread(f,*args,**kw)
        finally:
            self._lock.release()
        return d

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

