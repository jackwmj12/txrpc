import logging
import os
import socket
import sys

from twisted.python.logfile import DailyLogFile

from txrpc.utils.logger import LevelFileLogObserver
from typing import List, Dict, Any

from twisted.internet import reactor

from txrpc.distributed.node import RemoteObject
from txrpc.distributed.root import BilateralFactory, PBRoot
from txrpc.globalobject import GlobalObject
from txrpc.service import services
from txrpc.utils import delay_import, logger


class RPC():
    
    def __init__(self):
        '''
        :return
        '''
        if GlobalObject().starthandler:
            GlobalObject().starthandler()
    
    def run(self):
        '''
        :return
        '''
        reactor.run()
    
    def registerService(self, service_path : str):
        '''
        :return
        '''
        delay_import(service_path.split(","))

    def log_init(self):
        '''

        :return:
        '''
        # 初始化日志
        # GlobalObject().config["LOG_PATH"] = GlobalObject().base_dir + os.sep + "logs"
        
        if GlobalObject().config["LOG_PATH"]:
        
            logger.msg("初始化日志路径为：{}".format(GlobalObject().config["LOG_PATH"]))
    
            if os.path.isdir(GlobalObject().config.get("LOG_PATH")) == False:  # 设置生产日志路径
                os.mkdir(GlobalObject().config.get("LOG_PATH"))
            logger.FileLogObserver.timeFormat = '%Y-%m-%d %H:%M:%S'

            f = DailyLogFile(".".join([GlobalObject().config.get("LOG_NAME","txrpc").lower() , "log"]), GlobalObject().config.get("LOG_PATH"))
            logger.msg("当前为常规模式，设置日志路径，且将日志运行于每日分割模式")
        else:
            f = sys.stdout
            # f = DailyLogFile(self.name.lower() + ".log", GlobalObject().config.get("LOG_PATH"))
            logger.msg("当前未输入日志路径，设置日志为屏幕输出")
           
        log_level = GlobalObject().config.get("LOG_LEVEL", "DEBUG")
    
        if log_level.upper() == "DEBUG":
            log_observer = LevelFileLogObserver(f, logging.DEBUG)
        else:
            log_observer = LevelFileLogObserver(f, logging.INFO)
    
        logger.startLoggingWithObserver(log_observer.emit, setStdout=False)

    def twisted_init(self):
        '''
        # 初始化socket超时时间
        :param
        '''
    
        socket.setdefaulttimeout(GlobalObject().config.get("SOCKET_TIME_OUT", 60))
    
        logger.msg("初始化socket超时时间为：{}".format(GlobalObject().config.get("SOCKET_TIME_OUT", 60)))
    
        reactor.suggestThreadPoolSize(GlobalObject().config.get("TWISTED_THREAD_POOL", 8))  # 设置线程池数量
    
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
            self.registerService(service_path)

    def setDoWhenChildConnect(self,handler):
        GlobalObject().root.doChildConnect = handler
    
    def setDoWhenChildLostConnect(self,handler):
        GlobalObject().root.doChildLostConnect = handler

    @staticmethod
    def callRemote(remoteName: str, functionName: str, *args, **kwargs):
        '''
        :param
        '''
        return GlobalObject().root.callChildByName(remoteName, functionName, *args, **kwargs)

class RPCClient(RPC):
    '''
    :return
    '''
    
    def __init__(self):
        '''
        :return
        '''
        super().__init__()

    def _connectRemote(self, name: str, target_name: str, host: str, port: int,weight:int=10):
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
        remote.setWeight(weight)
        remote.connect((host, port))
        GlobalObject().remote[target_name] = remote
    
    def setDoWhenConnect(self, serverName : str,handler):
        '''
        :param
        '''
        GlobalObject().remote[serverName]._doWhenConnect = handler
    
    def clientConnect(self,name: str,target_name:str, host: str, port: int, service_path: str=None,weight=10):
        '''
        :param
        '''
        logger.debug("local<{name}> -> remote:<{target_name}>".format(name=name, target_name=target_name))

        self._connectRemote(name=name, target_name=target_name, host=host, port=port,weight=weight)

        if service_path:
            self.registerService(service_path)
        
        return self

    @staticmethod
    def callRemote(remoteName: str, functionName: str, *args, **kwargs):
        '''
        :param
        '''
        return GlobalObject().getRemote(remoteName).callRemote(functionName, *args, **kwargs)

def run():
    '''
    :return
    '''
    reactor.run()