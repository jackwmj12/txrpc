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
from txrpc.core import RPC
from txrpc.distributed.node import RemoteObject
from txrpc.globalobject import GlobalObject
from txrpc.service.service import Service
from txrpc.utils import logger


class RPCClient(RPC):
	'''
	:return
	'''
	
	def __init__(self):
		'''
		:return
		'''
		super().__init__()
		self.connectService = Service("connect_service")
	
	def doConnect(self,target):
		'''
		
		:param
		'''
		self.connectService.mapTarget(target)
		
	def clientConnect(self, name: str, target_name: str, host: str, port: int, service_path: str = None, weight=10):
		'''
		:param
		'''
		logger.debug("local<{name}> -> remote:<{target_name}>".format(name=name, target_name=target_name))
		
		self._connectRemote(name=name, target_name=target_name, host=host, port=port, weight=weight)
		
		if service_path:
			self.registerService(service_path)
		
		return self
	
	@staticmethod
	def callRemote(remoteName: str, functionName: str, *args, **kwargs):
		'''
		:param
		'''
		return GlobalObject().getRemote(remoteName).callRemote(functionName, *args, **kwargs)
	
	def _connectRemote(self, name: str, target_name: str, host: str, port: int, weight: int = 10):
		'''
			控制 节点 连接 另一个节点
			:param name:  当前节点名称
			:param remote_name:  需要连接的节点名称
			:return:
		'''
		assert name != None, "local 名称不能为空"
		assert port != None, "port 不能为空"
		assert host != None, "host 不能为空"
		assert target_name != None, "target_name 不能为空"
		
		remote = RemoteObject(name)
		remote.setWeight(weight)
		remote.connect((host, port))
		GlobalObject().remote[target_name] = remote
		
		for service in self.connectService:
			self.connectService.callTarget(service)