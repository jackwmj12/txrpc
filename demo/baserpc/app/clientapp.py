from txrpc2.globalobject import remoteServiceHandle, GlobalObject, connectRootHandle, lostConnectRootHandle
from txrpc2.client import RPCClient
from loguru import logger
import os

NODE_NAME = "CLIENT"

def fun():
    d = GlobalObject().callRoot("SERVER", "server_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return d

@remoteServiceHandle("SERVER")
def client_test():
    # from twisted.internet import reactor
    # reactor.callLater(1, fun)
    return f"this is a response from client<{os.getpid()}>"
    