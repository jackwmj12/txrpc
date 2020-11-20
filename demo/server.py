from twisted.internet import reactor

from globalobject import GlobalObject
from utils import Log
import sys

from rpc import RPCServer, callRemote

Log.init_()

def fun_():
    d = GlobalObject().root.callChildByName("client", "test")
    d.addCallback(print)
    d.addErrback(print)
    return d

def doChildConnect(name,transport):
    '''
    :return
    '''
    Log.msg("{} connected".format(name))
    
    reactor.callLater(1,fun_)
    
    
def doChildLostConnect(childId):
    '''
    :return
    '''
    Log.debug("{} lost connect".format(childId))

server = RPCServer("server",10000)
server.setDoWhenChildConnect(doChildConnect)
server.setDoWhenChildLostConnect(doChildLostConnect)
server.run()