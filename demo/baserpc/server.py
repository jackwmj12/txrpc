from twisted.internet import reactor

from txrpc.utils import logger

from txrpc.server import RPCServer

logger.init()

def fun():
    d = RPCServer.callRemote("client", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

app = RPCServer("server",10000,service_path="demo.baserpc.app.serverapp")

@app.startServiceHandle
def doWhenStart():
    logger.debug("i am starting")

@app.childConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    logger.debug("{} connected".format(name))
    
    for i in range(1000):
        reactor.callLater(i * 2 + 1, fun)

@app.childLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

# app.setDoWhenChildConnect(doChildConnect)
# app.setDoWhenChildLostConnect(doChildLostConnect)
app.run()