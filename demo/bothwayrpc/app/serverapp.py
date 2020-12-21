from twisted.internet import reactor

from globalobject import remoteserviceHandle, rootserviceHandle

@rootserviceHandle
def server_test():
    return "this is a response from server"
