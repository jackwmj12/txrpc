import asyncio

import aiozk
from twisted.internet import defer
from twisted.internet.defer import Deferred, ensureDeferred
from twisted.internet.task import react
import os
from globalobject import remoteserviceHandle
from globalobject import remoteserviceHandle
from utils import Log, asDeferred


@asDeferred
async def zktest():
    zk = aiozk.ZKClient('{}:2181'.format(os.environ.get("TEST_ZK_HOST")))
    await zk.start()
    await zk.ensure_path('/greeting/to')
    await zk.delete('/greeting/to/words')
    await zk.create('/greeting/to/words',"hello")
    data, stat = await zk.get('/greeting/to/words')
    Log.debug(type(data))
    Log.debug(type(stat))
    Log.debug(data)
    # b'hello world' is printed
    # await zk.delete('/greeting/to/words')
    # await zk.close()
    return "this is a response from client"


@remoteserviceHandle("server")
@defer.inlineCallbacks
def client_test():
    ret = yield zktest()
    Log.debug(ret)
    defer.returnValue(ret)