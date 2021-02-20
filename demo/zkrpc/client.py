import asyncio
import json
import os

from twisted.internet import asyncioreactor

loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

from txrpc.client import RPCClient

from txrpc.utils import logger

from txrpc.globalobject import GlobalObject

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

logger.init()

NODE_NAME = "CLIENT"



client = RPCClient(name=NODE_NAME).clientConnect()

client.run()