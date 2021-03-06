
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
    root节点
'''
from typing import Dict, List, Union
from zope.interface import Interface, implementer
import numpy as np
from txrpc.distributed.child import Child
from txrpc.utils.log import logger

class RemoteUnFindedError(Exception):
    pass

class Node():
    def __init__(self, name):
        '''
        初始化子节点对象
        '''
        self.name = name
        self.hand : List[int] = []
        self.children : List[Child] = []
        self.handCur : int = 0
    
    def __str__(self):
        return f" Children : {self.name} : {self.children} "
    
    def __repr__(self):
        return f" Children : {self.name}"
    
    def append(self,child : Child):
        '''
        :param
        '''
        if child not in self.children:
            self.children.append(child)
            self.handCur = 0
            hand = [child for _ in range(child.getWeight())]
            self.hand.extend(hand)
            np.random.shuffle(self.hand)  # 洗牌
            logger.debug(f"append success , \nnodes {self.children}\nhand : {self.hand}")
        else:
            logger.error("append failed , node %s is already exist" % child.getName())
    
    def remove(self,child : Child):
        '''
        :param
        '''
        if child in self.children:
            self.children.remove(child)
            self.handCur = 0
            self.hand = [item for item in self.hand if item != child] #
            np.random.shuffle(self.hand)  # 洗牌
            logger.debug(f"remove success , \nnodes {self.children}\nhand : {self.hand}")
        else:
            logger.error("remove failed , node %s is not exist" % child.getName())
    
    def shuffle(self):
        '''
        :param
        '''
        np.random.shuffle(self.hand)  # 洗牌
        self.handCur = 0
    
    def getChild(self):
        '''
        
        :return:
        '''
        if self.children and self.hand:
            if self.handCur >= len(self.hand) :
                self.handCur = 0
            # logger.debug(self.hand[self.handCur])
            child = self.hand[self.handCur]
            self.handCur += 1
            return child
        return None
        
class _NodeManager(Interface):
    '''节点管理器接口'''
    
    def __init__(self):
        '''初始化接口'''
        
    def getChildById(self,childId):
        '''根据节点id获取节点实例'''
        
    def getChildByName(self,childname):
        '''根据节点的名称获取节点实例'''
        
    def addChild(self,child):
        '''添加一个child节点
        @param child: Child object
        '''
    
    def dropChild(self,*arg,**kw):
        '''删除一个节点'''
        
    def callChildById(self,*args,**kw):
        '''调用子节点的接口'''
        
    def callChildByName(self,*args,**kw):
        '''调用子节点的接口
        @param childname: str 子节点的名称
        '''
    
    def dropChildByID(self,childId):
        '''删除一个child 节点
        @param childId: Child ID
        '''
       
@implementer(_NodeManager)
class NodeManager(object):
    '''子节点管理器'''
    
    def __init__(self):
        '''初始化子节点管理器'''
        self._nodes : Dict[str:Node] = {}
        
    def getNode(self,name) -> Union[Node,None]:
        '''
        :param
        '''
        node : Node = self._nodes.get(name)
        if node :
            return node
        return None
    
    def getChildById(self,childId) -> Union[None,Child]:
        '''
        根据节点的ID获取节点实例
        '''
        for node in self._nodes.values():
            for child in node.children:
                if child.getId() == childId:
                    return child
        return None
        
    def getChildByName(self,name) -> Union[None,Child]:
        '''
        根据节点的名称获取节点实例
        '''
        if name:
            node : Node = self._nodes.get(name)
            logger.debug(f"node 获取成功 {node}")
            if node:
                return node.getChild()
        return None
        
    def addChild(self,child :Child):
        '''
        添加一个child节点
        @param child: Child object
        '''
        name = child.getName()
        # logger.info("node %s is connecting"%name)
        node : Node = self._nodes.get(name)
        if node:
            node.append(child)
        else:
            self._nodes[name] = Node(name)
            self._nodes[name].append(child)
        # logger.info("node %s is connected" % name)
        
    def handShuffle(self,name):
        '''
        :param
        '''
        node : Node = self._nodes.get(name)
        if node:
            node.shuffle()
        else:
            logger.error("child nodes %s is not exist" % name)
        
    def dropChild(self,child):
        '''
        删除一个child 节点
        @param child: Child Object 
        '''
        node : Node = self._nodes.get(child.getName())
        if node:
            node.remove(child)
        else:
            logger.error("nodes %s is not exist " % child.getName())
            
    def dropChildById(self,childId : int) -> bool:
        '''
        删除一个child 节点
        @param childId: Child ID 
        '''
        child : Child = self.getChildById(childId)
        if child:
            self.dropChild(child)
            return True
        else:
            logger.error("node[%s] is not exist" % childId)
        return False
            
    def callChildById(self,childId,*args,**kw):
        '''调用子节点的接口
        @param childId: int 子节点的id
        '''
        child = self.getChildById(childId=childId)
        if not child:
            logger.error("child %s doesn't exists" % childId)
            return
        return child.callbackChild(*args,**kw)
    
    def callChildByName(self,name,*args,**kw):
        '''调用子节点的接口
        @param name: str 子节点的名称
        '''
        # logger.debug("调用服务，请求：{} 服务".format(name))
        # logger.debug("参数为：{}".format(args))

        child = self.getChildByName(name)
        
        if not child:
            logger.error("child %s doesn't exists" % name)
            return
        return child.callbackChild(*args,**kw)
        