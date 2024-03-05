

from txrpc.globalobject import remoteServiceHandle
from txrpc.client import RPCClient
from loguru import logger

def fun():
    d = RPCClient.callRemote("SERVER", "server_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return d

@remoteServiceHandle("SERVER")
def client_test():
    from twisted.internet import reactor
    reactor.callLater(1, fun)
    return "this is a response from client"

