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
from txrpc.service.service import Service
from loguru import logger


class RPCClient(RPC):
	'''
	:return
	'''
	
	def __init__(self,name = None):
		'''
		:return
		'''
		super(RPCClient, self).__init__()
		self.connectService = Service("connect_service")  # rpc连接成功时运行
		self.lostConnectService = Service("lost_connect_service")  # rpc连接断开时运行
		self.name = name
		
	def clientConnect(self,name=None,host =None,port=None,weight=None,service_path=None):
		'''
		:param
		'''
		
		if not service_path:
			self.service_path = GlobalObject().config.get("DISTRIBUTED").get(self.name).get("APP")
		else:
			self.service_path = service_path
		
		if not name:
			name = GlobalObject().config.get("DISTRIBUTED").get(self.name).get("REMOTE").get("NAME")
		
		if not host:
			host = GlobalObject().config.get("DISTRIBUTED").get(self.name).get("REMOTE").get("HOST")
			
		if not port:
			port = int(GlobalObject().config.get("DISTRIBUTED").get(self.name).get("REMOTE").get("PORT"))
		
		if not weight:
			weight = int(GlobalObject().config.get("DISTRIBUTED").get(self.name).get("REMOTE").get("WEIGHT",10))
		
		logger.debug("local<{name}> -> remote:<{target_name}>".format(name=self.name, target_name=name))
		
		self._connectRemote(name=self.name, target_name=name, host=host, port=port, weight=weight)

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
		GlobalObject().remote[target_name] = remote
		d = remote.connect((host, port))
		d.addCallback(lambda ign : self._doWhenConnect())
		d.addCallback(lambda ign : self.registerService(self.service_path))
	
	def connectServiceHandle(self, target):
		self.connectService.mapTarget(target)
	
	def lostConnectServiceHandle(self, target):
		self.lostConnectService.mapTarget(target)
	
	def _doWhenConnect(self) -> defer.Deferred:
		defer_list = []
		for service in self.connectService:
			defer_list.append(self.connectService.callTarget(service))
		return defer.DeferredList(defer_list, consumeErrors=True)
	
	def _doWhenLostConnect(self) -> defer.Deferred:
		defer_list = []
		for service in self.lostConnectService:
			defer_list.append(self.lostConnectService.callTarget(service))
		return defer.DeferredList(defer_list, consumeErrors=True)
		