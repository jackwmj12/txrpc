import asyncio

import aiozk
from twisted.internet import defer
from twisted.internet.defer import Deferred, ensureDeferred
from twisted.internet.task import react

from globalobject import remoteserviceHandle
from globalobject import remoteserviceHandle
from utils import Log, asDeferred


@asDeferred
async def zktest():
    print(32*"#")
    zk = aiozk.ZKClient('47.97.222.143:2181')
    await zk.start()
    await zk.ensure_path('/greeting/to')
    await zk.create('/greeting/to/world', 'hello world')
    data, stat = await zk.get('/greeting/to/world')
    Log.debug(type(data))
    Log.debug(type(stat))
    Log.debug(data)
    # b'hello world' is printed
    await zk.delete('/greeting/to/world')
    await zk.close()
    return "this is a response from client"


@remoteserviceHandle("server")
@defer.inlineCallbacks
def client_test():
    ret = yield zktest()
    print(ret)
    defer.returnValue(ret)