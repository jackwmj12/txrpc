
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
from service.services import Service

class ProxyReference(pb.Referenceable):
    '''代理通道'''
    
    def __init__(self):
        '''初始化'''
        self._service = Service('proxy')
        
    def addService(self,service):
        '''添加一条服务通道'''
        self._service = service
    
    def remote_callChild(self, command,*arg,**kw):
        '''
        代理发送数据
        '''
        return self._service.callTarget(command,*arg,**kw)
    
    
    
        