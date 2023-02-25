
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
    节点相关
'''

from twisted.spread import pb
from twisted.internet import defer
from typing import Dict, Union

from txrpc2.distributed.reference import ProxyReference
from txrpc2.globalobject import GlobalObject
from txrpc2.service.service import CommandService
from loguru import logger

class RpcClientFactory(pb.PBClientFactory):

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def clientConnectionLost(self, connector, reason, reconnecting=0):
        super().clientConnectionLost(connector, reason, reconnecting)
        deferList = []
        for service in GlobalObject().lostConnectRootMap.get(self.name, None):
            deferList.append(GlobalObject().lostConnectRootMap.get(self.name).callFunction(service))
        return defer.DeferredList(deferList, consumeErrors=True)
    
    def clientConnectionMade(self, broker):
        super().clientConnectionMade(broker)
        deferList = []
        for service in GlobalObject().connectRootMap.get(self.name, None):
            deferList.append(GlobalObject().connectRootMap.get(self.name).callFunction(service))
        return defer.DeferredList(deferList, consumeErrors=True)

class RemoteObject(object):
    '''远程调用对象'''
    
    def __init__(self,name):
        '''初始化远程调用对象
        @param port: int 远程分布服的端口号
        @param rootaddr: 根节点服务器地址
        '''
        self._id = ""
        self._name = name
        self._weight: int = 10
        self._factory = RpcClientFactory(name) # pb的客户端，客户端可以执行server端的remote方法
        self._reference = ProxyReference()  # 创建代理通道，该通道包含添加服务，代理发送数据功能
        self._addr: Union[str,None] = None
        # self._config: Dict = {}
        # self.connectedService = CommandService("connected_service")

    def __str__(self):
        if  not self._id :
            return self._name
        return ":".join([self._name, self._id])

    def __repr__(self):
        if  not self._id :
            return self._name
        return ":".join([self._name,self._id])

    def getName(self):
        '''获取节点的名称'''
        return self._name

    def setName(self,name: str) -> "RemoteObject":
        '''设置节点的名称'''
        self._name = name
        return self

    def setID(self, id: str) -> "RemoteObject":
        self._id = id
        return self

    def getID(self):
        return self._id

    def getRemoteName(self):
        return ":".join([self._name,self._id])

    def getWeight(self):
        '''
            获取节点权重
        :return:
        '''
        return self._weight
    
    def setWeight(self,weight) -> "RemoteObject":
        '''
            设置节点权重
        :param weight:
        :return:
        '''
        self._weight = weight
        return self

    # def setConfig(self, **kwargs) -> "RemoteObject":
    #     self._config = kwargs
    #     return self

    # def getConfig(self) -> Dict:
    #     return self._config

    def connect(self,addr) -> defer.Deferred:
        '''
            初始化 并连接 root 节点
        '''
        from twisted.internet import reactor
        
        self._addr = addr
        reactor.connectTCP(addr[0], addr[1], self._factory)
        # 将 远程函数 代理给 ROOT 节点
        return self.takeProxy()
        
    def reconnect(self):
        '''
            重新连接
        '''
        self.connect(self._addr)
        
    def addServiceChannel(self,service):
        '''
            设置引用对象
        '''
        self._reference.addService(service)
    
    def takeProxy(self) -> defer.Deferred:
        '''
            向远程服务端发送代理通道对象
        '''
        deferedRemote = self._factory.getRootObject()
        return deferedRemote.addCallback(_callRemote,'takeProxy',self._name,self._weight,self._reference)
    
    def callRemote(self,commandId,*args,**kw):
        '''
            远程调用
        '''
        logger.debug(f"RPC : call <remote> method <{commandId}> with args = {args} kwargs = {kw}")
        deferedRemote = self._factory.getRootObject()
        return deferedRemote.addCallback(_callRemote,'callFunction',commandId,*args,**kw)
    
    # def doWhenConnect(self,ign=None):
    #     '''
    #         连接成功后触发
    #         :param
    #     '''
    #     self._doWhenConnect()
    #
    # def _doWhenConnect(self):
    #     '''
    #         连接成功后触发
    #     :param
    #     '''
    #     for service in self.connectedService:
    #         self.connectedService.callFunction(service)
        
def _callRemote(obj:RemoteObject,funcName:str,*args,**kw):
    '''
    远程调用
    @param funcName: str 远程方法
    '''
    return obj.callRemote(funcName, *args,**kw)
    