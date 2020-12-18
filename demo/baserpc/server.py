from twisted.internet import reactor

from globalobject import GlobalObject
from utils import Log
import sys

from rpc import RPCServer

Log.init_()

def fun():
    d = RPCServer.callRemote("client", "client_test")
    d.addCallback(Log.debug)
    d.addErrback(Log.err)
    return d

def doChildConnect(name,transport):
    '''
    :return
    '''
    Log.debug("{} connected".format(name))
    
    for i in range(1000):
        reactor.callLater(i*2 + 1,fun)
    
    
def doChildLostConnect(childId):
    '''
    :return
    '''
    Log.debug("{} lost connect".format(childId))

server = RPCServer("server",10000,service_path="demo.baserpc.app.serverapp")
server.setDoWhenChildConnect(doChildConnect)
server.setDoWhenChildLostConnect(doChildLostConnect)
server.run()