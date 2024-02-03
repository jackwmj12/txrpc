# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : client.py
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
from twisted.internet import defer

from txrpc.core import RPC
from txrpc.distributed.node import RemoteObject
from txrpc.globalobject import GlobalObject
from txrpc.service.service import Service
from loguru import logger


class RPCClient(RPC):
    '''
            RPC 客户端
    :return
    '''

    def __init__(self, name=None):
        '''

        :param name: 节点名称
        '''
        super(RPCClient, self).__init__(name=name)
        self.connectService = Service("connect_service")  # rpc服务连接成功时运行
        self.lostConnectService = Service("lost_connect_service")  # rpc服务连接断开时运行

    def clientConnect(self, name=None, host=None, port=None, weight=None):
        '''
                RPC客户端 主动连接 RPC服务端 节点
        :param name:  本节点名称
        :param host:  server节点host
        :param port:  server节点port
        :param weight:  本节点权重
        :param remote_service_path:  本节点服务地址
        :return:
        '''
        logger.debug("clientConnect ...")

        if not host:
            host = GlobalObject().config.get("DISTRIBUTED").get(
                self.name).get("REMOTE").get("HOST")

        if not port:
            port = int(
                GlobalObject().config.get("DISTRIBUTED").get(
                    self.name).get("REMOTE").get("PORT"))

        if not weight:
            weight = int(
                GlobalObject().config.get("DISTRIBUTED").get(
                    self.name).get("REMOTE").get(
                    "WEIGHT", 10))

        logger.debug(
            "local<{name}> -> remote:<{target_name}>".format(name=self.name, target_name=name))

        # self._connectRemote(name=self.name, target_name=name, host=host, port=port, weight=weight)

        assert name is not None, "local 名称不能为空"
        logger.debug("名称检查通过 ...")
        assert port is not None, "port 不能为空"
        logger.debug("port ...")
        assert host is not None, "host 不能为空"
        logger.debug("host ...")
        assert name is not None, "target_name 不能为空"
        logger.debug("target_name ...")

        remote = RemoteObject(name)
        remote.setWeight(weight)
        GlobalObject().remote_map[name] = remote
        d = remote.connect((host, port))
        d.addCallback(lambda ign: self._doWhenConnect())
        d.addCallback(
            lambda ign: self.registerService(
                self.remote_service_path))

        return self

    @staticmethod
    def callRemote(remoteName: str, functionName: str, *args, **kwargs):
        '''
                调用远端节点
        :param remoteName: 节点名称
        :param functionName:  函数名称
        :param args:  参数1
        :param kwargs:  参数2
        :return:
        '''
        return GlobalObject().getRemote(remoteName).callRemote(
            functionName, *args, **kwargs)

    def connectServiceHandle(self, target):
        '''
                注册连接成功时触发函数的handler
        :param target: 函数
        :return:
        '''
        self.connectService.mapTarget(target)

    def lostConnectServiceHandle(self, target):
        '''
                注册连接断开时触发函数的handler
        :param target: 函数
        :return:
        '''
        self.lostConnectService.mapTarget(target)

    def _doWhenConnect(self) -> defer.Deferred:
        '''
                连接成功时触发
        :return:
        '''
        defer_list = []
        for service in self.connectService:
            defer_list.append(self.connectService.callTarget(service))
        return defer.DeferredList(defer_list, consumeErrors=True)

    def _doWhenLostConnect(self) -> defer.Deferred:
        '''
                连接断开时触发
        :return:
        '''
        defer_list = []
        for service in self.lostConnectService:
            defer_list.append(self.lostConnectService.callTarget(service))
        return defer.DeferredList(defer_list, consumeErrors=True)
