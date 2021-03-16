import json
import os
from txrpc.globalobject import GlobalObject
from txrpc.utils.log import logger
from txrpc.server import RPCServer

NODE_NAME = "SERVER"

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

def fun():
    d = RPCServer.callRemote("CLIENT", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return d

app = RPCServer(NODE_NAME)

@app.startServiceHandle
def doWhenStart():
    logger.debug("i am starting")

@app.childConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    from twisted.internet import reactor
    
    logger.debug("{} connected".format(name))
    
    for i in range(1000):
        reactor.callLater(i * 2 + 1, fun)

@app.childLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

app.run()