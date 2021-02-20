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
from txrpc.core import RPC
from txrpc.service.service import Service
from txrpc.distributed.root import BilateralFactory, PBRoot
from txrpc.globalobject import GlobalObject

class RPCServer(RPC):
	'''
	:return
	'''
	
	def __init__(self, name: str, port: int, service_path: str = None):
		'''
		:return
		'''
		# root对象监听制定端口
		super().__init__()
		
		self.service_path = service_path
		
		GlobalObject().root = PBRoot()
		
		from twisted.internet import reactor
		
		reactor.listenTCP(port, BilateralFactory(GlobalObject().root))
		
		service = Service(name=name)
		
		# 将服务添加到root
		GlobalObject().root.addServiceChannel(service)
		
		if service_path:
			self.registerService(service_path)
	
	def childConnectHandle(self, target):
		"""
		程序运行时,将会运行该服务
		"""
		GlobalObject().root.childConnectService.mapTarget(target)
	
	def childLostConnectHandle(self, target):
		"""
		程序结束时,将会运行该服务
		"""
		GlobalObject().root.childLostConnectService.mapTarget(target)
	
	@staticmethod
	def callRemote(remoteName: str, functionName: str, *args, **kwargs):
		'''
		:param
		'''
		return GlobalObject().root.callChildByName(remoteName, functionName, *args, **kwargs)