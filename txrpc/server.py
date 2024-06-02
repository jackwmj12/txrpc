# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
# @Time     : 2021-02-20 21:16
# @Software : txrpc
# @Email    : jackwmj12@163.com
# @Github   : 
# @Desc     : 
#            ┏┓      ┏┓
#          ┏┛┻━━━┛┻┓
#          ┃      ━      ┃
#          ┃  ┳┛  ┗┳  ┃
#          ┃              ┃
#          ┃      ┻      ┃
#          ┗━┓      ┏━┛
#              ┃      ┃
#              ┃      ┗━━━┓
#              ┃              ┣┓
#              ┃              ┏┛
#              ┗┓┓┏━┳┓┏┛
#                ┃┫┫  ┃┫┫
#                ┗┻┛  ┗┻┛
#                 神兽保佑，代码无BUG!
#
#
#
from loguru import logger

from txrpc.core import RPC
from txrpc.distributed.root import BilateralFactory, PBRoot
from txrpc.globalobject import GlobalObject


class RPCServer(RPC):
    '''
    :return
    '''

    def __init__(self, name: str, service_path = None, port=None):
        '''
            RPC 服务端
        :param name: 服务端名字
        :param service_path: 服务路径
        :param port: 服务端port
        '''
        # root对象监听制定端口
        super(RPCServer,self).__init__(name=name)
        if not service_path:
            self.servicePath = GlobalObject().config.get("DISTRIBUTED").get(name).get("APP")

        if not port:
            port = int(GlobalObject().config.get("DISTRIBUTED").get(name).get("PORT"))

        self.pbRoot = PBRoot()
        from twisted.internet import reactor
        reactor.listenTCP(port, BilateralFactory(self.pbRoot))
        # 注册服务
        self.registerService(self.servicePath)

    # @staticmethod
    # def callRemote(remoteName: str, functionName: str, *args, **kwargs):
    #     '''
    #         调用子节点挂载的函数
    #     :param remoteName:  远程分支节点名称
    #     :param functionName: 方法名称
    #     :param args:  参数
    #     :param kwargs:  参数
    #     :return:
    #     '''
    #     return GlobalObject().callLeaf(remoteName, functionName, *args, **kwargs)
    #
    # @staticmethod
    # def callRemoteByID(remoteID: str, functionName: str, *args, **kwargs):
    #     '''
    #         调用子节点挂载的函数
    #     :param remoteID:  远程分支节点ID
    #     :param functionName: 方法名称
    #     :param args:  参数
    #     :param kwargs:  参数
    #     :return:
    #     '''
    #     return GlobalObject().callLeafByID(remoteID, functionName, *args, **kwargs)