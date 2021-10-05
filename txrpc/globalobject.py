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
from typing import Dict, List, Any, Union

from txrpc.distributed.manager import RemoteUnFindedError
from txrpc.distributed.node import RemoteObject
from txrpc.distributed.root import PBRoot
from txrpc.service.service import Service
from loguru import logger
from txrpc.utils.singleton import Singleton

class GlobalObject(metaclass=Singleton):
    
    def __init__(self):
        self.config = {}  # 配置信息
        self.remote_map : Dict[str:RemoteObject] = {}  # REMOTE 节点组
        # self.root : Union[PBRoot,None] = None # 当前连接的root节点
        
        self.node = None  # 当前节点实例
        self.masterremote = None  # 当前连接的master节点
        self.webapp = None # 当前挂载的web服务
        
    def get_config_from_object(self,obj):
        '''
            从对象中获取配置
        :param obj:
        :return:
        '''
        for key in dir(obj):
            if key.isupper():
                self.config[key] = getattr(obj, key)
        return self.config
    
    def getRemote(self,remote_name:str)->RemoteObject:
        '''
            根据节点名称获取节点实例
        :param remote_name: 节点名称
        :return:
        '''
        remote_obj = self.remote_map.get(remote_name)
        if remote_obj:
            return remote_obj
        else:
            raise RemoteUnFindedError
    
    def set(self,name,value):
        '''
            设置属性
        :param name:
        :param value:
        :return:
        '''
        setattr(self, name, value)
    
    def get(self,name,default):
        '''
            获取属性
        :param name: 名称
        :param default: 默认
        :return:
        '''
        return getattr(self,name,default)
        
def rootserviceHandle(target):
    """
        注册函数到root节点,供给root节点调用
    :param target: 函数
    :return:
    """
    GlobalObject().node.pbRoot.service.mapTarget(target)

class remoteserviceHandle:
    """
    该装饰器类，使用方法：
        def func:
            ...
        绑定成功后，root 可以调用 该 remote func 方法
    """
    def __init__(self,remotename):
        """
            远端节点的名称
        :param remotename:
        """
        self.remotename = remotename

    def __call__(self,target):
        """
        
        :param target:
        :return:
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

