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
from loguru import logger


class RPCServer(RPC):
	'''
	:return
	'''
	
	def __init__(self, name: str,service_path = None,port=None):
		'''
		:return
		'''
		# root对象监听制定端口
		super(RPCServer,self).__init__(name=name)
		
		self.name = name
		
		if not service_path:
			self.service_path = GlobalObject().config.get("DISTRIBUTED").get(name).get("APP")
		
		if not port:
			port = int(GlobalObject().config.get("DISTRIBUTED").get(name).get("PORT"))
		
		self.pbRoot = PBRoot()
		
		from twisted.internet import reactor
		
		reactor.listenTCP(port, BilateralFactory(self.pbRoot))
		
		service = Service(name=name)
		
		# 将服务添加到root
		self.pbRoot.addServiceChannel(service)
		
		self.registerService(self.service_path)
	
	def childConnectHandle(self, target):
		"""
			注册子节点连接触发触发函数的handler
		:param target: 函数
		:return:
		"""
		self.pbRoot.childConnectService.mapTarget(target)
	
	def childLostConnectHandle(self, target):
		"""
			注册子节点断开触发触发函数的handler
		:param target:
		:return:
		"""
		self.pbRoot.childLostConnectService.mapTarget(target)
	
	@staticmethod
	def callRemote(remoteName: str, functionName: str, *args, **kwargs):
		'''
			调用子节点挂载的函数
		:param remoteName:  节点名称
		:param functionName: 方法名称
		:param args:  参数
		:param kwargs:  参数
		:return:
		'''
		return GlobalObject().node.pbRoot.callChildByName(remoteName, functionName, *args, **kwargs)