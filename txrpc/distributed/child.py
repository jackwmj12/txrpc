'''
Created on 2019-11-22
@author: LCC
            ┏┓　　　┏┓
          ┏┛┻━━━┛┻┓
          ┃　　　━　　　┃
          ┃　┳┛　┗┳　┃
          ┃　　　　　　　┃
          ┃　　　┻　　　┃
          ┗━┓　　　┏━┛
              ┃　　　┃
              ┃　　　┗━━━┓
              ┃　　　　　　　┣┓
              ┃　　　　　　　┏┛
              ┗┓┓┏━┳┓┏┛
                ┃┫┫　┃┫┫
                ┗┻┛　┗┻┛
                 神兽保佑，代码无BUG!
 @desc：
                  | - Node       |-- NodeChild
    NodeManager - - - Node - - - - - NodeChild
                  | - Node       |-- NodeChild
'''

class NodeChild(object):
	'''
    子节点对象
    '''

	def __init__(self, cid, name):
		'''
        初始化子节点对象
        '''
		self._id = cid
		self._name = name
		self._weight = 10
		self._transport = None

	def __str__(self):
		return f" NodeChild<{self._name}:{self._id}>"

	def __repr__(self):
		return f" NodeChild<{self._name}:{self._id}>"

	def setId(self,id):
		self._id = id

	def getId(self):
		return self._id

	def setName(self,name):
		'''
		设置节点名称
		:param
		'''
		self._name = name

	def getName(self):
		'''
        获取节点的名称
        '''
		return self._name

	def getWeight(self):
		'''
		获取节点比重
		:param
		'''
		return self._weight

	def setWeight(self,weight):
		'''
		设置节点比重
		:param
		'''
		self._weight = weight

	def setTransport(self, transport):
		'''
        设置子节点的代理通道
        '''
		self._transport = transport

	def callbackNodeChild(self, *args, **kw):
		'''
            root节点调用子节点的接口
            return a Defered Object (recvdata)
        '''
		# logger.debug("root 远程调用 child:{} ".format(self.getName()))
		recvdata = self._transport.callRemote('callChild', *args, **kw)
		return recvdata