import json
import os

import txrpc2
from txrpc2.globalobject import GlobalObject
from loguru import logger
from txrpc2.server import RPCServer


# logger.debug(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"]))

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

def fun():
    d = GlobalObject().callLeaf("CLIENT", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    d.addCallback(
        lambda ign : {

        }
    )
    return d

server = RPCServer("SERVER")

@server.leafConnectHandle
def doLeafConnect(name, transport):
    '''
    :return
    '''
    from twisted.internet import reactor
    
    logger.debug("{} connected".format(name))

    reactor.callLater(1, fun)

@server.leafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

txrpc2.run()