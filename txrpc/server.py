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
from txrpc.utils import logger


class RPCServer(RPC):
	'''
	:return
	'''
	
	def __init__(self, name: str,service_path = None,port=None):
		'''
		:return
		'''
		# root对象监听制定端口
		super(RPCServer,self).__init__()
		
		self.name = name
		
		if not service_path:
			self.service_path = GlobalObject().config.get("DISTRIBUTED").get(name).get("APP")
		
		if not port:
			port = int(GlobalObject().config.get("DISTRIBUTED").get(name).get("PORT"))
		
		GlobalObject().root = PBRoot()
		
		from twisted.internet import reactor
		
		reactor.listenTCP(port, BilateralFactory(GlobalObject().root))
		
		service = Service(name=name)
		
		# 将服务添加到root
		GlobalObject().root.addServiceChannel(service)
		
		if self.service_path:
			self.registerService(self.service_path)
	
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