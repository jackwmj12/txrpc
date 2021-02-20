import asyncio
from twisted.internet import asyncioreactor

loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

import os

import aiozk
from twisted.internet import reactor, defer

from txrpc.globalobject import GlobalObject
from txrpc.utils import asDeferred, logger
from txrpc.server import RPCServer

logger.init()

zk = aiozk.ZKClient('{}:2181'.format(os.environ.get("TEST_ZK_HOST")))

async def data_callback(d):
    logger.debug(d)
    # await asyncio.sleep(0.1)
    # try:
    #     await zk.delete('/greeting/to/words')
    # except Exception as e:
    #     logger.err(e)

@asDeferred
async def create_zk_water():
    await zk.start()
    await zk.ensure_path('/greeting/to')
    # watcher = zk.recipes.DataWatcher()
    # watcher.set_client(zk)
    # watcher.add_callback("/greeting/to/words", data_callback)
    watcher = zk.recipes.ChildrenWatcher()
    watcher.set_client(zk)
    watcher.add_callback("/greeting/to", data_callback)
    return "this is a response from client"

@defer.inlineCallbacks
def fun2_():
    try:
        ret = yield create_zk_water()
        defer.returnValue(ret)
    except Exception as e:
        logger.err(e)
        defer.returnValue(None)

def fun_():
    d = GlobalObject().root.callChildByName("client", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

def doChildConnect(name,transport):
    '''
    :return
    '''
    logger.debug("{} connected".format(name))
    reactor.callLater(1,fun_)
    
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))

server = RPCServer("server",10000)
server.setDoWhenChildConnect(doChildConnect)
server.setDoWhenChildLostConnect(doChildLostConnect)
reactor.callLater(0.1,fun2_)
server.run()