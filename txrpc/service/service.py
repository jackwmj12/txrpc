
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
from twisted.internet.defer import Deferred

from txrpc.utils import logger


class Service(object):
    """A remoting service 
    
    attributes:
    ============
     * name - string, service name.
     * runstyle 
    """
    SINGLE_STYLE = 1
    PARALLEL_STYLE = 2

    def __init__(self, name:str,runstyle = SINGLE_STYLE):
        self._name = name
        self._runstyle = runstyle
        self.unDisplay = set()
        self._lock = threading.RLock()
        self._targets = {} # Keeps track of targets internally

    def __iter__(self):
        return iter(self._targets.keys())

    def setName(self,name):
        self._name = name

    def addUnDisplayTarget(self,command):
        '''Add a target unDisplay when client call it.'''
        self.unDisplay.add(command)

    def mapTarget(self, target):
        """Add a target to the service."""
        self._lock.acquire()
        try:
            key = target.__name__
            if key in self._targets.keys():
                exist_target = self._targets.get(key)
                raise Exception(f"target {key} Already exists,Conflict between the {exist_target.__name__} and {target.__name__}")
            logger.debug(f"Service:<{self._name}> {key} 注册成功")
            self._targets[key] = target
        finally:
            self._lock.release()

    def unMapTarget(self, target):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            key = target.__name__
            if key in self._targets:
                del self._targets[key]
        finally:
            self._lock.release()
            
    def unMapTargetByKey(self,targetKey):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            del self._targets[targetKey]
        finally:
            self._lock.release()
            
    def getTarget(self, targetKey):
        """Get a target from the service by name."""
        self._lock.acquire()
        try:
            # logger.msg("共有服务target：{}".format(self._targets))
            target = self._targets.get(targetKey, None)
        finally:
            self._lock.release()
        return target
    
    def callTarget(self,targetKey,*args,**kwargs):
        '''call Target
        @param conn: client connection
        @param targetKey: target ID
        @param data: client data
        '''
        # logger.debug("targetKey为：{}".format(targetKey))
        # logger.debug("args为：{}".format(args))
        # logger.debug("kwargs为：{}".format(kwargs))
        if self._runstyle == self.SINGLE_STYLE:
            result = self.callTargetSingle(targetKey,*args,**kwargs)
        else:
            result = self.callTargetParallel(targetKey,*args,**kwargs)
        return result
    
    def callTargetSingle(self,targetKey,*args,**kw):
        '''call Target by Single
        @param conn: client connection
        @param targetKey: target ID
        @param data: client data
        '''
        target = self.getTarget(targetKey)
        
        self._lock.acquire()
        try:
            if not target:
                logger.err('the command ' + str(targetKey) + ' not Found on service in ' + self._name)
                return None
            if targetKey not in self.unDisplay:
                logger.debug("RPC : <remote> call method <%s> on service[single]" % target.__name__)
            defer_data = target(*args,**kw)
            if not defer_data:
                return None
            if isinstance(defer_data,defer.Deferred):
                return defer_data
            elif inspect.isawaitable(defer_data):
                return Deferred.fromFuture(asyncio.ensure_future(defer_data))
            elif asyncio.coroutines.iscoroutine(defer_data):
                return Deferred.fromCoroutine(defer_data)
            d = defer.Deferred()
            d.callback(defer_data)
        finally:
            self._lock.release()
        return d
    
    def callTargetParallel(self,targetKey,*args,**kw):
        '''call Target by Single
        @param conn: client connection
        @param targetKey: target ID
        @param data: client data
        '''
        self._lock.acquire()
        try:
            target = self.getTarget(targetKey)
            if not target:
                logger.err('the command ' + str(targetKey) + ' not Found on service in ' + self._name)
                return None
            logger.debug("RPC : <remote> call method <%s> on service[parallel]" % target.__name__)
            d = threads.deferToThread(target,*args,**kw)
        finally:
            self._lock.release()
        return d
    
class CommandService(Service):
    """A remoting service 
    According to Command ID search target
    """
    def mapTarget(self, target):
        """Add a target to the service."""
        self._lock.acquire()
        try:
            key = (target.__name__).split('_')[-1]
            if key in self._targets.keys():
                exist_target = self._targets.get(key)
                raise "target [%d] Already exists,\
                Conflict between the %s and %s"%(key,exist_target.__name__,target.__name__)
            logger.debug("当前服务器 CommandService:<{}> {} 注册成功".format(self._name, key))
            self._targets[key] = target
        finally:
            self._lock.release()
            
    def unMapTarget(self, target):
        """Remove a target from the service."""
        self._lock.acquire()
        try:
            key = (target.__name__).split('_')[-1]
            if key in self._targets:
                del self._targets[key]
        finally:
            self._lock.release()
    

    
    
    
            