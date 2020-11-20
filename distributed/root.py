
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

from twisted.internet.defer import Deferred
from twisted.python import log
from twisted.spread import pb
from distributed.child import Child
from distributed.manager import ChildsManager

from service.services import Service
from utils import Log


class BilateralBroker(pb.Broker):
    
    def connectionLost(self, reason):
        clientID = self.transport.sessionno
        # Log.msg("node [%d] lose"%clientID)
        self.factory.root.dropChildSessionId(clientID)
        pb.Broker.connectionLost(self, reason)

class BilateralFactory(pb.PBServerFactory):
    
    protocol = BilateralBroker
    

class PBRoot(pb.Root):
    '''PB 代理服务器'''
    
    def __init__(self,dnsmanager = ChildsManager()):
        '''初始化根节点
        '''
        self._current_id = 0
        self.childsmanager : ChildsManager = dnsmanager
        self.service: Service
        
    def addServiceChannel(self,service : Service):
        '''添加服务通道
        @param service: Service Object(In bilateral.services)
        '''
        self.service : Service = service

    def doChildConnect(self,name,transport):
        """
        当node节点连接时的处理
        """
        Log.msg("{} connected".format(name))

    def doChildLostConnect(self,childId):
        """
        当node节点连接时的处理
        """
        Log.debug("{} lost connect".format(childId))
    
    # def addChild(self):
    #     self.childsmanager.addChild
    
    def dropChild(self,*args,**kw):
        '''删除子节点记录'''
        self.childsmanager.dropChild(*args,**kw)
        
    def dropChildByID(self,childId):
        '''删除子节点记录'''
        self.doChildLostConnect(childId)
        self.childsmanager.dropChildByID(childId)
        
    def dropChildSessionId(self, session_id):
        '''删除子节点记录'''
        child = self.childsmanager.getChildBYSessionId(session_id)
        if not child:
            return
        child_id = child._id
        self.doChildLostConnect(child_id)
        self.childsmanager.dropChildByID(child_id)

    def callChild(self,key,*args,**kw)->Deferred:
        '''调用子节点的接口
        @param childId: int 子节点的id
        return Defered Object
        '''
        return self.childsmanager.callChild(key,*args,**kw)
    
    def callChildByName(self,childname,*args,**kw)->Deferred:
        '''调用子节点的接口
        @param childId: int 子节点的id
        return Defered Object
        '''
        return self.childsmanager.callChildByName(childname,*args,**kw)
    
    def remote_takeProxy(self,name,transport):
        '''
        设置代理通道
        @param addr: (hostname,port)hostname 根节点的主机名,根节点的端口
        '''
        Log.debug('node [%s] takeProxy ready'%(name))
        child = Child(name,name)
        self.childsmanager.addChild(child)
        child.setTransport(transport)
        self.doChildConnect(name, transport)

    def remote_callTarget(self, command, *args, **kw):
        '''
        远程调用方法
        @param commandId: 指令号
        @param data: str 调用参数
        '''
        data = self.service.callTarget(command, *args, **kw)
        return data