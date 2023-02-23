
from txrpc2.globalobject import remoteServiceHandle, rootServiceHandle

@rootServiceHandle
def server_test():
    return "this is a response from server"
