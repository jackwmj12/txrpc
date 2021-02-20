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
from txrpc.service.service import Service
from txrpc.globalobject import GlobalObject
from txrpc.utils import delay_import, logger

class RPC():
	
	def __init__(self):
		'''
		:return
		'''
		self.startService = Service("startservice")
		self.stopService = Service("endservice")
		self.reloadService = Service("reloadservice")
		
		from twisted.internet import reactor
		
		reactor.callWhenRunning(self._doWhenStart)
	
	def run(self):
		'''
		:return
		'''
		from twisted.internet import reactor
		
		reactor.run()
	
	def registerService(self, service_path: str):
		'''
		:return
		'''
		delay_import(service_path.split(","))
	
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
	
	def _doWhenStart(self):
		for service in self.startService:
			self.startService.callTarget(service)
	
	def _doWhenStop(self):
		for service in self.stopService:
			self.stopService.callTarget(service)
	
	def _doWhenReload(self):
		for service in self.reloadService:
			self.reloadService.callTarget(service)