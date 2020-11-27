from twisted.internet import reactor

from globalobject import remoteserviceHandle
from rpc import RPCClient
from utils import Log

def fun():
    d = RPCClient.callRemote("server", "server_test")
    d.addCallback(Log.debug)
    d.addErrback(Log.err)
    return d

@remoteserviceHandle("server")
def client_test():
    reactor.callLater(1, fun)
    return "this is a response from client"
    