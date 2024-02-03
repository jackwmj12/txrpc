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

    def __init__(self, name: str = None):
        '''
                :return
        '''
        GlobalObject().node = self
        self.name = name
        self.local_service_path: Union[List[str], None] = GlobalObject().config.get("DISTRIBUTED").get(self.name).get("LOCAL_APP")  # 本地服务路径
        self.remote_service_path: Union[List[str], None] = GlobalObject().config.get("DISTRIBUTED").get(self.name).get("REMOTE_APP")  # 远程服务路径
        self.startService = Service("startservice")  # 程序开始时运行
        self.stopService = Service("endservice")    # 程序结束时运行(暂无实现)
        self.reloadService = Service("reloadservice")  # 程序重载时运行

    def run(self):
        '''
                :return
        '''
        from twisted.internet import reactor
        reactor.callWhenRunning(self._doWhenStart)
        reactor.run()

    def install(self):
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
            logger.debug(f"即将导入模块:{service_path}")
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

    def startServiceHandle(self, target):
        """
                注册程序停止触发函数的handler
        :param target: 函数
        :return:
        """
        self.startService.mapTarget(target)

    def stopServiceHandle(self, target):
        """
                注册程序停止触发函数的handler
        :param target: 函数
        :return:
        """
        self.stopService.mapTarget(target)

    def reloadServiceHandle(self, target):
        """
                注册程序重载触发函数的handler
        :param target: 函数
        :return:
        """
        self.reloadService.mapTarget(target)

    def _doWhenStart(self) -> defer.Deferred:
        '''
                程序开始时,将会运行该函数
        :return:
        '''
        self.registerService(self.local_service_path)  # 重载本地服务
        # self.registerService(self.remote_service_path)  # 注意!
        # 该服务必须在RPC连接成功后调用,而非程序启动调用

        defer_list = []
        for service in self.startService:
            defer_list.append(self.startService.callTarget(service))
        return defer.DeferredList(defer_list, consumeErrors=True)

    def _doWhenStop(self) -> defer.Deferred:
        '''
                程序停止时,将会运行该服务
        :return:
        '''
        defer_list = []
        for service in self.stopService:
            defer_list.append(self.stopService.callTarget(service))
        return defer.DeferredList(defer_list, consumeErrors=True)

    def _doWhenReload(self) -> defer.Deferred:
        '''
                程序重载时,将会运行该服务
        :return:
        '''
        self.registerService(self.remote_service_path)  # 重载RPC远程服务
        self.registerService(self.local_service_path)  # 重载本地服务

        defer_list = []
        for service in self.reloadService:
            defer_list.append(self.reloadService.callTarget(service))
        return defer.DeferredList(defer_list, consumeErrors=True)
