
from txrpc.globalobject import remoteServiceHandle, rootServiceHandle

@rootserviceHandle
def server_test():
    return "this is a response from server"
