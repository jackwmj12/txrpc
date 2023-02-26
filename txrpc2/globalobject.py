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
from typing import Dict, List, Any, Union, Callable
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

        ############################### 全局 ######################################################
        self.startService = Service("startservice")  # 程序开始时运行
        self.stopService = Service("endservice")  # 程序结束时运行(暂无实现)
        self.reloadService = Service("reloadservice")  # 程序重载时运行
        ################################################################################################

        ############################### leaf 节点 ######################################################
        self.leafNodeMap = {} # type: Dict[str,RPCClient]
        # 用于保存远程调用对象
        # LEAF 调用 ROOT 需要 通过 leafRemoteMap 中的对象进行调用
        self.leafRemoteMap = {}  # type: Dict[str,RemoteObject]
        self.leafConnectServiceMap: Dict[str: Service] = {} # leaf 节点 成功连接 ROOT 时在 LEAF 节点 运行
        self.leafLostConnectServiceMap: Dict[str: Service] = {} # leaf 节点 与 ROOT 断开 时运行
        ################################################################################################

        ############################### root 节点 ######################################################
        # 用于保存ROOT对象
        # ROOT 调用 LEAF 通过该对象调用
        self.root = None  # type: RPCServer
        self.rootRecvConnectService = Service("root_recv_connect_service") # leaf 节点成功连入时调用
        self.rootLostConnectService = Service("root_lost_connect_service") # leaf 节点断开连接时调用
        ################################################################################################

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
        return self.leafRemoteMap.get(name) # type: RemoteObject

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
        return GlobalObject().getRoot().pbRoot.rootCallLeafByName(leafName, functionName, *args, **kwargs)

    def callLeafByID(self, leafID: str, functionName: str, *args, **kwargs):
        '''
            调用子节点挂载的函数
        :param leafName:    远程分支节点名称
        :param functionName:    方法名称
        :param args:    参数
        :param kwargs:  参数
        :return:
        '''
        return GlobalObject().getRoot().pbRoot.rootCallLeafByID(leafID, functionName, *args, **kwargs)

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

def startServiceHandle(target: Callable):
    """
        注册程序启动时触发的函数的 Handler
    :param target: 函数
    :return:
    """
    GlobalObject().startService.mapFunction(target)

def stopServiceHandle(target: Callable):
    """
        注册程序停止时触发的函数的 Handler
    :param target: 函数
    :return:
    """
    GlobalObject().stopService.mapFunction(target)

def reloadServiceHandle(target):
    """
        注册程序重载时触发的函数的 Handler
    :param target: 函数
    :return:
    """
    GlobalObject().reloadService.mapFunction(target)

def leafConnectHandle(target):
    """
        被该装饰器装饰的函数
            会在 leaf 节点和 root 节点连接建立时,在root节点触发
    :param target: 函数
    :return:
    """
    GlobalObject().rootRecvConnectService.mapFunction(target)

def leafLostConnectHandle(target):
    """
        被该装饰器装饰的函数
            会在 leaf 节点和 root 节点连接断开时,在root节点触发
    :param target: 函数
    :return:
    """
    GlobalObject().rootLostConnectService.mapFunction(target)

class connectRootHandle:
    '''
        被该装饰器装饰的函数
            会在 leaf 节点和 root 节点连接建立时,在 leaf<name> 节点触发
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
        if not GlobalObject().leafConnectServiceMap.get(self.name):
            GlobalObject().leafConnectServiceMap[self.name] = Service(f"leaf_connect_service_{self.name}")  # rpc连接成功时运行
        GlobalObject().leafConnectServiceMap.get(self.name).mapFunction(target)

class lostConnectRootHandle:
    '''
            被该装饰器装饰的函数
        会在 leaf 节点和 root 节点连接断开时,在 leaf<name> 节点触发
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

def rootServiceHandle(target):
    """
        注册函数到 本地 RootNode
            所有注册到本地 RootNode 的函数, 都将暴露给 远端 LeafNode
            供给 LeafNode 调用
    :param target: 函数
    :return:
    """
    if not GlobalObject().root.pbRoot.rootService:
        service = Service(name = GlobalObject().root.getName())
        GlobalObject().root.pbRoot.rootAddServiceChannel(service)
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
        assert GlobalObject().getRemoteObject(self.name) != None, f"请检查 <{self.name}> 节点是否正常运行"
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

