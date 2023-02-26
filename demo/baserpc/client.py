import json
import os
import txrpc2
from txrpc2.globalobject import GlobalObject, startServiceHandle, connectRootHandle, lostConnectRootHandle
from loguru import logger
from txrpc2.client import RPCClient

NODE_NAME = "CLIENT"

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

app = RPCClient(name=NODE_NAME).clientConnect()

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
        0.5,
        p
    )

@connectRootHandle(NODE_NAME)
def doWhenConnect():
    logger.debug(100 * "*")
    logger.debug("i am connected")
    from twisted.internet import reactor
    p()

@lostConnectRootHandle(NODE_NAME)
def doWhenLoseconnect():
    logger.debug(100 * "*")
    logger.debug("i am loseconnect")
    from twisted.internet import reactor
    reactor.callLater(
        1,
        p
    )

txrpc2.run()