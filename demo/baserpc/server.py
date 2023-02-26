import json
import os

import txrpc2
from txrpc2.globalobject import GlobalObject, startServiceHandle, leafConnectHandle, leafLostConnectHandle
from loguru import logger
from txrpc2.server import RPCServer

NODE_NAME = "SERVER"

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

def fun():
    d = GlobalObject().callLeaf("CLIENT", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return d

app = RPCServer(NODE_NAME)

def p():
    logger.debug(f"config : {GlobalObject().config}")
    logger.debug(f"leafRemoteMap : {GlobalObject().leafRemoteMap}")
    logger.debug(f"root : {GlobalObject().root}")
    logger.debug(f"leafNodeMap : {GlobalObject().leafNodeMap}")
    logger.debug(100 * "*")

@startServiceHandle
def doWhenStart():
    logger.debug(100 * "*")
    logger.debug("i am starting")
    from twisted.internet import reactor
    reactor.callLater(
        1,
        p
    )

@leafConnectHandle
def doLeafConnect(name, transport):
    '''
    :return
    '''
    logger.debug(100 * "*")
    logger.debug("{} connected".format(name))
    from twisted.internet import reactor
    reactor.callLater(
        1,
        p
    )
    reactor.callLater(
        2,
        fun
    )

@leafLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug(100 * "*")
    logger.debug("{} lost connect".format(childId))
    from twisted.internet import reactor
    reactor.callLater(
        2,
        p
    )

txrpc2.run()