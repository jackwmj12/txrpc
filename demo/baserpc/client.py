import json
import os

from txrpc.globalobject import GlobalObject
from txrpc.utils import logger
from txrpc.client import RPCClient

NODE_NAME = "CLIENT"

with open(os.sep.join([os.path.dirname(os.path.abspath(__file__)),"config.json"])) as f:
    GlobalObject().config = json.load(f)

logger.init()

app = RPCClient(name=NODE_NAME).clientConnect()

@app.startServiceHandle
def doWhenStart():
    logger.debug("i am starting")

app.run()