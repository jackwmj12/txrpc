
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
from twisted.internet import reactor
from txrpc.distributed.reference import ProxyReference
from txrpc.service.service import Service
from txrpc.utils import logger


class RemoteObject(object):
    '''远程调用对象'''
    
    def __init__(self,name):
        '''初始化远程调用对象
        @param port: int 远程分布服的端口号
        @param rootaddr: 根节点服务器地址
        '''
        self._name = name
        self._weight = 10
        self._factory = pb.PBClientFactory() # pb的客户端，客户端可以执行server端的remote方法
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
        return self._weight
    
    def setWeight(self,weight):
        self._weight = weight
        
    def connect(self,addr):
        '''初始化远程调用对象'''
        self._addr = addr
        reactor.connectTCP(addr[0], addr[1], self._factory)
        self.takeProxy()
        
    def reconnect(self):
        '''重新连接'''
        self.connect(self._addr)
        
    def addServiceChannel(self,service):
        '''设置引用对象'''
        self._reference.addService(service)
    
    def takeProxy(self):
        '''
        向远程服务端发送代理通道对象
        '''
        deferedRemote = self._factory.getRootObject()
        deferedRemote.addCallback(_callRemote,'takeProxy',self._name,self._weight,self._reference).addCallback(self.doWhenConnect)
    
    def callRemote(self,commandId,*args,**kw):
        '''
        远程调用
        '''
        logger.debug("RPC : call <remote> method <{}>".format(commandId))
        deferedRemote = self._factory.getRootObject()
        return deferedRemote.addCallback(_callRemote,'callTarget',commandId,*args,**kw)
    
    def doWhenConnect(self,ign=None):
        '''
        :param
        '''
        self._doWhenConnect()
        
    def _doWhenConnect(self):
        '''
        :param
        '''
        for service in self.connectedService:
            self.connectedService.callTarget(service)
        
def _callRemote(obj:RemoteObject,funcName:str,*args,**kw):
    '''远程调用
    @param funcName: str 远程方法
    '''
    return obj.callRemote(funcName, *args,**kw)
    