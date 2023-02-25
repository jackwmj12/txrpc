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
        # self.remoteLeaf: Dict[str, RemoteObject] = {} # 远程 RPC 子节点信息
        # self.remoteRoot: Dict[str, RemoteObject] = {}  # 远程 RPC 根节点信息
        # self.masterRoot: RemoteObject = None # 远程 MASTER RPC 节点

        self.remoteMap: Dict[str, RemoteObject] = {}
        # 用于保存远程调用对象,
        # LEAF 调用 ROOT 需要 通过 RemoteMap 中的对象进行调用

        self.root = None # type: RPCServer
        # 用于保存ROOT对象
        # ROOT 调用 LEAF 通过该对象调用
        self.leafNodeMap = {} # type: Dict[str,RPCClient]

    def getRoot(self): #
        '''
            根据节点名称获取本地根节点实例
        :param name: 节点名称
        :return:
        '''
        return self.root # type: RPCServer

    def getLeaf(self, name: str):
        '''

        :param name:
        :return:
        '''
        return self.leafNodeMap.get(name) # type: Dict[str,RPCClient]

    def getRemoteObject(self, name: str):
        '''

        :return:
        '''
        return self.remoteMap.get(name)

    # def getRemoteConfig(self, remoteName: str) -> Dict:
    #     remoteObj = self.getRemote(remoteName)
    #     if remoteObj:
    #         return remoteObj.getConfig()
    #     else:
    #         raise RemoteUnFindedError
    #
    # def addRootRemoteObject(self, name: str, id: str = None):
    #     '''
    #
    #     :param name:
    #     :param id:
    #     :return:
    #     '''
    #     remoteObject = RemoteObject(name)
    #     self.remoteLeaf[name] = remoteObject
    #     return remoteObject
    #
    # def addLeafRemoteObject(self, name: str, id: str = None):
    #     '''
    #
    #     :param name:
    #     :param id:
    #     :return:
    #     '''
    #     remoteName = ":".join([name,id])
    #     remoteObject = RemoteObject(remoteName)
    #     self.remoteLeaf[remoteName] = remoteObject
    #     return remoteObject
    #
    # def getRemoteObject(self, remoteName: str) -> RemoteObject:
    #     '''
    #         根据节点名称获取节点实例
    #     :param name: 节点名称
    #     :return:
    #     '''
    #     remoteObj = self.remoteLeaf.get(remoteName)
    #     if remoteObj:
    #         return remoteObj
    #     else:
    #         remoteObj = self.remoteRoot.get(remoteName)
    #         if remoteObj:
    #             return remoteObj
    #     raise RemoteUnFindedError
    #
    # def getRootRemoteObject(self, name: str) -> Union[RemoteObject,None]:
    #     '''
    #
    #     :param name:
    #     :param id:
    #     :return:
    #     '''
    #     remote_obj = self.remoteRoot.get(name)
    #     if remote_obj:
    #         return remote_obj
    #     else:
    #         raise RemoteUnFindedError
    #
    # def getLeafRemoteObject(self, name: str, id: str) -> Union[RemoteObject,None]:
    #     '''
    #
    #     :param name:
    #     :param id:
    #     :return:
    #     '''
    #     remoteName = ":".join([name, id])
    #     return self.remoteLeaf.get(remoteName,None)

    def callRoot(self, remoteName: str, functionName: str, *args, **kwargs):
        '''
            调用远端Root节点
        :param remoteName:  节点名称
        :param functionName:  函数名称
        :param args:  参数1
        :param kwargs:  参数2
        :return:
        '''
        return GlobalObject().getRemoteObject(remoteName).callRemote(functionName, *args, **kwargs)

    def callLeaf(self, leafName: str, functionName: str, *args, **kwargs):
        '''
            调用子节点挂载的函数
        :param leafName:    远程分支节点名称
        :param functionName:    方法名称
        :param args:    参数
        :param kwargs:  参数
        :return:
        '''
        return GlobalObject().getRoot().pbRoot.callNodeChildByName(leafName, functionName, *args, **kwargs)

    def callLeafByID(self, leafID: str, functionName: str, *args, **kwargs):
        '''
            调用子节点挂载的函数
        :param leafName:    远程分支节点名称
        :param functionName:    方法名称
        :param args:    参数
        :param kwargs:  参数
        :return:
        '''
        return GlobalObject().getRoot().pbRoot.callNodeChildByID(leafID, functionName, *args, **kwargs)

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
    if not GlobalObject().root.pbRoot.rootService:
        service = Service(name = GlobalObject().root.getName())
        GlobalObject().root.pbRoot.addRootServiceChannel(service)
    GlobalObject().root.pbRoot.rootService.mapFunction(target)

class remoteServiceHandle:
    '''
        从 remoteLeaf 中获取 指定 远端 RootNode
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
        GlobalObject().getRemoteObject(self.name)._reference._service.mapFunction(target)

localservice = Service('localservice')

def localserviceHandle(target):
    '''
        创建本地服务装饰器
        被该装饰器装饰的函数
        可以且仅可以被本地使用
        @param target: func Object
    '''
    localservice.mapFunction(target)

