import json
import os

from twisted.internet import reactor

import txrpc
from txrpc.globalobject import GlobalObject
from txrpc.utils import logger

from txrpc.server import RPCServer

logger.init()

# logger.debug(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"]))

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

def fun():
    d = RPCServer.callRemote("CLIENT", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

server = RPCServer("SERVER")

@server.childConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    logger.debug("{} connected".format(name))
    
    for i in range(1000):
        reactor.callLater(i * 2 + 1, fun)

@server.childLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

txrpc.run()