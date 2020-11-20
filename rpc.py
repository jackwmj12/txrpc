from utils import Log
from typing import List, Dict, Any

from twisted.internet import reactor

from distributed.node import RemoteObject
from distributed.root import BilateralFactory, PBRoot
from globalobject import GlobalObject
from service import services
from utils import delay_import


def callRemote(remote_name:str, commandId, *args,**kw):
    '''

    :param remoteObj:
    :param commandId
    :param args
    :param kw
    :return:
    '''
    # raise Exception("callRemote method is not realize")
    # remoteObj.callRemote(commandId,*args,**kw)
    return GlobalObject().getRemote(remote_name).callRemote(commandId,*args,**kw)

def _doChildConnect(name, transport):
    '''
    :return
    '''
    try:
        Log.info("node [%s] connect" % name)
        # del GlobalObject().remote[childId]
    except Exception as e:
        Log.info(str(e))


def _doChildLostConnect(childId):
    """
        当节点与master断开时master的回调
    """
    try:
        Log.info("node [%s] lose" % childId)
        # del GlobalObject().remote[childId]
    except Exception as e:
        Log.info(str(e))


class RPC():
    
    def __init__(self):
        '''
        :return
        '''
        if GlobalObject().root:
            GlobalObject().root.doChildConnect = _doChildConnect
            GlobalObject().root.doChildLostConnect = _doChildLostConnect
    
    def run(self):
        '''
        :return
        '''
        reactor.run()
    
    def importService(self, filePath: List[str]):
        '''
        :return
        '''
        delay_import(filePath)
    
    def connectRemote(self, name: str, target_name:str,host: str, port: int):
        '''
            控制 节点 连接 另一个节点
            :param name:  当前节点名称
            :param remote_name:  需要连接的节点名称
            :return:
            '''
        assert name != None, "remote 名称不能为空"
        assert port != None, "port 不能为空"
        assert host != None, "host 不能为空"
        assert target_name != None, "target_name 不能为空"
        
        remote = RemoteObject(name)
        remote.connect((host, port))
        GlobalObject().remote[target_name] = remote
        # if not GlobalObject().remote[remote_name]:
        #     GlobalObject().remote[remote_name] = [remote]
        # else:
        #     GlobalObject().remote[remote_name].append(remote)
    
    def setDoWhenStop(self, handler):
        '''
        :return
        '''
        GlobalObject().stophandler = handler
    
    def setDoWhenStart(self, handler):
        '''
        :return
        '''
        GlobalObject().starthandler = handler
    
    def setDoWhenReload(self, handler):
        '''
        :return
        '''
        GlobalObject().reloadhandler = handler
    
    def setDoWhenChildConnect(self,handler):
        GlobalObject().root.doChildConnect = handler
    
    def setDoWhenChildLostConnect(self,handler):
        GlobalObject().root.doChildLostConnect = handler

class RPCServer(RPC):
    '''
    :return
    '''
    
    def __init__(self, name: str, port: int, service_path: str=None):
        '''
        :return
        '''
        # root对象监听制定端口
        super().__init__()
        
        GlobalObject().root = PBRoot()
        
        reactor.listenTCP(port, BilateralFactory(GlobalObject().root))
        
        service = services.Service(name=name)
        
        # 将服务添加到root
        GlobalObject().root.addServiceChannel(service)
        
        if service_path:
            self.importService(service_path.split(","))


class RPCClient(RPC):
    '''
    :return
    '''
    
    def __init__(self, name: str,target_name:str, host: str, port: int, service_path: str=None):
        '''
        :return
        '''
        super().__init__()
        
        Log.debug("本地节点{name} -> 远程节点:{target_name}".format(name=name,target_name=target_name))
        
        self.connectRemote(name=name,target_name=target_name,host=host, port=port)
        
        if service_path:
            self.importService(service_path.split(","))