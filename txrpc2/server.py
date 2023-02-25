# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : joe lin
# @FILE     : server.py
# @Time     : 2021-02-20 21:16
# @Software : txrpc2
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
from txrpc2.core import RPCBase
from txrpc2.service.service import Service
from txrpc2.distributed.root import BilateralFactory, PBRoot
from txrpc2.globalobject import GlobalObject

class RPCServer(RPCBase):
	'''
	:return
	'''
	
	def __init__(self, name: str,service_path = None,port=None):
		'''
			RPC 服务端
		:param name: 服务端名字
		:param service_path: 服务路径
		:param port: 服务端port
		'''
		# root对象监听制定端口
		GlobalObject().root = self
		super(RPCServer,self).__init__()
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
		# 注册服务
		self.registerService(self.service_path)
	
	def leafConnectHandle(self, target):
		"""
			被该装饰器装饰的函数,会在leaf节点和root节点连接建立时触发
		:param target: 函数
		:return:
		"""
		self.pbRoot.leafConnectService.mapFunction(target)
	
	def leafLostConnectHandle(self, target):
		"""
			被该装饰器装饰的函数,会在leaf节点和root节点连接断开时触发
		:param target: 函数
		:return:
		"""
		self.pbRoot.leafLostConnectService.mapFunction(target)
	
	@staticmethod
	def callRemote(remoteName: str, functionName: str, *args, **kwargs):
		'''
			调用子节点挂载的函数
		:param remoteName:  远程分支节点名称
		:param functionName: 方法名称
		:param args:  参数
		:param kwargs:  参数
		:return:
		'''
		return GlobalObject().getRoot().pbRoot.callChildByName(remoteName, functionName, *args, **kwargs)

	@staticmethod
	def callRemoteByID(remoteID: str, functionName: str, *args, **kwargs):
		'''
            调用子节点挂载的函数
        :param remoteID:  远程分支节点ID
        :param functionName: 方法名称
        :param args:  参数
        :param kwargs:  参数
        :return:
        '''
		return GlobalObject().getRoot().pbRoot.callChildByID(remoteID, functionName, *args, **kwargs)