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

from txrpc2.service.service import Service
from txrpc2.globalobject import GlobalObject
from txrpc2.utils import delay_import
from loguru import logger

class RPCBase():
	'''
		RPC 基类
	'''

	def __init__(self):
		'''
			:return
		'''
		self.servicePath : Union[List[str],None] = None # 服务的py文件路径
		self.startService = Service("startservice") # 程序开始时运行
		self.stopService = Service("endservice")    # 程序结束时运行(暂无实现)
		self.reloadService = Service("reloadservice") # 程序重载时运行
	
	def run(self):
		'''
			:return
		'''
		from twisted.internet import reactor
		reactor.callWhenRunning(self._doWhenStart) # 注册开始运行函数
		reactor.run()
	
	def install(self):
		'''
			:param
		'''
		from twisted.internet import reactor
		reactor.callWhenRunning(self._doWhenStart) # 注册开始运行函数
	
	def registerService(self, servicePath: Union[List[str],str,None]):
		'''
			:return
		'''
		if servicePath:
			logger.debug(f"即将导入模块 : {servicePath}")
			delay_import(servicePath)
	
	def twisted_init(self):
		'''

		:param
		'''
		socket.setdefaulttimeout(GlobalObject().config.get("SOCKET_TIME_OUT", 60)) # 设置socket超时时间
		logger.info("设置socket超时时间为：{}".format(GlobalObject().config.get("SOCKET_TIME_OUT", 60)))
		from twisted.internet import reactor
		reactor.suggestThreadPoolSize(GlobalObject().config.get("TWISTED_THREAD_POOL", 8))  # 设置线程池数量
		logger.info("设置线程池数量为：{}".format(GlobalObject().config.get("TWISTED_THREAD_POOL", 8)))

	def startServiceHandle(self, target):
		"""
			注册程序停止触发函数的handler
		:param target: 函数
		:return:
		"""
		self.startService.mapFunction(target)
	
	def stopServiceHandle(self, target):
		"""
			注册程序停止触发函数的handler
		:param target: 函数
		:return:
		"""
		self.stopService.mapFunction(target)
	
	def reloadServiceHandle(self, target):
		"""
			注册程序重载触发函数的handler
		:param target: 函数
		:return:
		"""
		self.reloadService.mapFunction(target)
	
	def _doWhenStart(self) -> defer.Deferred:
		'''
			程序开始时,将会运行该函数
		:return:
		'''
		defer_list = []
		for service in self.startService:
			defer_list.append(
				self.startService.callFunction(service)
			)
		return defer.DeferredList(defer_list,consumeErrors=True)
	
	def _doWhenStop(self) -> defer.Deferred:
		'''
			程序停止时,将会运行该服务
		:return:
		'''
		defer_list = []
		for service in self.stopService:
			defer_list.append(
				self.stopService.callFunction(service)
			)
		return defer.DeferredList(defer_list, consumeErrors=True)
	
	def _doWhenReload(self) -> defer.Deferred:
		'''
			程序重载时,将会运行该服务
		:return:
		'''
		self.registerService(self.servicePath)
		defer_list = []
		for service in self.reloadService:
			defer_list.append(
				self.reloadService.callFunction(service)
			)
		return defer.DeferredList(defer_list, consumeErrors=True)
	