from twisted.internet import reactor

from globalobject import remoteserviceHandle
from rpc import RPCClient
from utils import logger

def fun():
    d = RPCClient.callRemote("server", "server_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

@remoteserviceHandle("server")
def client_test():
    reactor.callLater(1, fun)
    return "this is a response from client"
    