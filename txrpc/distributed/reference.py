
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
    普遍透明代理客户端向服务器发送的引用接口
'''

from twisted.spread import pb
from txrpc.service.service import Service
from loguru import logger


class ProxyReference(pb.Referenceable):
    '''
        可引用的代理对象
            将 service 挂载在可引用的代理对象下
        RPC连接成功后,客户端需要将可引用的代理对象发送给服务端,
            发送成功后,服务端才可以通过代理对象调用客户端
    '''
    
    def __init__(self, name= 'proxy'):
        '''初始化'''
        self._service = Service(name)
        
    def addService(self,service):
        '''
            将服务挂载到可引用的代理对象下
        :param service:
        :return:
        '''
        self._service = service
    
    def remote_callChild(self, functionName,*arg,**kw):
        '''
            服务端调用客户端
        '''
        return self._service.callFunction(functionName,*arg,**kw)
    
    
    
        