import asyncio
import json

from twisted.internet import asyncioreactor

loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

import os

import aiozk
from twisted.internet import defer

from txrpc.globalobject import GlobalObject
from txrpc.utils import asDeferred, logger
from txrpc.server import RPCServer

NODE_NAME = "SERVER"

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

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
    d = GlobalObject().root.callChildByName("CLIENT", "client_test")
    if not d:
        return None
    d.addCallback(logger.debug)
    d.addErrback(logger.err)
    return d

server = RPCServer("SERVER")

@server.childConnectHandle
def doChildConnect(name, transport):
    '''
    :return
    '''
    from twisted.internet import reactor
    logger.debug("{} connected".format(name))
    reactor.callLater(1, fun_)

@server.childLostConnectHandle
def doChildLostConnect(childId):
    '''
    :return
    '''
    logger.debug("{} lost connect".format(childId))
    
from twisted.internet import reactor
reactor.callLater(0.1,fun2_)
server.run()