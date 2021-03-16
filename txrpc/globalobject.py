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
    单例模式的全局对象
'''
import os
from typing import Dict, List, Any

from txrpc.distributed.manager import RemoteUnFindedError
from txrpc.distributed.node import RemoteObject
from txrpc.distributed.root import PBRoot
from txrpc.service.service import Service
from txrpc.utils.log import logger
from txrpc.utils.singleton import Singleton

class GlobalObject(metaclass=Singleton):

    def __init__(self):
        self.config = {}  # 配置信息
        self.remote : Dict[str:RemoteObject] = {}  # REMOTE remote节点
        self.root : PBRoot = None
        
        self.starthandler = None #开始指令触发函数
        
    def get_config_from_object(self,obj):
        for key in dir(obj):
            if key.isupper():
                self.config[key] = getattr(obj, key)
        return self.config
    
    def getRemote(self,remote_name:str)->RemoteObject:
        '''
        :return
        '''
        remote_obj = self.remote.get(remote_name)
        if remote_obj:
            return remote_obj
        else:
            raise RemoteUnFindedError
        
def rootserviceHandle(target):
    """
    将服务加入根节点
    """
    GlobalObject().root.service.mapTarget(target)

class remoteserviceHandle:
    """
    该装饰器类，使用方法：
        def func:
            ...
        绑定成功后，root 可以调用 该 remote func 方法
    """
    def __init__(self,remotename):
        """
        """
        self.remotename = remotename

    def __call__(self,target):
        """
        """
        logger.debug(f"remoteserviceHandle <{self.remotename}>")
        
        GlobalObject().getRemote(self.remotename)._reference._service.mapTarget(target)

localservice = Service('localservice')

def localserviceHandle(target):
    '''
    创建本地服务装饰器
    被该装饰器装饰的函数
    可以且仅可以被本地使用
    @param target: func Object
    '''
    localservice.mapTarget(target)

