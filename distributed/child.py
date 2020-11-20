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
    子节点
'''

class Child(object):
	'''
    子节点对象
    '''

	def __init__(self, cid, name):
		'''
        初始化子节点对象
        '''
		self._id = cid
		self._name = name
		self._transport = None

	def getName(self):
		'''
        获取子节点的名称
        '''
		return self._name

	def setTransport(self, transport):
		'''
        设置子节点的代理通道
        '''
		self._transport = transport

	def callbackChild(self, *args, **kw):
		'''
        root节点调用子节点的接口
        return a Defered Object (recvdata)
        '''
		# Log.debug("root 远程调用 child:{} ".format(self.getName()))
		recvdata = self._transport.callRemote('callChild', *args, **kw)
		return recvdata