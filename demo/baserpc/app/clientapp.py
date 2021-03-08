from txrpc.globalobject import remoteserviceHandle
from txrpc.client import RPCClient
from txrpc.utils import logger

def fun():
    d = RPCClient.callRemote("SERVER", "server_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

@remoteserviceHandle("SERVER")
def client_test():
    from twisted.internet import reactor
    
    reactor.callLater(1, fun)
    return "this is a response from client"
    