from twisted.internet import reactor

from txrpc.globalobject import remoteserviceHandle
from txrpc.rpc import RPCClient
from txrpc.utils import logger

def fun():
    d = RPCClient.callRemote("server", "server_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

@remoteserviceHandle("server")
def client_test():
    reactor.callLater(1, fun)
    return "this is a response from client"

