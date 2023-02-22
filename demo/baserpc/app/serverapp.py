from loguru import logger

from txrpc2.globalobject import remoteserviceHandle, rootserviceHandle
from txrpc2.server import RPCServer


@rootserviceHandle
def server_test():
    d = RPCServer.callRemote("CLIENT","client_test")
    d.addCallback(logger.debug)
    d.addErrback(logger.error)
    return f"\n{'*'*32}\nthis is a response from server\n{'*'*32}"
