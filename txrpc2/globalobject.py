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

from txrpc2.distributed.manager import RemoteUnFindedError, LocalUnFindedError
from txrpc2.distributed.node import RemoteObject
from txrpc2.distributed.root import PBRoot
from txrpc2.service.service import Service
from loguru import logger
from txrpc2.utils.singleton import Singleton

class GlobalObject(metaclass=Singleton):
    
    def __init__(self):
        '''
            一个 RPC 服务仅能创建一个 ROOT 节点
                ROOT 节点上的所有函数,都将暴露给连接上来的 LEAF 节点,供给给他们调用
            一个 RPC 服务器可以创建无数个 LEAF 节点
                LEAF 节点会提供 LEAF 节点装饰过的remote方法给 ROOT 节点调用
        '''
        self.config = {}  # 配置信息
        self.remoteMap: Dict[str, RemoteObject] = {} # 远程 RPC 节点信息
        # self.remoteRoots: Dict[str: RemoteObject] = {} # 远程 RPC 根节点
        self.masterRoot: RemoteObject = None # 远程 MASTER RPC 节点
        self.root = None # type: RPCServer
        self.leafMap = {} # type: Dict[str,RPCClient]

    def getRoot(self):
        '''
            根据节点名称获取本地根节点实例
        :param name: 节点名称
        :return:
        '''
        return self.root

    def getLeaf(self, name: str):
        '''

        :param name:
        :return:
        '''
        return self.leafMap.get(name)

    def getRemote(self, name: str) -> RemoteObject:
        '''
            根据节点名称获取节点实例
        :param name: 节点名称
        :return:
        '''
        remoteObj = self.remoteMap.get(name)
        if remoteObj:
            return remoteObj
        else:
            raise RemoteUnFindedError

    def getRemoteConfig(self, name: str) -> Dict:
        remoteObj = self.remoteMap.get(name)
        if remoteObj:
            return remoteObj.getConfig()
        else:
            raise RemoteUnFindedError

    def addRemoteObject(self, name: str, id: str):
        '''

        :param name:
        :param id:
        :return:
        '''
        remoteName = ":".join([name,id])
        remoteObject = RemoteObject(remoteName)
        self.remoteMap[remoteName] = remoteObject
        return remoteObject

    def getRemoteObject(self, name: str, id: str) -> Union[RemoteObject,None]:
        '''

        :param name:
        :param id:
        :return:
        '''
        remoteName = ":".join([name, id])
        return self.remoteMap.get(remoteName,None)

    # def getRemoteRoot(self, name:str) -> RemoteObject:
    #     '''
    #         根据节点名称获取节点实例
    #     :param name: 节点名称
    #     :return:
    #     '''
    #     remote_obj = self.remoteRoots.get(name)
    #     if remote_obj:
    #         return remote_obj
    #     else:
    #         raise RemoteUnFindedError

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

def rootServiceHandle(target):
    """
        注册函数到 本地 RootNode
            所有注册到本地 RootNode 的函数, 都将暴露给 远端LeafNode
            供给 LeafNode 调用
    :param target: 函数
    :return:
    """
    GlobalObject().root.pbRoot.service.mapFunction(target)

class remoteServiceHandle:
    '''
        从 remoteRoots 中获取 指定 远端 RootNode
            并将被装饰的方法暴露给 远端 RootNode
            给予 远端 RootNode 调用
    '''
    def __init__(self,name):
        """
            rootNode 的名称
        :param name
        """
        self.name = name

    def __call__(self,target):
        """

        :param target:
        :return:
        """
        logger.debug(f"remoteServiceHandle <{self.name}>")
        GlobalObject().getRemote(self.name)._reference._service.mapFunction(target)

localservice = Service('localservice')

def localserviceHandle(target):
    '''
    创建本地服务装饰器
    被该装饰器装饰的函数
    可以且仅可以被本地使用
    @param target: func Object
    '''
    localservice.mapFunction(target)

