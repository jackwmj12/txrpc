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
from typing import Dict, List, Any, Union, Optional, Callable
from txrpc.service.service import Service
from loguru import logger
from txrpc.utils.singleton import Singleton

class GlobalObject(metaclass=Singleton):
    
    def __init__(self):
        '''
            一个 RPC 服务仅能创建一个 ROOT 节点
                ROOT 节点上的所有函数,都将暴露给连接上来的 LEAF 节点,供给给他们调用
            一个 RPC 服务器可以创建无数个 LEAF 节点
                LEAF 节点会提供 LEAF 节点装饰过的remote方法给 ROOT 节点调用
        '''
        self.config = {}  # 配置信息

        ############################### 全局 ######################################################
        self.startService = Service("startservice")  # 程序开始时运行
        self.stopService = Service("endservice")  # 程序结束时运行(暂无实现)
        self.reloadService = Service("reloadservice")  # 程序重载时运行
        ################################################################################################

        ############################### leaf 节点 ######################################################
        self.leaf = None  # type: RPCClient     # 用于保存LEAF对象
        self.leafRemoteMap = {}  # type: Dict[str,RemoteObject]     # 用于保存远程调用对象
        self.leafConnectSuccessServiceMap: Dict[str: Service] = {}  # leaf 节点 连接 ROOT 成功 时在 LEAF 节点 运行
        self.leafConnectFailedServiceMap: Dict[str: Service] = {}  # leaf 节点 连接 ROOT 失败 时在 LEAF 节点 运行
        self.leafLostConnectServiceMap: Dict[str: Service] = {}  # leaf 节点 与 ROOT 断开 时运行
        ################################################################################################

        ############################### root 节点 ######################################################
        self.root = None  # type: RPCServer # 用于保存ROOT对象
        self.rootRemoteMap = {}  # type: Dict[str,RemoteObject] # 用于保存远程调用对象
        self.rootRecvConnectService = Service("root_recv_connect_service") # leaf 节点成功连入时调用
        self.rootLostConnectService = Service("root_lost_connect_service") # leaf 节点断开连接时调用
        ################################################################################################

        ############################### master 节点 ######################################################
        self.masterremote = None  # type: # RemoteObject
        ################################################################################################

    def getRoot(self):
        return self.root # type: RPCServer

    def getLeaf(self):
        return self.leaf  # type: RPCClient

    def getLeafRemoteObject(self, name: str):
        '''
            root 节点中 获取 远端 leaf 节点对象
        :return:
        '''
        return self.leafRemoteMap.get(name) # type: RemoteObject

    def getRootRemoteObject(self, name: str):
        '''
            leaf 节点中 获取 远端 root 节点对象
        :return:
        '''
        return self.rootRemoteMap.get(name) # type: RemoteObject

    def callRoot(self, remoteName: str, functionName: str, *args, **kwargs):
        '''
            调用远端Root节点
        :param remoteName:  节点名称
        :param functionName:  函数名称
        :param args:  参数1
        :param kwargs:  参数2
        :return:
        '''
        return GlobalObject().getRootRemoteObject(remoteName).callRemote(functionName, *args, **kwargs)

    def callLeaf(self, leafName: str, functionName: str, *args, **kwargs):
        '''
            调用子节点挂载的函数
        :param leafName:    远程分支节点名称
        :param functionName:    方法名称
        :param args:    参数
        :param kwargs:  参数
        :return:
        '''
        return GlobalObject().getRoot().pbRoot.callLeafByName(leafName, functionName, *args, **kwargs)

    def callLeafByID(self, leafID: str, functionName: str, *args, **kwargs):
        '''
            调用子节点挂载的函数
        :param leafName:    远程分支节点名称
        :param functionName:    方法名称
        :param args:    参数
        :param kwargs:  参数
        :return:
        '''
        return GlobalObject().getRoot().pbRoot.callLeafByID(leafID, functionName, *args, **kwargs)

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
        通常于 root 节点上调用
        将函数注册到 root 节点 ,进而暴露给所有 leaf 节点 以供 leaf 节点调用
    :return:
    """
    if not GlobalObject().root.pbRoot.rootService:
        service = Service(name = GlobalObject().root.getName())
        GlobalObject().root.pbRoot.addServiceChannel(service)
    GlobalObject().root.pbRoot.rootService.mapFunction(target)

class remoteServiceHandle:
    '''
        通常于 leaf 节点上调用
        将被装饰的方法暴露给 远端 root<name> 节点以供 root<name> 节点调用
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
        assert GlobalObject().getLeafRemoteObject(self.name) != None, f"请检查 <{self.name}> 节点是否正常运行"
        GlobalObject().getLeafRemoteObject(self.name)._reference._service.mapFunction(target)

localservice = Service('localservice')

def localserviceHandle(target):
    '''
        创建本地服务装饰器
        被该装饰器装饰的函数
        可以且仅可以被本地随时随地使用
        @param target: func Object
    '''
    localservice.mapFunction(target)

def startServiceHandle(target: Callable):
    """
        注册程 序启动时触发 的函数的 Handler
    :param target: 函数
    :return:
    """
    GlobalObject().startService.mapFunction(target)

def stopServiceHandle(target: Callable):
    """
        注册 程序停止时触发 的函数的 Handler
    :param target: 函数
    :return:
    """
    GlobalObject().stopService.mapFunction(target)

def reloadServiceHandle(target):
    """
        注册 程序重载时触发 的函数的 Handler, 一般用于master节点回调
    :param target: 函数
    :return:
    """
    GlobalObject().reloadService.mapFunction(target)

def rootWhenLeafConnectHandle(target):
    """
        被该装饰器装饰的函数
            会在 leaf 节点和 root 节点连接建立时, 在root节点触发
    :param target: 函数
    :return:
    """
    GlobalObject().rootRecvConnectService.mapFunction(target)

def rootWhenLeafLostConnectHandle(target):
    """
        被该装饰器装饰的函数
            会在 leaf 节点和 root 节点连接断开时,在root节点触发
    :param target: 函数
    :return:
    """
    GlobalObject().rootLostConnectService.mapFunction(target)

class LeafConnectRootSuccessHandle:
    '''
        被该装饰器装饰的函数
            会在 leaf 节点和 root<name> 节点连接建立时,在 leaf 节点触发
    '''
    def __init__(self, name):
        """
        :param name root 节点名称
        """
        self.name = name

    def __call__(self,target):
        """

        :param target:
        :return:
        """
        if not GlobalObject().leafConnectSuccessServiceMap.get(self.name):
            GlobalObject().leafConnectSuccessServiceMap[self.name] = Service(f"leaf_connect_success_service_{self.name}")  # rpc连接成功时运行
        GlobalObject().leafConnectSuccessServiceMap.get(self.name).mapFunction(target)

class LeafLostConnectRootHandle:
    '''
        被该装饰器装饰的函数
            会在 leaf 节点和 root<name> 节点连接断开时,在 leaf 节点触发
    '''
    def __init__(self,name):
        """

        :param name
        """
        self.name = name

    def __call__(self,target):
        """

        :param target:
        :return:
        """
        if not GlobalObject().leafLostConnectServiceMap.get(self.name):
            GlobalObject().leafLostConnectServiceMap[self.name] = Service(f"leaf_lost_connect_service_{self.name}")  # rpc连接成功时运行
        GlobalObject().leafLostConnectServiceMap.get(self.name).mapFunction(target)

class LeafConnectRootFailedHandle:
    '''
        被该装饰器装饰的函数
            会在 leaf 节点和 root<name> 节点连接建立失败时,在 leaf 节点触发
    '''
    def __init__(self,name):
        """

        :param name
        """
        self.name = name

    def __call__(self,target):
        """

        :param target:
        :return:
        """
        if not GlobalObject().leafConnectFailedServiceMap.get(self.name):
            GlobalObject().leafConnectFailedServiceMap[self.name] = Service(f"leaf_connect_failed_service_{self.name}")  # rpc连接成功时运行
        GlobalObject().leafConnectFailedServiceMap.get(self.name).mapFunction(target)


