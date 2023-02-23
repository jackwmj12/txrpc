
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
    pb服务器
'''
from twisted.internet import defer
from twisted.internet.defer import Deferred
from twisted.spread import pb
from txrpc2.distributed.child import ChildNode
from txrpc2.distributed.manager import NodeManager
from txrpc2.service.service import CommandService, Service
from loguru import logger

class BilateralBroker(pb.Broker):
    '''

    '''
    def connectionLost(self, reason):
        clientID = self.transport.sessionno
        d = self.factory.root.dropChildById(clientID)
        d.addCallback(lambda ign : pb.Broker.connectionLost(self, reason))

class BilateralFactory(pb.PBServerFactory):
    
    protocol = BilateralBroker

class PBRoot(pb.Root):
    '''PB 代理服务器'''
    
    def __init__(self,dnsmanager = NodeManager()):
        '''
            初始化根节点
        '''
        self.dnsmanager: NodeManager = dnsmanager
        self.service: Service
        self.childConnectService = Service("child_connect_service")
        self.childLostConnectService = Service("child_lost_connect_service")
        
    def addServiceChannel(self,service : Service):
        '''
            添加服务通道
        @param service: Service Object(In bilateral.services)
        '''
        self.service: Service = service

    def doChildConnect(self,name,transport) -> Deferred:
        """
            当node节点连接时的处理
        :param name: 子节点名称
        :param transport:  子节点句柄
        :return:
        """
        defer_list = []
        try:
            logger.debug("node [%s] connect" % name)
            for service in self.childConnectService:
                # 遍历注册的 子节点连接服务(函数)并调用
                defer_list.append(
                    self.childConnectService.callFunction(service,name,transport)
                )
        except Exception as e:
            logger.error(str(e))
        return defer.DeferredList(defer_list,consumeErrors=True)
            
    def doChildLostConnect(self,childId) -> Deferred:
        """
            当node节点断开时的处理
        :param childId:  子节点ID
        :return:
        """
        defer_list = []
        try:
            logger.debug("node [%s] lose" % childId)
            for service in self.childLostConnectService:
                # 遍历注册的 子节点断开连接服务(函数)并调用
                defer_list.append(self.childLostConnectService.callFunction(service,childId))
        except Exception as e:
            logger.error(str(e))
        return defer.DeferredList(defer_list, consumeErrors=True)

    def dropChild(self,*args,**kw):
        '''
            删除子节点记录
        '''
        self.dnsmanager.dropChild(*args,**kw)
        
    def dropChildById(self,childId) -> Deferred:
        '''
            根据ID删除子节点记录
        :param childId:
        :return:
        '''
        if self.dnsmanager.dropChildById(childId):
            return self.doChildLostConnect(childId)
        else:
            return self.doChildLostConnect(None)
    
    def callChildByName(self,childname,*args,**kw)->Deferred:
        '''
            通过节点组名称调用子节点的接口,节点管理器会根据权重随机调用节点
        @param childname: str 子节点组的名称
        '''
        return self.dnsmanager.callChildByName(childname,*args,**kw)
    
    def callChildById(self,childId,*args,**kw)->Deferred:
        '''
            通过子节点的唯一ID调用子节点的接口
        @param childId: int 子节点的id
        return Defered Object
        '''
        return self.dnsmanager.callChildById(childId,*args,**kw)
    
    def remote_takeProxy(self,name,weight,transport):
        '''
            设置代理通道
            子节点和根节点建立连接后,通过该remote函数,设置并提交代理通道
            后续根节点通过该代理通道进行子节点调用
        @param addr: (hostname,port)hostname 根节点的主机名,根节点的端口
        '''
        logger.debug('node [%s] takeProxy ready' % (name))
        child = ChildNode(transport.broker.transport.sessionno,name)
        child.setWeight(weight)
        child.setTransport(transport)
        self.dnsmanager.addChild(child)
        return self.doChildConnect(name,transport)
        
    def remote_callFunction(self, command, *args, **kw):
        '''
            远程调用方法
            子节点通过该remote函数,进行root节点的服务调用
        @param commandId: 指令号
        @param data: str 调用参数
        '''
        data = self.service.callFunction(command, *args, **kw)
        return data