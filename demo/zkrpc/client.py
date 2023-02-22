import asyncio
import json
import os

from twisted.internet import asyncioreactor

loop = asyncio.get_event_loop()
asyncioreactor.install(eventloop=loop)

from txrpc2.client import RPCClient

from loguru import logger

from txrpc2.globalobject import GlobalObject

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

NODE_NAME = "CLIENT"

client = RPCClient(name=NODE_NAME).clientConnect()

client.run()