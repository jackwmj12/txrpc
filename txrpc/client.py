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

    def clientConnect(self, name=None, remoteName=None, host=None, port=None, weight=None):
        '''

        :param name:  本节点名称
        :param remoteName: 目标节点名称
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

        # 创建远程对象实例
        remote = RemoteObject(name, remoteName)
        remote.setWeight(weight)
        # 远程对象存入 leafRemoteMap
        GlobalObject().leafRemoteMap[remoteName] = remote
        # 创建连接
        d = remote.connect(
            (host, port)
        ).addCallback(
            lambda ign: self.registerService(
                self.servicePath
            )
        )
        return d

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
        return GlobalObject().callRoot(
            remoteName,
            functionName,
            *args, **kwargs
        )
