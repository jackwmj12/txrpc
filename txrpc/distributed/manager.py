
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
import random
from typing import Dict, List, Union
from zope.interface import Interface, implementer
from txrpc.distributed.child import NodeChild
from loguru import logger

class RemoteUnFindedError(Exception):
    pass

class LocalUnFindedError(Exception):
    pass

class Node():
    def __init__(self, name):
        '''
            初始化子节点对象
        '''
        self.name = name
        self.hand : List[NodeChild] = []
        self.children : List[NodeChild] = []
        self.handCur : int = 0
    
    def __str__(self):
        return f" Children : {self.name} : {self.children} "
    
    def __repr__(self):
        return f" Children : {self.name}"
    
    def append(self,child : NodeChild):
        '''
            :param
        '''
        if child not in self.children:
            self.children.append(child)
            self.handCur = 0
            hand = [child for _ in range(child.getWeight())]
            self.hand.extend(hand)
            random.shuffle(self.hand)  # 洗牌
            logger.debug(f"node <{self.name}> append NodeChild <{self.children}> success ")
        else:
            logger.error("append failed , node %s is already exist" % child.getName())
    
    def remove(self,child : NodeChild):
        '''
            :param
        '''
        if child in self.children:
            self.children.remove(child)
            self.handCur = 0
            self.hand = [item for item in self.hand if item != child] #
            random.shuffle(self.hand)  # 洗牌
            logger.debug(f"node <{self.name}> remove Nodechild <{self.children}> success ")
        else:
            logger.error("remove failed , node %s is not exist" % child.getName())
    
    def shuffle(self):
        '''
            洗牌
        :param
        '''
        random.shuffle(self.hand)
        self.handCur = 0
    
    def getChild(self) -> Union[NodeChild,None]:
        '''
            获取子节点
        :return:
        '''

        if self.children and self.hand:
            if self.handCur >= len(self.hand) :
                self.handCur = 0
            child = self.hand[self.handCur]
            self.handCur += 1
            return child
        return None
        
class _NodeManager(Interface):
    '''节点管理器接口'''
    
    def __init__(self):
        '''初始化接口'''
        
    def getNodeChildById(self,childId):
        '''根据节点id获取节点实例'''
        
    def getNodeChildByName(self,childname):
        '''根据节点的名称获取节点实例'''
        
    def addNodeChild(self,child):
        '''添加一个child节点
        @param child: Child object
        '''
    
    def dropNodeChild(self,*arg,**kw):
        '''删除一个节点'''
        
    def callNodeChildByID(self,*args,**kw):
        '''调用子节点的接口'''
        
    def callNodeChildByName(self,*args,**kw):
        '''调用子节点的接口
        @param childname: str 子节点的名称
        '''
    
    def dropNodeChildByID(self,childId):
        '''删除一个child 节点
        @param childId: Child ID
        '''
       
@implementer(_NodeManager)
class NodeManager(object):
    '''
        子节点管理器
    '''
    
    def __init__(self):
        '''
            初始化子节点管理器
        '''
        self._nodes : Dict[str:Node] = {}
    
    def getNodes(self) -> Dict:
        return self._nodes
    
    def getNode(self,name) -> Union[Node,None]:
        '''
            :param
        '''
        node: Node = self._nodes.get(name)
        if node :
            return node
        return None
    
    def getNodeChildById(self,childId) -> Union[None,NodeChild]:
        '''
            根据节点的ID获取节点实例
        '''
        for node in self._nodes.values():
            for nodeChild in node.children:
                if nodeChild.getId() == childId:
                    return nodeChild
        return None
        
    def getNodeChildByName(self,name) -> Union[None,NodeChild]:
        '''
            根据节点的名称获取节点实例
        '''
        if name:
            node: Node = self._nodes.get(name)
            # logger.debug(f"NODE 获取成功 {node}")
            if node:
                return node.getChild()
        return None
        
    def addNodeChild(self,nodeChild: NodeChild):
        '''
            添加一个child节点
            @param child: Child object
        '''
        name = nodeChild.getName()
        # logger.info("node %s is connecting"%name)
        node : Node = self._nodes.get(name)
        if node:
            node.append(nodeChild)
        else:
            self._nodes[name] = Node(name)
            self._nodes[name].append(nodeChild)
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
        
    def dropNodeChild(self,nodeChild: NodeChild):
        '''
        删除一个 nodeChild 节点
        @param nodeChild :
        '''
        node: Node = self._nodes.get(nodeChild.getName())
        if node:
            node.remove(nodeChild)
        else:
            logger.error("nodes %s is not exist " % nodeChild.getName())
            
    def dropNodeChildByID(self,childId : int) -> bool:
        '''
        删除一个child 节点
        @param childId: Child ID 
        '''
        nodeChild: NodeChild = self.getNodeChildById(childId)
        if nodeChild:
            self.dropNodeChild(nodeChild)
            return True
        else:
            logger.error("node[%s] is not exist" % childId)
        return False
            
    def callNodeChildByID(self,childId,*args,**kw):
        '''
            调用子节点的接口
            @param childId: int 子节点的id
        '''
        nodeChild = self.getNodeChildById(childId=childId) # 根据ID获取子节点
        if not nodeChild:
            # logger.error("child %s doesn't exists" % childId)
            # return
            raise RemoteUnFindedError()
        return nodeChild.callbackNodeChild(*args,**kw) # 调用子节点
    
    def callNodeChildByName(self,name,*args,**kw):
        '''
            调用子节点的接口
            @param name: str 子节点的名称
        '''

        nodeChild = self.getNodeChildByName(name) # 获取子节点
        if not nodeChild:
            # logger.error("NodeChild %s doesn't exists" % name)
            # return
            raise RemoteUnFindedError()
        return nodeChild.callbackNodeChild(*args,**kw) # 调用子节点
        