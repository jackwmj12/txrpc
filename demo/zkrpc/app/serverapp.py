
from txrpc.globalobject import remoteserviceHandle, rootserviceHandle

@rootserviceHandle
def server_test():
    return "this is a response from server"
