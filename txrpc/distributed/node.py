
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
from txrpc.distributed.reference import ProxyReference
from txrpc.service.service import Service
from loguru import logger

class RpcClientFactory(pb.PBClientFactory):

    def setRemoteObject(self, remoteObject):
        setattr(self, "remoteObject", remoteObject)
        return self

    def getRemoteObject(self):
        return getattr(self, "remoteObject", None)

    def clientConnectionLost(self, connector, reason, reconnecting=0):
        super().clientConnectionLost(connector, reason, reconnecting)

        remote_obj = self.getRemoteObject()
        if remote_obj:
            return remote_obj.doWhenDisconnect()

    def clientConnectionFailed(self, connector, reason):
        super().clientConnectionFailed(connector, reason)

        remote_obj = self.getRemoteObject()
        if remote_obj:
            return remote_obj.doWhenConnectFailed()

    def clientConnectionMade(self, broker):
        super().clientConnectionMade(broker)

        remote_obj = self.getRemoteObject()
        if remote_obj:
            return remote_obj.doWhenConnect()

class RemoteObject(object):
    '''远程调用对象'''
    
    def __init__(self, name):
        '''初始化远程调用对象
        @param port: int 远程分布服的端口号
        @param rootaddr: 根节点服务器地址
        '''
        self._name = name
        self._weight = 10
        # pb的客户端，客户端可以执行server端的remote方法
        self._factory = RpcClientFactory().setRemoteObject(self)
        self._reference = ProxyReference()  # 创建代理通道，该通道包含添加服务，代理发送数据功能
        self._addr = None
        
        self.connectedService = Service("connected_service")
    
    def setName(self,name):
        '''设置节点的名称'''
        self._name = name
        
    def getName(self):
        '''获取节点的名称'''
        return self._name
        
    def getWeight(self):
        '''
            获取节点权重
        :return:
        '''
        return self._weight
    
    def setWeight(self,weight):
        '''
            设置节点权重
        :param weight:
        :return:
        '''
        self._weight = weight
        
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
        deferedRemote = self._factory.getRootObject()
        return deferedRemote.addCallback(
            _callRemote,'takeProxy',self._name,self._weight,self._reference
        )
    
    def callRemote(self,commandId,*args,**kw):
        '''
            远程调用
        '''
        logger.debug(f"RPC : call <remote> method <{commandId}> with args = {args} kwargs = {kw}")
        deferedRemote = self._factory.getRootObject()
        return deferedRemote.addCallback(_callRemote,'callTarget',commandId,*args,**kw)

    def doWhenConnect(self):
        '''
            连接成功后触发
            :param
        '''
        for service in self.connectedService:
            self.connectedService.callTarget(service)

    def doWhenDisconnect(self):
        '''
            连接成功后触发
            :param
        '''

    def doWhenConnectFailed(self):
        '''
            连接失败后触发
        :return:
        '''
        
def _callRemote(remoteObject: RemoteObject, funcName: str, *args, **kw):
    '''
    远程调用
    @param funcName: str 远程方法
    '''
    return remoteObject.callRemote(funcName, *args,**kw)
    