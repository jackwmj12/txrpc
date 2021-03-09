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

from txrpc.service.service import Service
from txrpc.globalobject import GlobalObject
from txrpc.utils import delay_import, logger

class RPC():
	
	def __init__(self):
		'''
		:return
		'''
		self.startService = Service("startservice") # 程序开始时运行
		self.stopService = Service("endservice")    # 程序结束时运行(暂无实现)
		self.reloadService = Service("reloadservice") # 程序重载时运行
		
	
	def run(self):
		'''
		:return
		'''
		from twisted.internet import reactor
		
		reactor.callWhenRunning(self._doWhenStart)
		
		reactor.run()
	
	def install(self):
		from twisted.internet import reactor
		
		reactor.callWhenRunning(self._doWhenStart)
	
	def registerService(self, service_path: str):
		'''
		:return
		'''
		logger.debug(f"即将导入模块:{service_path}")
		delay_import(service_path)
	
	def twisted_init(self):
		'''
		# 初始化socket超时时间
		:param
		'''
		
		socket.setdefaulttimeout(GlobalObject().config.get("SOCKET_TIME_OUT", 60))
		
		logger.msg("初始化socket超时时间为：{}".format(GlobalObject().config.get("SOCKET_TIME_OUT", 60)))
		
		from twisted.internet import reactor
		
		reactor.suggestThreadPoolSize(GlobalObject().config.get("TWISTED_THREAD_POOL", 8))  # 设置线程池数量
	
	def startServiceHandle(self, target):
		"""
		程序运行时,将会运行该服务
		:param 
			function()
		"""
		self.startService.mapTarget(target)
	
	def stopServiceHandle(self, target):
		"""
		程序结束时,将会运行该服务
		"""
		self.stopService.mapTarget(target)
	
	def reloadServiceHandle(self, target):
		"""
		程序重载时,将会运行该服务
		"""
		self.reloadService.mapTarget(target)
	
	def _doWhenStart(self) -> defer.Deferred:
		defer_list = []
		for service in self.startService:
			defer_list.append(self.startService.callTarget(service))
		return defer.DeferredList(defer_list,consumeErrors=True)
	
	def _doWhenStop(self) -> defer.Deferred:
		# for service in self.stopService:
		# 	self.stopService.callTarget(service)
		defer_list = []
		for service in self.stopService:
			defer_list.append(self.stopService.callTarget(service))
		return defer.DeferredList(defer_list, consumeErrors=True)
	
	def _doWhenReload(self) -> defer.Deferred:
		# for service in self.reloadService:
		# 	self.reloadService.callTarget(service)
		defer_list = []
		for service in self.reloadService:
			defer_list.append(self.reloadService.callTarget(service))
		return defer.DeferredList(defer_list, consumeErrors=True)
	