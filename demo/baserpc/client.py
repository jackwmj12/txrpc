import json
import os
import txrpc2
from txrpc2.globalobject import GlobalObject
from loguru import logger
from txrpc2.client import RPCClient

NODE_NAME = "CLIENT"

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

app = RPCClient(name=NODE_NAME).clientConnect()

@app.startServiceHandle
def doWhenStart():
    logger.debug("i am starting")

txrpc2.run()