from loguru import logger

from txrpc2.globalobject import remoteServiceHandle, rootServiceHandle, GlobalObject
from txrpc2.server import RPCServer


@rootServiceHandle
def server_test():
    d = GlobalObject().callLeaf("CLIENT","client_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return f"this is a response from server"
