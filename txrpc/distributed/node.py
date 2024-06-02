
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
from twisted.internet.defer import Deferred
from twisted.spread import pb
from twisted.internet import defer
from typing import Union

from twisted.spread.pb import RemoteReference

from txrpc.distributed.reference import ProxyReference
from txrpc.globalobject import GlobalObject
from loguru import logger

class RpcClientFactory(pb.PBClientFactory):

    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def clientConnectionLost(self, connector, reason, reconnecting=0):
        super().clientConnectionLost(connector, reason, reconnecting)
        deferList = []
        services = GlobalObject().leafLostConnectServiceMap.get(self.name, None)
        if services:
            for service in services:
                if service:
                    deferList.append(GlobalObject().leafLostConnectServiceMap.get(self.name).callFunctionEnsureDeferred(service))
        return defer.DeferredList(deferList, consumeErrors=True)

    def clientConnectionMade(self, broker):
        super().clientConnectionMade(broker)
        deferList = []
        services = GlobalObject().leafConnectSuccessServiceMap.get(self.name, None)
        if services:
            for service in services:
                if service:
                    deferList.append(GlobalObject().leafConnectSuccessServiceMap.get(self.name).callFunctionEnsureDeferred(service))
        return defer.DeferredList(deferList, consumeErrors=True)

    def clientConnectionFailed(self, connector, reason):
        super().clientConnectionFailed(connector, reason)
        deferList = []
        services = GlobalObject().leafConnectFailedServiceMap.get(self.name, None)
        if services:
            for service in services:
                if service:
                    deferList.append(GlobalObject().leafConnectFailedServiceMap.get(self.name).callFunctionEnsureDeferred(service))
        return defer.DeferredList(deferList, consumeErrors=True)

class RemoteObject(object):
    '''远程调用对象'''
    
    def __init__(self, nameOnRemote, remoteNameOnLocal = 'proxy'):
        '''初始化远程调用对象
        @param nameOnRemote:  本节点地址在
        @param remoteNameOnLocal: 根节点服务器地址
        '''
        self._id = ""
        self._name = remoteNameOnLocal
        self._name_on_remote = nameOnRemote
        self._weight: int = 10
        self._factory = RpcClientFactory(remoteNameOnLocal)  # pb的客户端，客户端可以执行server端的remote方法
        self._reference = ProxyReference(remoteNameOnLocal)  # 创建代理通道，该通道包含添加服务，代理发送数据功能
        self._addr: Union[str, None] = None

    def __str__(self):
        if not self._id:
            return f"RemoteObject<{self._name}>"
        return f"RemoteObject<{':'.join([self._name, self._id])}>"

    def __repr__(self):
        if not self._id :
            return f"RemoteObject<{self._name}>"
        return f"RemoteObject<{':'.join([self._name,self._id])}>"

    def getName(self):
        '''获取节点的名称'''
        return self._name

    def setName(self, name: str) -> "RemoteObject":
        '''设置节点的名称'''
        self._name = name
        return self

    def getID(self):
        return self._id

    def getWeight(self):
        '''
            获取节点权重
        :return:
        '''
        return self._weight

    def setWeight(self, weight):
        '''
            设置节点权重
        :param weight:
        :return:
        '''
        self._weight = weight

    def getRemoteName(self):
        return ":".join([self._name,self._id])

    def connect(self, addr) -> defer.Deferred:
        '''
            初始化并连接 server 节点
        '''
        from twisted.internet import reactor
        
        self._addr = addr
        reactor.connectTCP(addr[0], addr[1], self._factory)
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
        return self._factory.getRootObject().addCallback(
            _callRemote,'takeProxy',self._name_on_remote,self._weight,self._reference
        ).addErrback(logger.error)
    
    def callRemote(self,commandId, *args, **kw) -> Deferred:
        '''
            远程调用
        '''
        logger.debug(f"RPC : call <remote> method <{commandId}> with args = {args} kwargs = {kw}")
        d = self._factory.getRootObject()
        # logger.debug(f"callRemote<{commandId}> ======================> {d}|<{type(d)}>")
        d.addCallback(
            _callRemote, 'callFunction', commandId, *args, **kw
        ).addErrback(logger.error)
        # logger.debug(f"callRemote<{commandId}> ======================> {d}|<{type(d)}>")
        return d
        # return self._factory.getRootObject().addCallback(
        #     _callRemote,'callFunction',commandId, *args, **kw
        # ).addErrback(logger.error)
        
def _callRemote(remoteObject: RemoteObject, funcName: str, *args, **kw) -> Deferred:
    '''
    远程调用
    @param funcName: str 远程方法
    '''
    return remoteObject.callRemote(funcName, *args,**kw)
    