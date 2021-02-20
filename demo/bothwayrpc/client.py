from twisted.internet import reactor

import txrpc
from txrpc.utils import logger
from txrpc.client import RPCClient
from txrpc.server import RPCServer

logger.init()


def fun():
    d = RPCServer.callRemote("client", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d


server = RPCServer("server",9000,service_path="demo.baserpc.app.serverapp")

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

client = RPCClient().clientConnect(
    name="client",
    target_name="server",
    host="127.0.0.1",
    port=10000,
    service_path="demo.baserpc.app.clientapp"
    ,weight=10)

txrpc.run()