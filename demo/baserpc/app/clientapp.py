from txrpc2.globalobject import remoteServiceHandle, GlobalObject
from txrpc2.client import RPCClient
from loguru import logger
import os

def fun():
    d = GlobalObject().callRoot("SERVER", "server_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return d

@remoteServiceHandle("SERVER")
def client_test():
    # from twisted.internet import reactor
    # reactor.callLater(1, fun)
    return f"\n{'*'*32}\nthis is a response from client<{os.getpid()}>\n{'*'*32}"
    