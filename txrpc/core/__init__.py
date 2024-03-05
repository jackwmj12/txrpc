# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : __init__.py.py
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
import socket

from twisted.internet import defer
from typing import List, Union

from txrpc.service.service import Service
from txrpc.globalobject import GlobalObject
from txrpc.utils import delay_import
from loguru import logger


class RPC():
    '''
        RPC 基类
    '''

    def __init__(self, name: str = None):
        '''
            :return
        '''
        self.servicePath: Union[List[str], None] = None  # 服务的py文件路径

        from twisted.internet import reactor
        reactor.callWhenRunning(self._doWhenStart)  # 注册开始运行函数

    def run(self):
        '''
                :return
        '''
        from twisted.internet import reactor
        reactor.callWhenRunning(self._doWhenStart)
        reactor.run()

    def prepare(self):
        '''
                :param
        '''
        from twisted.internet import reactor
        reactor.callWhenRunning(self._doWhenStart)

    def registerService(self, service_path: Union[List[str], str, None]):
        '''
                注册服务
                        本地服务
                        远端RPC服务
        '''
        if service_path:
            logger.debug(f"导入模块:{service_path}")
            delay_import(service_path)

    def twisted_init(self):
        '''
                初始化socket超时时间
        :param
        '''

        socket.setdefaulttimeout(
            GlobalObject().config.get(
                "SOCKET_TIME_OUT", 300))
        logger.info(
            "初始化socket超时时间为：{}".format(
                GlobalObject().config.get(
                    "SOCKET_TIME_OUT", 300)))

        from twisted.internet import reactor
        reactor.suggestThreadPoolSize(
            GlobalObject().config.get(
                "TWISTED_THREAD_POOL",
                8))  # 设置线程池数量

    def _doWhenStart(self) -> defer.Deferred:
        '''
                程序开始时,将会运行该函数
        :return:
        '''

        deferList = []
        for service in GlobalObject().startService:
            deferList.append(
                GlobalObject().startService.callFunction(service)
            )
        return defer.DeferredList(deferList, consumeErrors=True)

    def _doWhenStop(self) -> defer.Deferred:
        '''
                程序停止时,将会运行该服务
        :return:
        '''
        deferList = []
        for service in GlobalObject().stopService:
            deferList.append(
                GlobalObject().stopService.callFunction(service)
            )
        return defer.DeferredList(deferList, consumeErrors=True)

    def _doWhenReload(self) -> defer.Deferred:
        '''
                程序重载时,将会运行该服务
        :return:
        '''
        self.registerService(self.servicePath)
        deferList = []
        for service in GlobalObject().reloadService:
            deferList.append(
                GlobalObject().reloadService.callFunction(service)
            )
        return defer.DeferredList(deferList, consumeErrors=True)
